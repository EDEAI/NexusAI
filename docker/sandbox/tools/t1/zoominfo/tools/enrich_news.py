import requests
import logging
from collections.abc import Generator
from typing import Any
from datetime import datetime
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.config.logger_format import plugin_logger_handler
from utils.session_manager import ZoomInfoSessionManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)


class EnrichNewsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        logger.info("Starting ZoomInfo news enrichment")

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

        company_id = tool_parameters.get("company_id")
        limit = tool_parameters.get("limit")
        page = tool_parameters.get("page")
        date_min = tool_parameters.get("date_min", "").strip()
        date_max = tool_parameters.get("date_max", "").strip()

        logger.info(f"News enrichment request for company ID: {company_id}")
        logger.info(f"Parameters - limit: {limit}, page: {page}, date range: {date_min} to {date_max}")

        if company_id is None:
            logger.error("Company ID parameter is missing")
            raise Exception("Company ID cannot be empty.")

        if limit is None:
            logger.error("Limit parameter is missing")
            raise Exception("Limit cannot be empty.")

        if page is None:
            logger.error("Page parameter is missing")
            raise Exception("Page cannot be empty.")

        if not date_min:
            logger.error("Start date parameter is empty")
            raise Exception("Start date cannot be empty.")

        if not date_max:
            logger.error("End date parameter is empty")
            raise Exception("End date cannot be empty.")

        try:
            company_id = int(company_id)
            if company_id <= 0:
                raise ValueError("Company ID must be positive")
        except (ValueError, TypeError):
            logger.error(f"Invalid company ID: {company_id}")
            raise Exception("Company ID must be a positive integer.")

        try:
            limit = int(limit)
            if limit <= 0:
                raise ValueError("Limit must be positive")
        except (ValueError, TypeError):
            logger.error(f"Invalid limit: {limit}")
            raise Exception("Limit must be a positive integer.")

        try:
            page = int(page)
            if page <= 0:
                raise ValueError("Page must be positive")
        except (ValueError, TypeError):
            logger.error(f"Invalid page: {page}")
            raise Exception("Page must be a positive integer.")

        try:
            datetime.strptime(date_min, '%Y-%m-%d')
            datetime.strptime(date_max, '%Y-%m-%d')
        except ValueError:
            logger.error(f"Invalid date format: {date_min} or {date_max}")
            raise Exception("Dates must be in YYYY-MM-DD format.")

        def make_api_call(token: str) -> requests.Response:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            payload = {
                "companyId": company_id,
                "limit": limit,
                "page": page,
                "pageDateMin": date_min,
                "pageDateMax": date_max
            }

            logger.info(f"Making ZoomInfo API call for news enrichment")
            return requests.post(
                "https://api.zoominfo.com/enrich/news",
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
                logger.warning(f"No news found for company ID {company_id}")
                raise Exception(f"No news found for company ID {company_id}.")
            elif response.status_code != 200:
                logger.error(f"ZoomInfo API error (status {response.status_code}): {response.text[:200]}")
                raise Exception(f"ZoomInfo API error (status {response.status_code}): {response.text}")

            logger.info("Parsing ZoomInfo API response")
            result_data = response.json()

            formatted_result = {
                "company_id": company_id,
                "limit": limit,
                "page": page,
                "date_range": {
                    "start": date_min,
                    "end": date_max
                },
                "data": result_data,
                "status": "success"
            }

            if result_data and isinstance(result_data, dict):
                news_count = len(result_data.get('data', []))
                summary = f"News enrichment completed successfully for company ID {company_id}. Found {news_count} news articles."
                logger.info(
                    f"News enrichment completed successfully for company ID {company_id}, found {news_count} articles")
            else:
                summary = f"News enrichment completed but no news found for company ID {company_id}."
                logger.info(f"News enrichment completed but no news found for company ID {company_id}")

            yield self.create_text_message(summary)
            yield self.create_json_message(formatted_result)

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while querying ZoomInfo: {str(e)}")
            raise Exception(f"Network error while querying ZoomInfo: {str(e)}")
        except Exception as e:
            if "Invalid request" in str(e) or "Unauthorized" in str(e) or "ZoomInfo API error" in str(e):
                raise e
            else:
                logger.error(f"Unexpected error during news enrichment: {str(e)}")
                raise Exception(f"Unexpected error during news enrichment: {str(e)}")
