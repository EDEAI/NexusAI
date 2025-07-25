from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from upstash_redis import Redis
from upstash_ratelimit import Ratelimit, FixedWindow, SlidingWindow

class UpstashRatelimitTool(Tool):
    def _validate_parameters(self, tool_parameters: dict[str, Any]) -> None:
        if "window type" not in tool_parameters:
            raise ValueError("Missing required parameter 'window type'")
        if "window size" not in tool_parameters:
            raise ValueError("Missing required parameter 'window size'")
        if "max requests" not in tool_parameters:
            raise ValueError("Missing required parameter 'max requests'")
        if "rate limit scope" not in tool_parameters:
            raise ValueError("Missing required parameter 'rate limit scope'")
        if not isinstance(tool_parameters["window size"], int):
            raise ValueError("Parameter 'window size' must be an integer")
        if not isinstance(tool_parameters["max requests"], int):
            raise ValueError("Parameter 'max requests' must be an integer")
        if tool_parameters["window type"] not in ["sliding window", "fixed window"]:
            raise ValueError("Parameter 'window type' must be either 'sliding window' or 'fixed window'")
        
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            self._validate_parameters(tool_parameters)
        except ValueError as e:
            yield self.create_json_message({
                "status": "error",
                "message": str(e)
            })
            return
        

        window_type = tool_parameters["window type"]  # "sliding window" or "fixed window"
        window_size = tool_parameters["window size"]  # Window size in seconds
        max_requests = tool_parameters["max requests"] # Maximum number of requests allowed in the window
        rate_limit_scope = tool_parameters["rate limit scope"]  # "global" or "user"
        rate = tool_parameters.get("rate", 1)

        # Initialize Redis client with credentials
        redis = Redis(
            url=self.runtime.credentials["UPSTASH_REDIS_REST_URL"],
            token=self.runtime.credentials["UPSTASH_REDIS_REST_TOKEN"]
        )

        # Determine rate limit key based on scope
        if rate_limit_scope == "per user":
            user_id = self.runtime.user_id
            if not user_id:
                yield self.create_json_message({
                    "status": "error",
                    "message": "User ID is required for per-user rate limiting but not found."
                })
                return
            identifier = f"user:{user_id}"
        else:
            identifier = "global"

        # Set up the appropriate rate limiting strategy
        if window_type == "sliding window":
            ratelimit = Ratelimit(
                redis=redis,
                limiter=SlidingWindow(max_requests=max_requests, window=window_size),
            )
        elif window_type == "fixed window":
            ratelimit = Ratelimit(
                redis=redis,
                limiter=FixedWindow(max_requests=max_requests, window=window_size),
            )
        else:
            yield self.create_json_message({
                "status": "error",
                "message": f"Unsupported window type '{window_type}'"
            })
            return
        
        # Apply rate limiting
        response = ratelimit.limit(identifier, rate=rate)

        status = "success" if response.allowed else "error"
        message = "Request allowed" if response.allowed else "Rate limit exceeded"

        yield self.create_json_message({
            "status": status,
            "message": message,
            "limit": response.limit,
            "remaining": response.remaining,
            "reset_time": response.reset,
        })

        yield self.create_variable_message("status", status)
        yield self.create_variable_message("message", message)
        yield self.create_variable_message("limit", response.limit)
        yield self.create_variable_message("remaining", response.remaining)
        yield self.create_variable_message("reset_time", response.reset)

