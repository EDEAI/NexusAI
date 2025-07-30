import requests
import logging
from typing import Any
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin.config.logger_format import plugin_logger_handler
from utils.session_manager import ZoomInfoSessionManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)


class ZoomInfoProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        logger.info("Starting ZoomInfo credential validation")

        username = credentials.get("zoominfo_username")
        password = credentials.get("zoominfo_password")

        if not username:
            logger.error("ZoomInfo Username is empty")
            raise ToolProviderCredentialValidationError("ZoomInfo Username cannot be empty.")
        if not password:
            logger.error("ZoomInfo Password is empty")
            raise ToolProviderCredentialValidationError("ZoomInfo Password cannot be empty.")

        try:
            logger.info(f"Validating credentials for user: {username[:3]}***")
            logger.info(f"Password length: {len(password)} characters")

            logger.info("Creating temporary session manager for credential validation")

            class MockStorage:
                def get(self, key: str) -> bytes:
                    return None

                def set(self, key: str, val: bytes) -> None:
                    pass

                def delete(self, key: str) -> None:
                    pass

            session_manager = ZoomInfoSessionManager(username, password, MockStorage())

            logger.info("Attempting to get token for credential validation")

            token = session_manager.get_valid_token()

            if not token:
                logger.error("Failed to obtain token from ZoomInfo")
                raise ToolProviderCredentialValidationError(
                    "Failed to obtain token from ZoomInfo. Check your username and password.")

            logger.info(f"Token obtained successfully. Token length: {len(token)} characters")

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            logger.info("Testing token with ZoomInfo API")

            test_payload = {
                "matchCompanyInput": [{"companyName": "Microsoft"}],
                "outputFields": ["id", "name"]
            }

            response = requests.post(
                "https://api.zoominfo.com/enrich/company",
                headers=headers,
                json=test_payload,
                timeout=10
            )

            logger.info(f"API test response status: {response.status_code}")

            if response.status_code == 401:
                logger.error(f"Token validation failed (401 Unauthorized)")
                raise ToolProviderCredentialValidationError(
                    f"Token validation failed (401 Unauthorized). Response: {response.text[:200]}")

            if response.status_code not in [200, 400, 404]:
                logger.error(f"ZoomInfo API validation failed with status {response.status_code}")
                raise ToolProviderCredentialValidationError(
                    f"ZoomInfo API validation failed with status {response.status_code}. Response: {response.text[:200]}")

            logger.info("ZoomInfo credential validation successful!")

        except ToolProviderCredentialValidationError:
            raise
        except requests.exceptions.Timeout as e:
            logger.error(f"ZoomInfo API connection timed out: {str(e)}")
            raise ToolProviderCredentialValidationError(
                f"ZoomInfo API connection timed out. Check your network connection: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Failed to connect to ZoomInfo API: {str(e)}")
            raise ToolProviderCredentialValidationError(
                f"Failed to connect to ZoomInfo API. Check your network connection: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during ZoomInfo API validation: {str(e)}")
            raise ToolProviderCredentialValidationError(f"Network error during ZoomInfo API validation: {str(e)}")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Credential validation error: {error_msg}")
            if any(keyword in error_msg for keyword in
                   ["Invalid ZoomInfo", "Authentication failed", "authentication error"]):
                raise ToolProviderCredentialValidationError(error_msg)
            else:
                raise ToolProviderCredentialValidationError(
                    f"ZoomInfo credential validation failed with unexpected error: {error_msg}")
