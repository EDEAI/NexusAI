"""Google Sheets service helper functions."""

from typing import Any
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_sheets_service(credentials_json: Any) -> Any:
    """Create and return a Google Sheets API service object.
    
    Args:
        credentials_json: The OAuth2 credentials JSON data
        
    Returns:
        A Google Sheets API service object
    """
    # Create credentials object from the JSON data
    credentials = Credentials.from_service_account_info(credentials_json)
    # Create and return the service
    return build('sheets', 'v4', credentials=credentials)


def handle_google_api_error(error: Exception) -> str:
    """Format Google API errors into readable messages.
    
    Args:
        error: The exception raised during API call
        
    Returns:
        A formatted error message
    """
    if isinstance(error, HttpError):
        status_code = error.resp.status
        reason = error.resp.reason
        
        if status_code == 404:
            return "Spreadsheet not found. Check the spreadsheet ID and make sure it's shared with the service account."
        elif status_code == 403:
            return "Permission denied. Make sure the service account has access to the spreadsheet."
        elif status_code == 400:
            return f"Invalid request: {reason}. Check your parameters and try again."
        else:
            return f"Google API error: {status_code} {reason}"
    
    return f"An unexpected error occurred: {str(error)}" 