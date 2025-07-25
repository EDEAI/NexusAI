from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.common_utils import get_redis_connection, default_if_empty


class RedisSetAction(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        name = default_if_empty(tool_parameters.get('name'))
        key = default_if_empty(tool_parameters.get('key'))
        value = default_if_empty(tool_parameters.get('value'))
        ttl = int(default_if_empty(tool_parameters.get('ttl'), 60))

        if name and key and value:
            redis_key = name + ':' + key
            conn = get_redis_connection(self.runtime.credentials)
            if -1 == ttl:
                conn.set(name=redis_key, value=value)
            else:
                conn.setex(redis_key, ttl, value)
        yield self.create_text_message(value)
