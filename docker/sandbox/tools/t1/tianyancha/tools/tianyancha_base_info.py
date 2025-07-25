from collections.abc import Generator
from typing import Any
import requests
from datetime import datetime

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class TianyanchaBaseInfoTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Get company basic information
        
        Parameters:
            tool_parameters: Dictionary containing query parameters
                - company_keyword: Company keyword (name or ID)
        """
        # Get parameters
        company_keyword = tool_parameters.get("company_keyword")
        
        if not company_keyword:
            error_message = "Company keyword cannot be empty"
            yield self.create_json_message({"error": error_message})
            yield self.create_text_message(error_message)
            return
            
        # Get credentials from runtime
        try:
            token = self.runtime.credentials["token"]
        except (KeyError, AttributeError):
            error_message = "API token not configured, please provide a valid Tianyancha API Token in plugin settings"
            yield self.create_json_message({"error": error_message})
            yield self.create_text_message(error_message)
            return
        
        # Call API to get basic information
        try:
            result = self._get_company_base_info(company_keyword, token)
            text_result = self._generate_base_info_text(result)
            
            # Return structured JSON data
            yield self.create_json_message(result)
            # Return readable text format
            yield self.create_text_message(text_result)
        except Exception as e:
            error_message = f"Error occurred during request: {str(e)}"
            yield self.create_json_message({"error": error_message})
            yield self.create_text_message(error_message)
            
    def _format_timestamp(self, timestamp):
        """Format timestamp to readable date"""
        if not timestamp:
            return "Unknown"
        try:
            # Convert millisecond timestamp to seconds
            if len(str(timestamp)) > 10:
                timestamp = int(timestamp) / 1000
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            return str(timestamp)
    
    def _generate_base_info_text(self, data: dict) -> str:
        """Generate readable text for company basic information"""
        basic_info = data.get("Basic Information", {})
        reg_info = data.get("Registration Information", {})
        tags = data.get("Company Tags", [])
        
        text = f"# Basic Information of {basic_info.get('Company Name', 'Unknown Company')}\n\n"
        
        text += "## Basic Information\n"
        for key, value in basic_info.items():
            if value and key != "Industry Details":  # Exclude industry details as it may be complex structure
                text += f"- **{key}**: {value}\n"
        
        text += "\n## Registration Information\n"
        for key, value in reg_info.items():
            if value:
                text += f"- **{key}**: {value}\n"
        
        if tags:
            text += "\n## Company Tags\n"
            text += "- " + ", ".join(tags) + "\n"
        
        return text
    
    def _get_company_base_info(self, company_keyword: str, token: str) -> dict:
        """
        API call implementation for getting company basic information
        
        Parameters:
            company_keyword: Company keyword
            token: API credentials
            
        Returns:
            Formatted company basic information
        """
        # Build request
        url = f"http://open.api.tianyancha.com/services/open/ic/baseinfo/normal?keyword={company_keyword}"
        headers = {'Authorization': token}
        
        # Send request
        response = requests.get(url, headers=headers)
        
        # Check response status
        if response.status_code != 200:
            raise Exception(f"API request failed, status code: {response.status_code}, response: {response.text}")
            
        # Parse JSON response
        response_data = response.json()
        
        # Check API return status
        if response_data.get("error_code") != 0 or not response_data.get("result"):
            error_msg = response_data.get("reason", "Unknown error")
            raise Exception(f"Query failed: {error_msg}")
            
        # Extract company basic information fields
        company_data = response_data.get("result", {})
        
        # Build formatted information
        return {
            "Basic Information": {
                "Company Name": company_data.get("name"),
                "English Name": company_data.get("property3"),
                "Company Alias": company_data.get("alias"),
                "Legal Representative": company_data.get("legalPersonName"),
                "Company Type": company_data.get("companyOrgType"),
                "Registered Capital": f"{company_data.get('regCapital')}",
                "Paid-in Capital": f"{company_data.get('actualCapital')}",
                "Establishment Date": self._format_timestamp(company_data.get("estiblishTime")),
                "Business Status": company_data.get("regStatus"),
                "Unified Social Credit Code": company_data.get("creditCode"),
                "Business Registration Number": company_data.get("regNumber"),
                "Organization Code": company_data.get("orgNumber"),
                "Taxpayer Identification Number": company_data.get("taxNumber"),
                "Industry": company_data.get("industry"),
                "Industry Details": company_data.get("industryAll", {})
            },
            "Registration Information": {
                "Registration Authority": company_data.get("regInstitute"),
                "Registered Address": company_data.get("regLocation"),
                "Business Scope": company_data.get("businessScope"),
                "Business Term": f"{self._format_timestamp(company_data.get('fromTime'))} to {self._format_timestamp(company_data.get('toTime'))}"
            },
            "Company Tags": company_data.get("tags", "").split(";") if company_data.get("tags") else []
        }