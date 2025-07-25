from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from openai import AzureOpenAI, OpenAI

class Gpt4oOcrPdfProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # Get common credentials
            api_key = str(credentials.get("api_key", "").strip())
            api_type = str(credentials.get("api_type", "azure").strip().lower())
            
            # Check if API key is provided
            if not api_key:
                raise ToolProviderCredentialValidationError("API key is required")
            
            # Validate based on API type
            if api_type == "azure":
                # Get Azure-specific credentials
                deployment_name = str(credentials.get("deployment_name", "").strip())
                api_endpoint = str(credentials.get("api_endpoint", "").strip())
                api_version = str(credentials.get("api_version", "").strip())
                
                # Validate Azure-specific credentials
                if not deployment_name:
                    raise ToolProviderCredentialValidationError("Azure Deployment name is required")
                if not api_endpoint:
                    raise ToolProviderCredentialValidationError("Azure API endpoint is required")
                if not api_version:
                    raise ToolProviderCredentialValidationError("Azure API version is required")
                
                # Create Azure OpenAI client to validate credentials
                client = AzureOpenAI(
                    api_version=api_version,
                    azure_endpoint=api_endpoint,
                    api_key=api_key,
                )
                
                # Simple validation by checking if client is created
                if not client:
                    raise Exception("Invalid Azure OpenAI credentials")
            else:  # OpenAI
                # Create OpenAI client to validate credentials
                client = OpenAI(
                    api_key=api_key
                )
                
                # Simple validation by checking if client is created
                if not client:
                    raise Exception("Invalid OpenAI credentials")
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
