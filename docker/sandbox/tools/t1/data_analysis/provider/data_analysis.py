"""
apikey校验
"""
from typing import Any
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from utils.digitforce_api import DigitForceApi

class DataAnalysisProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            api_key = credentials.get('digitforce_api_key',"")
            result = DigitForceApi(api_key).dify_api_post({"query":"", "input_data":"", "type":"VerifyApikey"},"PythonDataAnalysis")
            if result != "Check success":
                raise ToolProviderCredentialValidationError("API Key check failed")
        except Exception:
            raise ToolProviderCredentialValidationError(str("API Key check failed"))
