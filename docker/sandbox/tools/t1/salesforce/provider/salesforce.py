import requests
import logging
from typing import Any
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin.config.logger_format import plugin_logger_handler
from utils.session_manager import SalesforceSessionManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)


class SalesforceProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        logger.info("Starting Salesforce credential validation")

        login_url = credentials.get("salesforce_login_url")
        username = credentials.get("salesforce_username")
        password_with_token = credentials.get("salesforce_password_with_security_token")

        if not login_url:
            logger.error("Salesforce Login URL is empty")
            raise ToolProviderCredentialValidationError("Salesforce Login URL cannot be empty.")
        if not username:
            logger.error("Salesforce Username is empty")
            raise ToolProviderCredentialValidationError("Salesforce Username cannot be empty.")
        if not password_with_token:
            logger.error("Salesforce Password + Security Token is empty")
            raise ToolProviderCredentialValidationError("Salesforce Password + Security Token cannot be empty.")

        login_url = login_url.strip().rstrip('/')
        if not login_url.startswith(('http://', 'https://')):
            logger.error(f"Invalid login URL format: {login_url}")
            raise ToolProviderCredentialValidationError("Salesforce Login URL must start with http:// or https://")

        try:
            logger.info(f"Validating credentials for user: {username[:3]}***")
            logger.info(f"Login URL: {login_url}")
            logger.info(f"Password length: {len(password_with_token)} characters")

            logger.info("Creating temporary session manager for credential validation")

            class MockStorage:
                def get(self, key: str) -> bytes:
                    return None

                def set(self, key: str, val: bytes) -> None:
                    pass

                def delete(self, key: str) -> None:
                    pass

            session_manager = SalesforceSessionManager(username, password_with_token, login_url, MockStorage())

            logger.info("Attempting to get session for credential validation")

            session_id, instance_url = session_manager.get_valid_session()

            if not session_id or not instance_url:
                logger.error("Failed to obtain session from Salesforce")
                raise ToolProviderCredentialValidationError(
                    "Failed to obtain session from Salesforce. Check your username, password, and security token.")

            logger.info(f"Session obtained successfully. Instance URL: {instance_url}")
            logger.info(f"Session ID length: {len(session_id)} characters")

            headers = {
                "Authorization": f"Bearer {session_id}",
                "Content-Type": "application/json"
            }

            logger.info("Testing session with Salesforce API")

            response = requests.get(
                f"{instance_url}/services/data/v63.0/limits",
                headers=headers,
                timeout=10
            )

            logger.info(f"API test response status: {response.status_code}")

            if response.status_code == 401:
                logger.error(f"Session validation failed (401 Unauthorized)")
                raise ToolProviderCredentialValidationError(
                    f"Session validation failed (401 Unauthorized). Response: {response.text[:200]}")

            if response.status_code not in [200, 400, 404]:
                logger.error(f"Salesforce API validation failed with status {response.status_code}")
                raise ToolProviderCredentialValidationError(
                    f"Salesforce API validation failed with status {response.status_code}. Response: {response.text[:200]}")

            logger.info("Salesforce credential validation successful!")

        except ToolProviderCredentialValidationError:
            raise
        except requests.exceptions.Timeout as e:
            logger.error(f"Salesforce API connection timed out: {str(e)}")
            raise ToolProviderCredentialValidationError(
                f"Salesforce API connection timed out. Check your network connection: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Failed to connect to Salesforce API: {str(e)}")
            raise ToolProviderCredentialValidationError(
                f"Failed to connect to Salesforce API. Check your login URL and network: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during Salesforce API validation: {str(e)}")
            raise ToolProviderCredentialValidationError(f"Network error during Salesforce API validation: {str(e)}")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Credential validation error: {error_msg}")
            if any(keyword in error_msg for keyword in
                   ["Invalid Salesforce", "login failed", "SOAP fault", "authentication error"]):
                raise ToolProviderCredentialValidationError(error_msg)
            else:
                raise ToolProviderCredentialValidationError(
                    f"Salesforce credential validation failed with unexpected error: {error_msg}")
