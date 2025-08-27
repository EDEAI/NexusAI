from collections.abc import Generator
from typing import Any, List
import logging
import re

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

# Import the API client
from .pubmed_client import PubMedAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PubMedFetchDetailsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invokes the PubMed fetch_details tool.

        Args:
            tool_parameters (dict): Parameters provided by the user or LLM.
                Expected keys: 'pmids'.

        Yields:
            ToolInvokeMessage: Messages containing results (JSON) or errors (TEXT).
        """
        logger.info(f"Invoking PubMed Fetch Details tool with parameters: {tool_parameters}")

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

        # 3. Get and Process Tool Parameters
        pmids_str = tool_parameters.get("pmids")
        if not pmids_str or not isinstance(pmids_str, str):
            logger.warning("PMIDs parameter is missing or not a string.")
            yield self.create_text_message("Error: PubMed IDs (pmids) parameter is required as a comma-separated string.")
            return

        # Split string into list and clean up IDs
        try:
             # Split by comma, remove whitespace, filter empty strings, keep only digits
            id_list = [id_val for id_val in (re.sub(r'\s+', '', pmid) for pmid in pmids_str.split(',')) if id_val.isdigit()]
            if not id_list:
                 raise ValueError("No valid PubMed IDs found after processing the input string.")
            logger.info(f"Processed PMIDs for fetching: {id_list}")
        except Exception as e:
            logger.error(f"Failed to process PMIDs string '{pmids_str}': {e}", exc_info=True)
            yield self.create_text_message(f"Error processing PubMed IDs input. Please provide a comma-separated list of valid IDs. Details: {e}")
            return


        # 4. Call API Method
        try:
            logger.info(f"Calling PubMedAPI fetch_details for {len(id_list)} IDs.")
            articles_details = api.fetch_details(id_list=id_list)
            logger.info(f"PubMed fetch_details successful. Returned details for {len(articles_details)} articles.")

            # 5. Format and Yield Result
            result_data = {
                "articles": articles_details,
                "count": len(articles_details),
                "requested_pmids_count": len(id_list), # Add count requested for comparison
            }
            yield self.create_json_message(result_data)
            logger.info("Successfully yielded JSON result for fetch_details.")

        except (ValueError, RuntimeError) as e: # Catch errors from client or processing
            logger.error(f"Error during PubMed fetch_details: {e}")
            yield self.create_text_message(f"PubMed Fetch Details Error: {e}")
        except Exception as e:
            # Handle unexpected errors during the API call or processing
            logger.error(f"Unexpected error during PubMed fetch_details execution: {e}", exc_info=True)
            yield self.create_text_message(f"An unexpected error occurred: {e}")