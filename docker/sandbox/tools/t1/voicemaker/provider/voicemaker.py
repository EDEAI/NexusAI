from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.voicemaker import VoicemakerTool


class VoicemakerProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            """
            IMPLEMENT YOUR VALIDATION HERE
            """
            for _ in VoicemakerTool.from_credentials(credentials).invoke(
                tool_parameters={"engine": "neural", "voiceId": "ai3-Jony", "languageCode": "en-US", "text": "Welcome to the Air.",
                                 "outputFormat": "mp3", "sampleRate": "48000", "effect": "default", "masterVolume": "0", "masterSpeed": "0", "masterPitch": "0"},
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
