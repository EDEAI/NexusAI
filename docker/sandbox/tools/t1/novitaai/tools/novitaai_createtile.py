from base64 import b64decode
from copy import deepcopy
from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from novita_client import NovitaClient


class NovitaAiCreateTileTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        invoke tools
        """
        if "api_key" not in self.runtime.credentials or not self.runtime.credentials.get("api_key"):
            raise ToolProviderCredentialValidationError("Novita AI API Key is required.")
        api_key = self.runtime.credentials.get("api_key")
        client = NovitaClient(api_key=api_key)
        param = self._process_parameters(tool_parameters)
        client_result = client.create_tile(**param)
        results = []
        results.append(
            self.create_blob_message(
                blob=b64decode(client_result.image_file),
                meta={"mime_type": f"image/{client_result.image_type}"},
                save_as=self.VariableKey.IMAGE.value,
            )
        )
        yield results

    def _process_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """
        process parameters
        """
        res_parameters = deepcopy(parameters)
        keys_to_delete = [k for (k, v) in res_parameters.items() if v is None or v == ""]
        for k in keys_to_delete:
            del res_parameters[k]
        return res_parameters
