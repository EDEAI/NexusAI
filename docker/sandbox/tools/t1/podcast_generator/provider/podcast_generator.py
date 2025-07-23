from typing import Any
import openai
from yarl import URL
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import ToolProvider


class PodcastGeneratorProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        tts_service = credentials.get("tts_service")
        api_key = credentials.get("api_key")
        base_url = credentials.get("openai_base_url")
        if not tts_service:
            raise ToolProviderCredentialValidationError("TTS service is not specified")
        if not api_key:
            raise ToolProviderCredentialValidationError("API key is missing")
        if base_url:
            base_url = str(URL(base_url) / "v1")
        if tts_service == "openai":
            self._validate_openai_credentials(api_key, base_url)
        else:
            raise ToolProviderCredentialValidationError(f"Unsupported TTS service: {tts_service}")

    def _validate_openai_credentials(self, api_key: str, base_url: str | None) -> None:
        client = openai.OpenAI(api_key=api_key, base_url=base_url)
        try:
            client.models.list()
        except openai.AuthenticationError:
            raise ToolProviderCredentialValidationError("Invalid OpenAI API key")
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"Error validating OpenAI API key: {str(e)}")
