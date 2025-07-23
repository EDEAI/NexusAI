from collections.abc import Generator
from typing import Any
import requests
from datetime import datetime

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class TianyanchaMortgageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Get enterprise movable property mortgage information
        
        Parameters:
            tool_parameters: Dictionary containing query parameters
                - company_keyword: Company keyword (name or ID)
                - page_size: Page size, default 20
                - page_num: Page number, default 1
        """
        # Get parameters
        company_keyword = tool_parameters.get("company_keyword")
        page_size = tool_parameters.get("page_size", 20)
        page_num = tool_parameters.get("page_num", 1)
        
        if not company_keyword:
            error_message = "Company keyword cannot be empty"
            yield self.create_json_message({"error": error_message})
            return
            
        # Get credentials from runtime
        try:
            token = self.runtime.credentials["token"]
        except (KeyError, AttributeError):
            error_message = "API token not configured, please provide a valid Tianyancha API Token in plugin settings"
            yield self.create_json_message({"error": error_message})
            return
        
        # Call API to get movable property mortgage information
        try:
            result = self._get_company_mortgage_info(company_keyword, token, page_size, page_num)
            
            # Return structured JSON data
            yield self.create_json_message(result)
        except Exception as e:
            error_message = f"Error occurred during request: {str(e)}"
            yield self.create_json_message({"error": error_message})
            
    def _format_timestamp(self, timestamp):
        """Format timestamp to readable date"""
        if not timestamp:
            return None
        try:
            # Convert millisecond timestamp to seconds
            if len(str(timestamp)) > 10:
                timestamp = int(timestamp) / 1000
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            return None
    
    def _get_company_mortgage_info(self, company_keyword: str, token: str, page_size: int = 20, page_num: int = 1) -> dict:
        """
        API call implementation for getting enterprise movable property mortgage information
        
        Parameters:
            company_keyword: Company keyword
            token: API credentials
            page_size: Page size
            page_num: Page number
            
        Returns:
            Formatted enterprise movable property mortgage information
        """
        # Build request
        url = f"http://open.api.tianyancha.com/services/open/mr/mortgageInfo/2.0?keyword={company_keyword}&pageSize={page_size}&pageNum={page_num}"
        headers = {'Authorization': token}
        
        # Send request
        response = requests.get(url, headers=headers)
        
        # Check response status
        if response.status_code != 200:
            raise Exception(f"API request failed, status code: {response.status_code}, response: {response.text}")
            
        # Parse JSON response
        response_data = response.json()
        
        # Check API return status
        if response_data.get("error_code") != 0:
            error_msg = response_data.get("reason", "Unknown error")
            raise Exception(f"Query failed: {error_msg}")
            
        # Extract movable property mortgage information
        mortgage_data = response_data.get("result", {})
        items_list = mortgage_data.get("items", [])
        total = mortgage_data.get("total", 0)
        
        # Build formatted information
        mortgage_info = []
        for item in items_list:
            base_info = item.get("baseInfo", {})
            people_info = item.get("peopleInfo", [])
            pawn_info_list = item.get("pawnInfoList", [])
            change_info_list = item.get("changeInfoList", [])
            
            mortgage_entry = {
                "basic_information": {
                    "registration_number": base_info.get("regNum"),
                    "registration_date": base_info.get("regDate"),
                    "registration_department": base_info.get("regDepartment"),
                    "status": base_info.get("status"),
                    "secured_debt_type": base_info.get("type"),
                    "guarantee_amount": base_info.get("amount"),
                    "debt_term": base_info.get("term") or base_info.get("overviewTerm"),
                    "guarantee_scope": base_info.get("scope") or base_info.get("overviewScope"),
                    "cancellation_date": base_info.get("cancelDate"),
                    "cancellation_reason": base_info.get("cancelReason"),
                    "publication_date": self._format_timestamp(base_info.get("publishDate")),
                    "remark": base_info.get("remark") or base_info.get("overviewRemark")
                },
                "creditor_information": [
                    {
                        "name": person.get("peopleName"),
                        "license_type": person.get("liceseType"),
                        "license_number": person.get("licenseNum")
                    } for person in people_info
                ],
                "mortgage_property_information": [
                    {
                        "property_name": pawn.get("pawnName"),
                        "ownership": pawn.get("ownership"),
                        "quantity_and_condition": pawn.get("detail"),
                        "remark": pawn.get("remark")
                    } for pawn in pawn_info_list
                ],
                "change_information": [
                    {
                        "change_date": change.get("changeDate"),
                        "change_content": change.get("changeContent")
                    } for change in change_info_list
                ]
            }
            mortgage_info.append(mortgage_entry)
            
        result = {
            "movable_property_mortgage": {
                "total_records": total,
                "current_page": page_num,
                "page_size": page_size,
                "mortgage_records": mortgage_info
            }
        }
        
        if not mortgage_info:
            result["movable_property_mortgage"]["note"] = "No movable property mortgage information found for this enterprise"
            
        return result