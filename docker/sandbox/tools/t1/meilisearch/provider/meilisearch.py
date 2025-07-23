from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from typing import Any

import requests

class MeilisearchDifyPluginProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            response = requests.get(
                credentials["base_url"],
                headers={"Authorization": f"Bearer {credentials['meilisearch_api_key']}"}
            )
            
            # Check if the request was successful;
            if response.status_code != 200:
                raise ToolProviderCredentialValidationError(
                    f"Meilisearch API returned status code: {response.status_code}"
                )
            
            # For self-hosted Meilisearch: Check JSON response;
            try:
                json_response = response.json()
                if json_response.get("status") == "Meilisearch is running":
                    return
            except ValueError:
                # For Meilisearch Cloud: It returns HTML instead of JSON;
                # If the response contains HTML and has 200 status, consider it valid;
                if "<!doctype html>" in response.text.lower() and "meilisearch" in response.text.lower():
                    return
                
            # If we got here without returning, validation failed;
            raise ToolProviderCredentialValidationError(
                "Unable to validate Meilisearch credentials. Invalid response format."
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
