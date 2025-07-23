from collections.abc import Generator
from typing import Any
import requests
from datetime import datetime

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class TianyanchaPublicNoticeTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Get enterprise bill public notice information
        
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
        
        # Call API to get public notice information
        try:
            result = self._get_company_public_notice(company_keyword, token, page_size, page_num)
            
            # Return structured JSON data
            yield self.create_json_message(result)
        except Exception as e:
            error_message = f"Error occurred during request: {str(e)}"
            yield self.create_json_message({"error": error_message})
    
    def _get_company_public_notice(self, company_keyword: str, token: str, page_size: int = 20, page_num: int = 1) -> dict:
        """
        API call implementation for getting enterprise bill public notice information
        
        Parameters:
            company_keyword: Company keyword
            token: API credentials
            page_size: Page size
            page_num: Page number
            
        Returns:
            Formatted enterprise bill public notice information
        """
        # Build request
        url = f"http://open.api.tianyancha.com/services/v4/open/publicNotice?keyword={company_keyword}&pageSize={page_size}&pageNum={page_num}"
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
            
        # Extract public notice information
        notice_data = response_data.get("result", {})
        items_list = notice_data.get("items", [])
        total = notice_data.get("total", 0)
        
        # Build formatted information
        notice_info = []
        for item in items_list:
            notice_entry = {
                "bill_type": item.get("billType"),
                "bill_number": item.get("billNum"),
                "bill_amount": item.get("billAmt"),
                "bill_start_date": item.get("billBeginDt"),
                "bill_end_date": item.get("billEndDt") or "Not disclosed",
                "urgent_type": item.get("exigentType"),
                "publish_date": item.get("publishDt"),
                "publish_organization": item.get("publishOrgName"),
                "drawer_company_name": item.get("drawCompanyName"),
                "drawer_company_id": item.get("drawCompanyId"),
                "holder_company_name": item.get("ownerCompanyName"),
                "holder_company_id": item.get("ownerCompanyId"),
                "applicant_company_name": item.get("applyCompanyName"),
                "applicant_company_id": item.get("applyCompanyId"),
                "payment_bank": item.get("payCompanyName"),
                "detailed_notice_content": item.get("infoDetail")
            }
            notice_info.append(notice_entry)
            
        result = {
            "public_notice": {
                "total_records": total,
                "current_page": page_num,
                "page_size": page_size,
                "notice_records": notice_info
            }
        }
        
        if not notice_info:
            result["public_notice"]["note"] = "No bill public notice information found for this enterprise"
            
        return result