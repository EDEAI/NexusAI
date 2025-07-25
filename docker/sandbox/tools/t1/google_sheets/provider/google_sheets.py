from typing import Any
import json
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class GoogleSheetsProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # Verify required fields exist in credentials
            if 'credentials_json' not in credentials:
                raise ValueError("Missing required field: credentials_json")
            
            # Parse the credentials JSON
            creds_json = json.loads(credentials['credentials_json'])
            
            # Create credentials object to validate format
            creds = service_account.Credentials.from_service_account_info(
                creds_json,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            # Verify we can build the service (further validation)
            build('sheets', 'v4', credentials=creds)
        except json.JSONDecodeError:
            raise ToolProviderCredentialValidationError("Invalid JSON format for credentials_json")
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
    
    def get_credentials(self) -> service_account.Credentials:
        """Helper method to get credentials for tools"""
        credentials = self._runtime.credentials
        creds_json = json.loads(credentials['credentials_json'])
        return service_account.Credentials.from_service_account_info(
            creds_json,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
