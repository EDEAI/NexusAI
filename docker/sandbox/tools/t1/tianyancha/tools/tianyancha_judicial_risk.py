from collections.abc import Generator
from typing import Any
import requests
from datetime import datetime

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class TianyanchaJudicialRiskTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Get enterprise judicial risk information
        
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
        
        # Call API to get judicial risk information
        try:
            result = self._get_company_judicial_risk(company_keyword, token)
            
            # Return only structured JSON data
            yield self.create_json_message(result)
        except Exception as e:
            error_message = f"Error occurred during request: {str(e)}"
            yield self.create_json_message({"error": error_message})
        
    def _get_company_judicial_risk(self, company_keyword: str, token: str) -> dict:
        """
        API call implementation for getting enterprise judicial risk information
        
        Parameters:
            company_keyword: Company keyword
            token: API credentials
            
        Returns:
            Formatted enterprise judicial risk information
        """
        # Build request
        url = f"http://open.api.tianyancha.com/services/open/cb/judicial/2.0?keyword={company_keyword}"
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
            
        # Extract judicial risk information
        judicial_data = response_data.get("result", {})
        
        # Build formatted information
        result = {"judicial_risk": {}}
        
        # Legal lawsuits
        lawsuit_list = judicial_data.get("lawSuitList", [])
        if lawsuit_list:
            result["judicial_risk"]["legal_lawsuits"] = [self._format_lawsuit(item) for item in lawsuit_list]
        
        # Court hearing announcements
        kt_announcement_list = judicial_data.get("ktAnnouncementList", [])
        if kt_announcement_list:
            result["judicial_risk"]["court_hearing_announcements"] = [self._format_kt_announcement(item) for item in kt_announcement_list]
        
        # Executed persons
        zhixing_list = judicial_data.get("zhixingList", [])
        if zhixing_list:
            result["judicial_risk"]["executed_persons"] = [self._format_zhixing(item) for item in zhixing_list]
        
        # Court announcements
        court_announcement_list = judicial_data.get("courtAnnouncementList", [])
        if court_announcement_list:
            result["judicial_risk"]["court_announcements"] = [self._format_court_announcement(item) for item in court_announcement_list]
        
        # Case filing information
        court_register_list = judicial_data.get("courtRegisterList", [])
        if court_register_list:
            result["judicial_risk"]["case_filing_information"] = [self._format_court_register(item) for item in court_register_list]
        
        # Service announcements
        send_announcement_list = judicial_data.get("sendAnnouncementList", [])
        if send_announcement_list:
            result["judicial_risk"]["service_announcements"] = [self._format_send_announcement(item) for item in send_announcement_list]
        
        # Dishonest persons
        dishonest_list = judicial_data.get("dishonestList", [])
        if dishonest_list:
            result["judicial_risk"]["dishonest_persons"] = [self._format_dishonest(item) for item in dishonest_list]
        
        # If no judicial risk data
        if not result["judicial_risk"]:
            result["judicial_risk"] = "No judicial risk information found for this enterprise"
            
        return result
    
    def _format_lawsuit(self, item: dict) -> dict:
        """Format legal lawsuit information"""
        return {
            "case_number": item.get("caseno"),
            "case_title": item.get("title"),
            "case_reason": item.get("casereason"),
            "case_type": item.get("casetype"),
            "court": item.get("court"),
            "document_type": item.get("doctype"),
            "submit_time": item.get("submittime"),
            "judgment_time": item.get("judgetime"),
            "plaintiffs": item.get("plaintiffs"),
            "defendants": item.get("defendants"),
            "lawsuit_url": item.get("lawsuitUrl")
        }
        
    def _format_kt_announcement(self, item: dict) -> dict:
        """Format court hearing announcement information"""
        return {
            "case_number": item.get("caseNo"),
            "case_reason": item.get("caseReason"),
            "court": item.get("court"),
            "hearing_date": item.get("startDate"),
            "courtroom": item.get("courtroom"),
            "litigants": item.get("litigant")
        }
    
    def _format_zhixing(self, item: dict) -> dict:
        """Format executed person information"""
        return {
            "case_code": item.get("caseCode"),
            "execution_court": item.get("execCourtName"),
            "case_filing_time": item.get("caseCreateTime"),
            "execution_amount": item.get("execMoney")
        }
    
    def _format_court_announcement(self, item: dict) -> dict:
        """Format court announcement information"""
        return {
            "case_number": item.get("caseno"),
            "party_1": item.get("party1"),
            "party_2": item.get("party2"),
            "case_reason": item.get("reason"),
            "court": item.get("courtcode"),
            "announcement_type": item.get("bltntypename"),
            "publish_date": item.get("publishdate"),
            "content_summary": item.get("content")[:100] + "..." if len(item.get("content", "")) > 100 else item.get("content")
        }
    
    def _format_court_register(self, item: dict) -> dict:
        """Format case filing information"""
        return {
            "case_number": item.get("caseNo"),
            "filing_date": item.get("filingDate"),
            "court": item.get("court"),
            "plaintiff": item.get("plaintiff"),
            "defendant": item.get("defendant"),
            "case_reason": item.get("caseReason") or "Not disclosed"
        }
    
    def _format_send_announcement(self, item: dict) -> dict:
        """Format service announcement information"""
        return {
            "title": item.get("title"),
            "court": item.get("court"),
            "announcement_date": item.get("startDate"),
            "content_summary": item.get("content")[:100] + "..." if len(item.get("content", "")) > 100 else item.get("content")
        }
    
    def _format_dishonest(self, item: dict) -> dict:
        """Format dishonest person information"""
        return {
            "case_code": item.get("casecode"),
            "dishonest_person_name": item.get("iname"),
            "execution_court": item.get("courtname"),
            "area": item.get("areaname"),
            "filing_date": item.get("regdate"),
            "publish_date": item.get("publishdate"),
            "dishonest_behavior": item.get("disrupttypename"),
            "performance_status": item.get("performance"),
            "obligations": item.get("duty")
        }