from collections.abc import Generator
from typing import Any
import requests
from datetime import datetime

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class TianyanchaBusinessInfoTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Get company business information
        
        Parameters:
            tool_parameters: Dictionary containing query parameters
                - company_keyword: Company keyword (name or ID)
        """
        # Get parameters
        company_keyword = tool_parameters.get("company_keyword")
        
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
        
        # Call API to get business information
        try:
            result = self._get_company_business_info(company_keyword, token)
            
            # Return structured JSON data only
            yield self.create_json_message(result)
        except Exception as e:
            error_message = f"Error occurred during request: {str(e)}"
            yield self.create_json_message({"error": error_message})
        
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
            
    def _get_company_business_info(self, company_keyword: str, token: str) -> dict:
        """
        API call implementation for getting company business information
        
        Parameters:
            company_keyword: Company keyword
            token: API credentials
            
        Returns:
            Formatted company business information
        """
        # Build request
        url = f"http://open.api.tianyancha.com/services/open/cb/ic/2.0?keyword={company_keyword}"
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
            
        # Extract business information
        business_data = response_data.get("result", {})
        
        # Build formatted information
        result = {"Business Information": {}}
        
        # Basic information section
        basic_info = {
            "Company Name": business_data.get("name"),
            "Registered Capital": business_data.get("regCapital"),
            "Paid-in Capital": business_data.get("actualCapital"),
            "Establishment Date": self._format_timestamp(business_data.get("estiblishTime")),
            "Unified Social Credit Code": business_data.get("creditCode"),
            "Business Registration Number": business_data.get("regNumber"),
            "Company Type": business_data.get("companyOrgType"),
            "Business Status": business_data.get("regStatus"),
            "Legal Representative": business_data.get("legalPersonName"),
            "Registered Address": business_data.get("regLocation"),
            "Registration Authority": business_data.get("regInstitute"),
            "Business Scope": business_data.get("businessScope")
        }
        result["Business Information"]["Basic Information"] = basic_info
        
        # Key personnel
        staff_list = business_data.get("staffList", [])
        if staff_list:
            staff_info = []
            for staff in staff_list:
                staff_info.append({
                    "Name": staff.get("name"),
                    "Position": staff.get("staffTypeName"),
                    "Other Positions": staff.get("typeJoin", [])
                })
            result["Business Information"]["Key Personnel"] = staff_info
        
        # Shareholder information
        shareholder_list = business_data.get("shareHolderList", [])
        if shareholder_list:
            shareholder_info = []
            for shareholder in shareholder_list:
                capital_info = []
                for capital in shareholder.get("capital", []):
                    capital_info.append({
                        "Investment Amount": capital.get("amomon"),
                        "Investment Ratio": capital.get("percent"),
                        "Investment Method": capital.get("paymet"),
                        "Investment Time": capital.get("time")
                    })
                
                shareholder_info.append({
                    "Shareholder Name": shareholder.get("name"),
                    "Shareholder Type": "Individual" if shareholder.get("type") == 2 else "Enterprise",
                    "Capital Information": capital_info
                })
            result["Business Information"]["Shareholder Information"] = shareholder_info
        
        # External investments
        invest_list = business_data.get("investList", [])
        if invest_list:
            investment_info = []
            for invest in invest_list[:10]:  # Only take first 10 investments to avoid too much data
                investment_info.append({
                    "Invested Company Name": invest.get("name"),
                    "Invested Company Alias": invest.get("alias"),
                    "Investment Ratio": invest.get("percent"),
                    "Investment Amount": invest.get("amount"),
                    "Registered Capital": invest.get("regCapital"),
                    "Business Status": invest.get("regStatus"),
                    "Establishment Date": self._format_timestamp(invest.get("estiblishTime")),
                    "Industry": invest.get("category")
                })
            result["Business Information"]["External Investments"] = investment_info
            
            # If more than 10 investment companies, add note
            if len(invest_list) > 10:
                result["Business Information"]["External Investments Note"] = f"The company has a total of {len(invest_list)} external investment companies, only showing the first 10"
        
        # Branches
        branch_list = business_data.get("branchList", [])
        if branch_list:
            branch_info = []
            for branch in branch_list[:10]:  # Only take first 10 branches to avoid too much data
                branch_info.append({
                    "Branch Name": branch.get("name"),
                    "Branch Alias": branch.get("alias"),
                    "Registration Status": branch.get("regStatus"),
                    "Establishment Date": self._format_timestamp(branch.get("estiblishTime")),
                    "Person in Charge": branch.get("legalPersonName")
                })
            result["Business Information"]["Branches"] = branch_info
            
            # If more than 10 branches, add note
            if len(branch_list) > 10:
                result["Business Information"]["Branches Note"] = f"The company has a total of {len(branch_list)} branches, only showing the first 10"
        
        # Change records
        change_list = business_data.get("changeList", [])
        if change_list:
            change_info = []
            for change in change_list[:10]:  # Only take first 10 change records to avoid too much data
                change_info.append({
                    "Change Item": change.get("changeItem"),
                    "Change Time": change.get("changeTime"),
                    "Content Before": change.get("contentBefore"),
                    "Content After": change.get("contentAfter")
                })
            result["Business Information"]["Change Records"] = change_info
            
            # If more than 10 change records, add note
            if len(change_list) > 10:
                result["Business Information"]["Change Records Note"] = f"The company has a total of {len(change_list)} change records, only showing the first 10"
            
        return result