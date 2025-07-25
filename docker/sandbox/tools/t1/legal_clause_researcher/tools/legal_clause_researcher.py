# File: dify-legal-plugin/tools/legal_clause_identifier.py
# This file contains the core Python logic for the "Legal Clause Identifier" tool,
# integrating with a hypothetical Thomson Reuters Legal API.

from collections.abc import Generator
from typing import Any, Mapping
import requests # For making HTTP requests to the Thomson Reuters API
import json # To pretty print JSON responses for debugging/logging

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class LegalClauseIdentifierTool(Tool):
    """
    A Dify Tool Plugin to identify legal clauses within text
    by integrating with a hypothetical Thomson Reuters Legal API.
    """

    def _invoke(self, tool_parameters: Mapping[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Invokes the Thomson Reuters Legal API for legal clause identification.

        Args:
            tool_parameters (Mapping[str, Any]): A dictionary containing the tool's input parameters.
                Expected keys:
                - "text" (str): The legal text to analyze. (required)
                - "keywords" (list[str], optional): Specific clause types to look for.
                                                   If empty, the API might use its default detection.

        Yields:
            ToolInvokeMessage: A JSON message with identified clauses.
            ToolInvokeMessage: Text messages for progress or errors.
        """
        text = tool_parameters.get("text")
        requested_keywords = tool_parameters.get("keywords") # Optional parameter for API to filter

        if not text:
            yield self.create_text_message("Error: Missing required parameter 'text' for legal analysis.")
            return

        # Retrieve Thomson Reuters API key and endpoint from Dify credentials
        thomsonreuters_api_key = self.runtime.credentials.get("thomsonreuters_api_key")
        thomsonreuters_api_endpoint = self.runtime.credentials.get("thomsonreuters_api_endpoint")

        if not thomsonreuters_api_key:
            yield self.create_text_message("Error: Thomson Reuters API key is not configured. Please set it in plugin credentials.")
            return
        if not thomsonreuters_api_endpoint:
            yield self.create_text_message("Error: Thomson Reuters API endpoint is not configured. Please set it in plugin credentials.")
            return

        yield self.create_text_message("Sending legal text to Thomson Reuters API for analysis...")

        # Construct payload and headers for Thomson Reuters API request
        # This is a hypothetical structure. You MUST adapt this to actual Thomson Reuters API documentation.
        headers = {
            "Authorization": f"Bearer {thomsonreuters_api_key}", # Or 'X-ThomsonReuters-API-Key', etc.
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {
            "document_text": text,
            "analysis_type": "clause_identification", # Hypothetical API parameter
            "preferred_clauses": requested_keywords # Pass optional keywords if provided
        }

        try:
            response = requests.post(thomsonreuters_api_endpoint, headers=headers, json=payload)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            analysis_data = response.json()

            # Parse the (hypothetical) Thomson Reuters API response
            # You MUST adapt this parsing logic to the actual API response structure.
            # Assuming the API returns a dictionary where keys are clause types and values are details.
            identified_clauses = analysis_data.get("identified_clauses", {})
            analysis_summary = analysis_data.get("summary", "Legal analysis performed.")

            if identified_clauses:
                # Reformat for Dify's output schema if necessary
                formatted_clauses = {}
                for clause_type, details in identified_clauses.items():
                    # Assuming details might contain "present" and "matched_phrases"
                    formatted_clauses[clause_type] = {
                        "present": details.get("present", True), # Assume present if found
                        "matched_phrases": details.get("matched_phrases", [])
                    }

                result = {
                    "analysis_summary": analysis_summary,
                    "identified_clauses": formatted_clauses
                }
                yield self.create_json_message({"legal_analysis": result})
                yield self.create_text_message("Legal text analysis complete using Thomson Reuters API.")
            else:
                yield self.create_text_message(
                    "Thomson Reuters API returned no identified legal clauses for the provided text. "
                    "The text might not contain common legal phrases or the API had no matches."
                )

        except requests.exceptions.HTTPError as e:
            yield self.create_text_message(f"Error from Thomson Reuters API: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Network error when connecting to Thomson Reuters API: {e}")
        except KeyError as e:
            yield self.create_text_message(f"Error parsing Thomson Reuters API response. Missing expected key: {e}. Response: {json.dumps(analysis_data, indent=2)}")
        except Exception as e:
            yield self.create_text_message(f"An unexpected error occurred during legal analysis: {e}")
