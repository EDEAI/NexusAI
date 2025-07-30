from typing import Any
import requests

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class BlackForestLabsProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            url = "https://api.bfl.ai/v1/flux-dev"
            payload = {
                "prompt": "ein fantastisches bild",
                "width": 1024,
                "height": 768,
                "steps": 28,
                "prompt_upsampling": False,
                "guidance": 3,
                "safety_tolerance": 2,
                "output_format": "jpeg"
            }
            headers = {
                "x-key": credentials.get("api_key", None),
                "Content-Type": "application/json"
            }
            response = requests.request(
                "POST", url, json=payload, headers=headers
            )
            if response.status_code == 200:
                pass
            else:
                error_info = response.json()
                raise Exception(
                    f"BFL API Message: {error_info}"
                )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
