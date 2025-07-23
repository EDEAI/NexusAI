import json
import requests
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class AnspireBrowserAgentTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        _api_key = self.runtime.credentials.get("api_key")

        task_id = tool_parameters.get("task_id")

        if not _api_key:
            error_message = "API key is required for this operation"
            print(f"[DEBUG] Error: {error_message}")
            yield self.create_json_message(
                {"status": "error", "message": error_message}
            )
            return

        print(
            f"[DEBUG] Validating Browser Agent API key: {_api_key[:4]}...{_api_key[-4:]}"
        )

        if not task_id:
            error_message = "Instance Id description is required"
            print(f"[DEBUG] Error: {error_message}")
            yield self.create_json_message(
                {"status": "error", "message": error_message}
            )
            return

        try:
            _endpoint = "https://plugin.anspire.cn/api/brower/action_stop"
            headers = {
                "Authorization": f"Bearer {_api_key}",
                "Content-Type": "application/json",
            }

            _body_data = dict(
                task_id=task_id,
            )

            print(f"[DEBUG] Sending request to {_endpoint}")
            print(f"[DEBUG] Request body: {_body_data}")

            response = requests.post(
                _endpoint, headers=headers, data=json.dumps(_body_data)
            )

            print(f"[DEBUG] Run Task response status code: {response.status_code}")
            print(f"[DEBUG] Run Task response content: {response.text}")

            if response.status_code == 200:
                try:
                    result = response.json()

                    print(f"[DEBUG] Task stop successfully. Task ID: {task_id}")

                    # Create response data with original JSON structure
                    response_data = {
                        "status": "success",
                        "message": f"Task stoped successfully. Task ID: {task_id}",
                        "data": result,
                    }

                    # Return the JSON response with full details
                    yield self.create_json_message(response_data)

                except Exception as e:
                    print(
                        f"[DEBUG] Could not parse response as JSON: {response.text}, Error: {str(e)}"
                    )
                    yield self.create_json_message(
                        {
                            "status": "error",
                            "message": f"Could not parse response: {str(e)}",
                            "raw_response": response.text,
                        }
                    )
            else:
                error_message = (
                    f"Task creation failed with status code: {response.status_code}"
                )
                print(f"[DEBUG] {error_message}")

                try:
                    error_data = response.json()
                    print(f"[DEBUG] Error response: {error_message}")
                    yield self.create_json_message(
                        {
                            "status": "error",
                            "message": error_message,
                            "error": error_data,
                        }
                    )
                except Exception:
                    print(
                        f"[DEBUG] Could not parse error response as JSON: {response.text}"
                    )
                    yield self.create_json_message(
                        {
                            "status": "error",
                            "message": error_message,
                            "error": response.text,
                        }
                    )

        except requests.RequestException as e:
            error_message = f"Failed to connect to Browser Agent API: {str(e)}"
            print(f"[DEBUG] {error_message}")
            yield self.create_json_message(
                {"status": "error", "message": error_message}
            )
        except Exception as e:
            error_message = f"Unexpected error stop task: {str(e)}"
            print(f"[DEBUG] {error_message}")
            yield self.create_json_message(
                {"status": "error", "message": error_message}
            )
