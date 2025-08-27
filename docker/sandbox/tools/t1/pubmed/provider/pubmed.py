# dify-plugin-pubmed/provider/pubmed.py
from typing import Any
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

# We need a minimal way to test credentials. Import the client.
# Assuming pubmed_client.py is in the tools directory
from tools.pubmed_client import PubMedAPI
from Bio import Entrez # Need Entrez for the validation call directly

class PubMedProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        email = credentials.get("email")
        api_key = credentials.get("api_key")

        if not email:
            raise ToolProviderCredentialValidationError("Email address is required.")

        # Configure Entrez directly for validation
        Entrez.email = email
        Entrez.tool = "DifyPubMedPluginValidation"
        if api_key:
            Entrez.api_key = api_key
        else:
            if hasattr(Entrez, 'api_key'):
                delattr(Entrez, 'api_key')

        try:
            handle = Entrez.esearch(
                db="pubmed",
                term="covid-19",
                retmax="1"
            )
            Entrez.read(handle)
            handle.close()

        except Exception as e:
            error_str = str(e)
            error_message = "PubMed credentials validation failed."
            
            if "API key invalid" in error_str:
                error_message = "Invalid NCBI API Key. Please check if it is correct."
            elif "Invalid e-mail address" in error_str:
                error_message = "Invalid email address format. Please enter a valid email address."
            elif "HTTP Error 400" in error_str:
                error_message = "Request parameters error. Please ensure the email address and API Key format are correct."
            elif "HTTP Error 429" in error_str:
                error_message = "Request rate limit exceeded. Please try again later or add an API Key to increase the limit."
            elif "HTTP Error" in error_str:
                error_message = f"Network request error ({error_str}). Please check your network connection or try again later."
            else:
                error_message = f"{error_message} Error details: {error_str}"

            raise ToolProviderCredentialValidationError(error_message)
        finally:
            # Clean up Entrez settings if necessary, although it's generally set globally per session
            pass

# Note: We don't instantiate the full PubMedAPI client here for validation
# to keep it lightweight and avoid circular dependencies if the client
# itself were defined in this file. A direct, minimal Entrez call is sufficient.