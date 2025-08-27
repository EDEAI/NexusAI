from collections.abc import Generator
from typing import Any
import logging


from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

# Import the API client
from .pubmed_client import PubMedAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PubMedSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invokes the PubMed search tool.
        ... (rest of the code remains the same) ...
        """
        logger.info(f"Invoking PubMed Search tool with parameters: {tool_parameters}")

        credentials = self.runtime.credentials
        email = credentials.get("email")
        api_key = credentials.get("api_key")

        if not email:
            logger.error("Email credential not found.")
            yield self.create_text_message("Error: PubMed email credential is not configured.")
            return

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

        query = tool_parameters.get("query")
        if not query:
            logger.warning("Search query parameter is missing.")
            yield self.create_text_message("Error: Search query cannot be empty.")
            return

        try:
            max_results = int(tool_parameters.get("max_results", 100))
            sort = tool_parameters.get("sort", "relevance")
            min_date = tool_parameters.get("min_date")
            max_date = tool_parameters.get("max_date")
        except (ValueError, TypeError) as e:
             logger.error(f"Invalid parameter type for max_results: {tool_parameters.get('max_results')}. Error: {e}")
             yield self.create_text_message(f"Error: Invalid value for 'Maximum Results'. It must be a number. Error: {e}")
             return

        if sort not in ["relevance", "pub_date"]:
            logger.warning(f"Invalid sort parameter provided: {sort}. Defaulting to 'relevance'.")
            sort = "relevance"

        try:
            logger.info(f"Calling PubMedAPI search: query='{query}', max_results={max_results}, sort='{sort}', min_date='{min_date}', max_date='{max_date}'")
            id_list = api.search(
                query=query,
                max_results=max_results,
                sort=sort,
                min_date=min_date,
                max_date=max_date
            )
            logger.info(f"PubMed search successful. Returned {len(id_list)} IDs.")

            result_data = {
                "pmids": id_list,
                "count": len(id_list),
                "search_details": {
                    "query": query,
                    "max_results_requested": max_results,
                    "sort_order": sort,
                    "start_date_filter": min_date,
                    "end_date_filter": max_date
                }
            }
            yield self.create_json_message(result_data)
            logger.info("Successfully yielded JSON result.")

        except (ValueError, RuntimeError) as e: # Catch standard exceptions
            logger.error(f"Error during PubMed search: {e}")
            yield self.create_text_message(f"PubMed Search Error: {e}")
        except Exception as e:
            # Handle unexpected errors during the API call or processing
            logger.error(f"Unexpected error during PubMed search execution: {e}", exc_info=True)
            yield self.create_text_message(f"An unexpected error occurred: {e}")