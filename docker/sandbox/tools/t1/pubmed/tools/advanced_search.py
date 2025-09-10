from collections.abc import Generator
from typing import Any, Dict
import logging

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

# Import the API client
from .pubmed_client import PubMedAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PubMedAdvancedSearchTool(Tool):
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invokes the PubMed advanced_search tool.

        Args:
            tool_parameters (dict): Parameters provided by the user or LLM.
                Expected keys correspond to fields in advanced_search.yaml.

        Yields:
            ToolInvokeMessage: Messages containing results (JSON) or errors (TEXT).
        """
        logger.info(f"Invoking PubMed Advanced Search tool with parameters: {tool_parameters}")

        # 1. Get Credentials
        credentials = self.runtime.credentials
        email = credentials.get("email")
        api_key = credentials.get("api_key")

        if not email:
            logger.error("Email credential not found.")
            yield self.create_text_message("Error: PubMed email credential is not configured.")
            return

        # 2. Instantiate API Client
        try:
            api = PubMedAPI(email=email, api_key=api_key)
            logger.info("PubMedAPI client instantiated successfully.")
        except ValueError as e: # Catch init errors
            logger.error(f"Failed to instantiate PubMedAPI client: {e}")
            yield self.create_text_message(f"Error initializing PubMed client: {e}")
            return
        except Exception as e:
            logger.error(f"Unexpected error instantiating PubMedAPI client: {e}", exc_info=True)
            yield self.create_text_message(f"Unexpected error initializing PubMed client: {e}")
            return

        # 3. Prepare parameters for the API client method
        # The tool_parameters dict should directly match what api.advanced_search expects
        search_params = tool_parameters.copy() # Avoid modifying original dict

        # Optional: Basic validation (e.g., ensure at least one field is present)
        search_fields = ['author', 'title', 'journal', 'abstract_keywords', 'mesh_terms', 'keywords', 'general_query']
        if not any(search_params.get(field) for field in search_fields):
             yield self.create_text_message("Error: Advanced search requires at least one search term in a specific field or a general query.")
             return

        # Validate max_results if provided
        try:
            if "max_results" in search_params and search_params["max_results"] is not None:
                 search_params["max_results"] = int(search_params["max_results"])
            else:
                 search_params["max_results"] = 100 # Ensure default if not present or None
        except (ValueError, TypeError):
             logger.warning(f"Invalid max_results value: {search_params.get('max_results')}. Using default 100.")
             search_params["max_results"] = 100


        # 4. Call API Method
        try:
            logger.info(f"Calling PubMedAPI advanced_search with params: {search_params}")
            id_list = api.advanced_search(params=search_params)
            logger.info(f"PubMed advanced_search successful. Returned {len(id_list)} IDs.")

            # 5. Format and Yield Result
            result_data = {
                "pmids": id_list,
                "count": len(id_list),
                "search_details": { # Include search parameters for context
                    "search_parameters": tool_parameters # Echo back the input params
                }
            }
            yield self.create_json_message(result_data)
            logger.info("Successfully yielded JSON result for advanced_search.")

        except (ValueError, RuntimeError) as e: # Catch errors from client or processing
            logger.error(f"Error during PubMed advanced_search: {e}")
            yield self.create_text_message(f"PubMed Advanced Search Error: {e}")
        except Exception as e:
            # Handle unexpected errors during the API call or processing
            logger.error(f"Unexpected error during PubMed advanced_search execution: {e}", exc_info=True)
            yield self.create_text_message(f"An unexpected error occurred: {e}")