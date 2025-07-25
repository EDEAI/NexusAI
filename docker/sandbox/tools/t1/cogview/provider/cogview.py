"""Provide the input parameters type for the cogview provider class"""

from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.cogview3 import CogView3Tool
from dify_plugin import ToolProvider


class COGVIEWProvider(ToolProvider):
    """cogview provider"""

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for _ in CogView3Tool.from_credentials(credentials).invoke(
                tool_parameters={
                    "prompt": "一个城市在水晶瓶中欢快生活的场景，水彩画风格，展现出微观与珠宝般的美丽。",
                    "size": "square",
                    "n": 1,
                }
            ):
                pass

        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e)) from e
