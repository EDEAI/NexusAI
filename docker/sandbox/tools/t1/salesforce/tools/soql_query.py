import requests
import logging
import urllib.parse
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.config.logger_format import plugin_logger_handler
from utils.session_manager import SalesforceSessionManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)


class SoqlQueryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        logger.info("Starting Salesforce SOQL query execution")

        try:
            login_url = self.runtime.credentials["salesforce_login_url"]
            username = self.runtime.credentials["salesforce_username"]
            password_with_token = self.runtime.credentials["salesforce_password_with_security_token"]
            logger.info(f"Initializing Salesforce tool for user: {username[:3]}***")
        except KeyError as e:
            missing_key = str(e).strip("'")
            logger.error(f"Missing Salesforce credential: {missing_key}")
            raise Exception(
                f"Salesforce credential '{missing_key}' is not configured. Please provide it in the plugin settings.")

        session_manager = SalesforceSessionManager(username, password_with_token, login_url, self.session.storage)

        soql_query = tool_parameters.get("soql_query", "").strip()
        logger.info(f"SOQL query to execute: {soql_query[:100]}{'...' if len(soql_query) > 100 else ''}")

        if not soql_query:
            logger.error("SOQL query is empty")
            raise Exception("SOQL query cannot be empty.")

        if not soql_query.upper().startswith("SELECT"):
            logger.error(f"Invalid SOQL query syntax: {soql_query[:50]}")
            raise Exception("Invalid SOQL query. Query must start with SELECT.")

        def make_api_call(session_id: str, instance_url: str) -> requests.Response:
            headers = {
                "Authorization": f"Bearer {session_id}",
                "Content-Type": "application/json"
            }

            encoded_query = urllib.parse.quote(soql_query)
            url = f"{instance_url}/services/data/v63.0/query?q={encoded_query}"
            logger.info(f"Making Salesforce API call to: {instance_url}/services/data/v63.0/query")
            return requests.get(url, headers=headers, timeout=30)

        try:
            session_id, instance_url = session_manager.get_valid_session()
            logger.info("Executing SOQL query with Salesforce API")
            response = make_api_call(session_id, instance_url)

            logger.info(f"Salesforce API response status: {response.status_code}")

            if 400 <= response.status_code < 500:
                logger.warning(f"Received {response.status_code} response, attempting session refresh")
                session_id, instance_url = session_manager.refresh_session()
                response = make_api_call(session_id, instance_url)
                logger.info(f"Retry response status: {response.status_code}")

            if response.status_code == 401:
                logger.error("Unauthorized: Invalid or expired session")
                raise Exception("Unauthorized: Invalid or expired session. Please check your credentials.")
            elif response.status_code == 400:
                logger.error(f"Bad request (400): {response.text[:200]}")
                try:
                    error_data = response.json()
                    error_message = error_data.get('message', 'Bad Request')
                    raise Exception(f"Invalid SOQL query: {error_message}")
                except:
                    raise Exception(f"Invalid SOQL query: {response.text}")
            elif response.status_code != 200:
                logger.error(f"Salesforce API error (status {response.status_code}): {response.text[:200]}")
                raise Exception(f"Salesforce API error (status {response.status_code}): {response.text}")

            logger.info("Parsing Salesforce API response")
            result_data = response.json()

            formatted_result = {
                "totalSize": result_data.get("totalSize", 0),
                "done": result_data.get("done", True),
                "records": result_data.get("records", []),
                "query": soql_query
            }

            if formatted_result["totalSize"] > 0:
                summary = f"Query executed successfully. Found {formatted_result['totalSize']} record(s)."
                logger.info(f"SOQL query completed successfully, found {formatted_result['totalSize']} records")
            else:
                summary = "Query executed successfully. No records found."
                logger.info("SOQL query completed successfully, no records found")

            yield self.create_text_message(summary)
            yield self.create_json_message(formatted_result)

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while querying Salesforce: {str(e)}")
            raise Exception(f"Network error while querying Salesforce: {str(e)}")
        except Exception as e:
            if "Invalid SOQL query" in str(e) or "Unauthorized" in str(e) or "Salesforce API error" in str(e):
                raise e
            else:
                logger.error(f"Unexpected error during SOQL query execution: {str(e)}")
                raise Exception(f"Unexpected error during SOQL query execution: {str(e)}")
