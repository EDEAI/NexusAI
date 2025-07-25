import requests
import logging
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.config.logger_format import plugin_logger_handler
from utils.session_manager import ZoomInfoSessionManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)


class EnrichContactTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        logger.info("Starting ZoomInfo contact enrichment")

        try:
            username = self.runtime.credentials["zoominfo_username"]
            password = self.runtime.credentials["zoominfo_password"]
            logger.info(f"Initializing ZoomInfo tool for user: {username[:3]}***")
        except KeyError as e:
            missing_key = str(e).strip("'")
            logger.error(f"Missing ZoomInfo credential: {missing_key}")
            raise Exception(
                f"ZoomInfo credential '{missing_key}' is not configured. Please provide it in the plugin settings.")

        session_manager = ZoomInfoSessionManager(username, password, self.session.storage)

        first_name = tool_parameters.get("first_name", "").strip()
        last_name = tool_parameters.get("last_name", "").strip()
        company_name = tool_parameters.get("company_name", "").strip()
        output_fields_str = tool_parameters.get("output_fields", "").strip()

        contact_name = f"{first_name} {last_name}".strip()
        logger.info(f"Contact enrichment request for: {contact_name} at {company_name}")
        logger.info(f"Requested output fields: {output_fields_str}")

        if not first_name:
            logger.error("First name parameter is empty")
            raise Exception("First name cannot be empty.")

        if not last_name:
            logger.error("Last name parameter is empty")
            raise Exception("Last name cannot be empty.")

        if not company_name:
            logger.error("Company name parameter is empty")
            raise Exception("Company name cannot be empty.")

        if not output_fields_str:
            logger.error("Output fields parameter is empty")
            raise Exception("Output fields cannot be empty.")

        try:
            output_fields = [field.strip() for field in output_fields_str.split(",")]
            output_fields = [field for field in output_fields if field]

            if len(output_fields) == 0:
                logger.error("No valid output fields specified")
                raise Exception("At least one output field must be specified.")

            if len(output_fields) > 5:
                logger.error(f"Too many output fields specified: {len(output_fields)}")
                raise Exception("Maximum 5 output fields are allowed.")

            logger.info(f"Parsed output fields: {output_fields}")

        except Exception as e:
            logger.error(f"Error parsing output fields: {e}")
            raise Exception(f"Invalid output fields format: {e}")

        def make_api_call(token: str) -> requests.Response:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            payload = {
                "matchPersonInput": [{
                    "firstName": first_name,
                    "lastName": last_name,
                    "companyName": company_name
                }],
                "outputFields": output_fields
            }

            logger.info("Making ZoomInfo API call for contact enrichment")
            return requests.post(
                "https://api.zoominfo.com/enrich/contact",
                headers=headers,
                json=payload,
                timeout=30
            )

        try:
            token = session_manager.get_valid_token()
            response = make_api_call(token)

            logger.info(f"ZoomInfo API response status: {response.status_code}")

            if 400 <= response.status_code < 500:
                logger.warning(f"Received {response.status_code} response, attempting token refresh")
                token = session_manager.refresh_token()
                response = make_api_call(token)
                logger.info(f"Retry response status: {response.status_code}")

            if response.status_code == 401:
                logger.error("Unauthorized: Invalid or expired token")
                raise Exception("Unauthorized: Invalid or expired token. Please check your credentials.")
            elif response.status_code == 400:
                logger.error(f"Bad request (400): {response.text[:200]}")
                try:
                    error_data = response.json()
                    error_message = error_data.get('message', 'Bad Request')
                    raise Exception(f"Invalid request: {error_message}")
                except:
                    raise Exception(f"Invalid request: {response.text}")
            elif response.status_code == 404:
                logger.warning(f"Contact '{contact_name}' at '{company_name}' not found in ZoomInfo database")
                raise Exception(f"Contact '{contact_name}' at '{company_name}' not found in ZoomInfo database.")
            elif response.status_code != 200:
                logger.error(f"ZoomInfo API error (status {response.status_code}): {response.text[:200]}")
                raise Exception(f"ZoomInfo API error (status {response.status_code}): {response.text}")

            logger.info("Parsing ZoomInfo API response")
            result_data = response.json()

            formatted_result = {
                "contact_name": contact_name,
                "company_name": company_name,
                "requested_fields": output_fields,
                "data": result_data,
                "status": "success"
            }

            if result_data and isinstance(result_data, dict):
                summary = f"Contact enrichment completed successfully for '{contact_name}' at '{company_name}'."
                logger.info(f"Contact enrichment completed successfully for: {contact_name} at {company_name}")
            else:
                summary = f"Contact enrichment completed but no data found for '{contact_name}' at '{company_name}'."
                logger.info(f"Contact enrichment completed but no data found for: {contact_name} at {company_name}")

            yield self.create_text_message(summary)
            yield self.create_json_message(formatted_result)

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while querying ZoomInfo: {str(e)}")
            raise Exception(f"Network error while querying ZoomInfo: {str(e)}")
        except Exception as e:
            if "Invalid request" in str(e) or "Unauthorized" in str(e) or "ZoomInfo API error" in str(e):
                raise e
            else:
                logger.error(f"Unexpected error during contact enrichment: {str(e)}")
                raise Exception(f"Unexpected error during contact enrichment: {str(e)}")
