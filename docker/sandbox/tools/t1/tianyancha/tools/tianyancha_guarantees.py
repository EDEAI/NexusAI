from collections.abc import Generator
from typing import Any
import requests
from datetime import datetime

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class TianyanchaGuaranteesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Get company external guarantee information
        
        Parameters:
            tool_parameters: Dictionary containing query parameters
                - company_keyword: Company keyword (name or ID)
                - page_size: Number of records per page, default 20
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
        
        # Call API to get external guarantee information
        try:
            result = self._get_company_guarantees(company_keyword, token, page_size, page_num)
            
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
    
    def _get_company_guarantees(self, company_keyword: str, token: str, page_size: int = 20, page_num: int = 1) -> dict:
        """
        API call implementation for getting company external guarantee information
        
        Parameters:
            company_keyword: Company keyword
            token: API credentials
            page_size: Number of records per page
            page_num: Page number
            
        Returns:
            Formatted company external guarantee information
        """
        # Build request
        url = f"http://open.api.tianyancha.com/services/open/stock/guarantees/2.0?keyword={company_keyword}&pageSize={page_size}&pageNum={page_num}"
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
            
        # Extract guarantee information
        guarantees_data = response_data.get("result", {})
        guarantees_list = guarantees_data.get("result", [])
        total = guarantees_data.get("total", 0)
        
        # Build formatted information
        guarantees_info = []
        for item in guarantees_list:
            guarantees_info.append({
                "Announcement Date": self._format_timestamp(item.get("announcement_date")),
                "Guarantor": item.get("grnt_corp_name"),
                "Guaranteed Party": item.get("secured_org_name"),
                "Guarantee Type": item.get("grnt_type"),
                "Guarantee Amount": item.get("grnt_amt"),
                "Currency": item.get("currency_variety"),
                "Guarantee Start Date": self._format_timestamp(item.get("grnt_sd")),
                "Guarantee End Date": self._format_timestamp(item.get("grnt_ed")),
                "Guarantee Period": item.get("grnt_period"),
                "Is Related Transaction": item.get("is_related_trans"),
                "Is Fulfilled": item.get("is_fulfillment")
            })
            
        result = {
            "External Guarantees": {
                "Total Records": total,
                "Current Page": page_num,
                "Page Size": page_size,
                "Guarantee Records": guarantees_info
            }
        }
        
        if not guarantees_info:
            result["External Guarantees"]["Note"] = "No external guarantee information found for this company"
            
        return result