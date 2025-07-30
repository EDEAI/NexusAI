from collections.abc import Generator
from typing import Any
import requests
from datetime import datetime

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class TianyanchaIllegalInfoTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Get enterprise serious violation information
        
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
        
        # Call API to get serious violation information
        try:
            result = self._get_company_illegal_info(company_keyword, token, page_size, page_num)
            
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
    
    def _get_company_illegal_info(self, company_keyword: str, token: str, page_size: int = 20, page_num: int = 1) -> dict:
        """
        API call implementation for getting enterprise serious violation information
        
        Parameters:
            company_keyword: Company keyword
            token: API credentials
            page_size: Page size
            page_num: Page number
            
        Returns:
            Formatted enterprise serious violation information
        """
        # Build request
        url = f"http://open.api.tianyancha.com/services/open/mr/illegalinfo/2.0?keyword={company_keyword}&pageSize={page_size}&pageNum={page_num}"
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
            
        # Extract serious violation information
        illegal_data = response_data.get("result", {})
        items_list = illegal_data.get("items", [])
        total = illegal_data.get("total", 0)
        
        # Build formatted information
        illegal_info = []
        for item in items_list:
            illegal_entry = {
                "inclusion_reason": item.get("putReason"),
                "inclusion_date": self._format_timestamp(item.get("putDate")),
                "inclusion_department": item.get("putDepartment"),
                "removal_reason": item.get("removeReason") or "Not removed yet",
                "removal_date": self._format_timestamp(item.get("removeDate")) or "Not removed yet",
                "removal_department": item.get("removeDepartment") or "Not removed yet"
            }
            illegal_info.append(illegal_entry)
            
        result = {
            "serious_violations": {
                "total_records": total,
                "current_page": page_num,
                "page_size": page_size,
                "violation_records": illegal_info
            }
        }
        
        if not illegal_info:
            result["serious_violations"]["note"] = "No serious violation information found for this enterprise"
            
        return result