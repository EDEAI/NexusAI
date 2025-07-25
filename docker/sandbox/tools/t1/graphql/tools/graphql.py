import json
from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class GraphQLTool(Tool):
    def _invoke(
        self,
        tool_parameters: dict[str, Any],
    ) -> Generator[ToolInvokeMessage]:
        """
        Invokes the GraphQL tool to send a request to a specified endpoint.
        """
        endpoint: str = tool_parameters.get("endpoint")
        method: str = tool_parameters.get("method", "POST").upper()
        query: str = tool_parameters.get("query", "")
        variables_str: str = tool_parameters.get(
            "variables", "{}"
        )  # Default to empty JSON object string
        headers_str: str = tool_parameters.get(
            "headers", "{}"
        )  # Default to empty JSON object string
        operation_name: str = tool_parameters.get("operation_name", None)

        if not endpoint:
            yield self.create_text_message("GraphQL endpoint is required.")
            return

        # consider introspection request
        # if not query:
        #     yield self.create_text_message("GraphQL query is required.")
        #     return

        try:
            # Ensure empty string or whitespace-only string becomes empty dict
            variables = (
                json.loads(variables_str)
                if variables_str and variables_str.strip()
                else {}
            )
        except json.JSONDecodeError:
            yield self.create_text_message(
                f"Invalid JSON format for variables: {variables_str}"
            )
            return

        try:
            # Ensure empty string or whitespace-only string becomes empty dict
            headers = (
                json.loads(headers_str) if headers_str and headers_str.strip() else {}
            )
        except json.JSONDecodeError:
            yield self.create_text_message(
                f"Invalid JSON format for headers: {headers_str}"
            )
            return

        if not isinstance(headers, dict):
            yield self.create_text_message("Headers must be a JSON object.")
            return

        # Ensure Content-Type is set for JSON payload, but allow override
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        payload = {"query": query}
        if variables:  # Only add variables to payload if they are not empty
            payload["variables"] = variables
        if operation_name:
            payload["operationName"] = operation_name

        try:
            if method == "GET":
                # For GET requests, add query parameters to the URL
                response = requests.get(endpoint, params=payload, headers=headers)
            else:
                # For POST requests, send the payload as JSON
                response = requests.post(endpoint, json=payload, headers=headers)

            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

            try:
                response_data = response.json()
                if isinstance(response_data, dict):
                    yield self.create_json_message(response_data)
                elif isinstance(response_data, list):
                    yield self.create_json_message({"data": response_data})

            except json.JSONDecodeError:  # If response is not JSON, return as text
                yield self.create_text_message(response.text)

        except requests.exceptions.HTTPError as e:
            error_message = f"HTTP error sending GraphQL request: {e}."
            # Try to append response details to the error message
            if e.response is not None:
                try:
                    error_details = e.response.json()
                    error_message += f" Details: {json.dumps(error_details)}"
                except json.JSONDecodeError:
                    error_message += f" Details: {e.response.text}"
            yield self.create_text_message(error_message)
        except (
            requests.exceptions.RequestException
        ) as e:  # For network errors, timeouts, etc.
            yield self.create_text_message(f"Error sending GraphQL request: {e}")
        except Exception as e:  # Catch any other unexpected errors
            yield self.create_text_message(f"An unexpected error occurred: {e}")
