from typing import Any, Generator
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class GoogleTranslate(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        invoke tools
        """
        content = tool_parameters.get("content", "")
        if not content:
            yield self.create_text_message("Invalid parameter content")
        dest = tool_parameters.get("dest", "")
        if not dest:
            yield self.create_text_message("Invalid parameter destination language")
        try:
            result = self._translate(content, dest)
            yield self.create_text_message(str(result))
        except Exception:
            yield self.create_text_message("Translation service error, please check the network")

    def _translate(self, content: str, dest: str) -> str:
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {"client": "gtx", "sl": "auto", "tl": dest, "dt": "t", "q": content}
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response_json = requests.get(url, params=params, headers=headers).json()
            result = response_json[0]
            translated_text = "".join([item[0] for item in result if item[0]])
            return str(translated_text)
        except Exception as e:
            return str(e)
