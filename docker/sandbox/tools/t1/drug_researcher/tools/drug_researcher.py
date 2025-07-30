# File: dify-drug-plugin/tools/drug_researcher.py
# This file contains the core Python logic for the "Medical Drug Researcher" tool,
# integrating with a hypothetical DrugBank API.

from collections.abc import Generator
from typing import Any, Mapping
import requests # For making HTTP requests to the DrugBank API

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class DrugResearcherTool(Tool):
    """
    A Dify Tool Plugin to research medical drug information (usage and side effects)
    by integrating with a hypothetical DrugBank API.
    """

    def _invoke(self, tool_parameters: Mapping[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Invokes the DrugBank API to retrieve drug information.

        Args:
            tool_parameters (Mapping[str, Any]): A dictionary containing the tool's input parameters.
                Expected keys:
                - "drug_name" (str): The name of the drug to research. (required)

        Yields:
            ToolInvokeMessage: A JSON message containing the drug information.
            ToolInvokeMessage: Text messages for progress or errors.
        """
        drug_name = tool_parameters.get("drug_name")

        if not drug_name:
            yield self.create_text_message("Error: Missing required parameter 'drug_name'.")
            return

        # Retrieve DrugBank API key and endpoint from Dify credentials
        drugbank_api_key = self.runtime.credentials.get("drugbank_api_key")
        drugbank_api_endpoint = self.runtime.credentials.get("drugbank_api_endpoint")

        if not drugbank_api_key:
            yield self.create_text_message("Error: DrugBank API key is not configured. Please set it in plugin credentials.")
            return
        if not drugbank_api_endpoint:
            yield self.create_text_message("Error: DrugBank API endpoint is not configured. Please set it in plugin credentials.")
            return

        yield self.create_text_message(f"Searching DrugBank for information on {drug_name.title()}...")

        # Construct payload and headers for DrugBank API request
        # This is a hypothetical structure based on common API designs.
        # You MUST adjust this according to actual DrugBank API documentation.
        headers = {
            "Authorization": f"Bearer {drugbank_api_key}", # Or 'X-API-Key', 'Basic Auth', etc.
            "Content-Type": "application/json"
        }
        # Assuming DrugBank has an endpoint like /drugs/search or /drugs/{name}
        # And expects the drug name as a query parameter or part of the URL path
        request_url = f"{drugbank_api_endpoint}/drugs/{drug_name.lower().replace(' ', '%20')}" # Example path parameter
        # Or if it's a query parameter:
        # request_url = f"{drugbank_api_endpoint}/search?query={drug_name.lower()}"

        try:
            response = requests.get(request_url, headers=headers)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            drug_data = response.json()

            # Parse the (hypothetical) DrugBank API response
            # You MUST adapt this parsing logic to the actual DrugBank API response structure.
            usage = drug_data.get("usage", "N/A")
            side_effects = drug_data.get("side_effects", []) # Expecting a list of strings
            if isinstance(side_effects, str): # Handle case where API might return a single string
                side_effects = [side_effects]

            # Check if meaningful data was found
            if usage != "N/A" or side_effects:
                result = {
                    "drug_name": drug_name.title(),
                    "usage": usage,
                    "side_effects": side_effects
                }
                yield self.create_json_message({"drug_details": result})
                yield self.create_text_message(f"Information found for {drug_name.title()} from DrugBank.")
            else:
                yield self.create_text_message(
                    f"No detailed information found for '{drug_name.title()}' from DrugBank. "
                    "Please check the drug name or consult DrugBank's documentation."
                )

        except requests.exceptions.HTTPError as e:
            yield self.create_text_message(f"Error from DrugBank API: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Network error when connecting to DrugBank API: {e}")
        except KeyError as e:
            yield self.create_text_message(f"Error parsing DrugBank API response. Missing expected key: {e}. Please check the API response format.")
        except Exception as e:
            yield self.create_text_message(f"An unexpected error occurred during DrugBank research: {e}")

