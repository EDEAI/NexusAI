from typing import Any
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import ToolProvider


class TwilioProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            account_sid = credentials["account_sid"]
            auth_token = credentials["auth_token"]
            client = Client(account_sid, auth_token)
            client.api.accounts(account_sid).fetch()
        except TwilioRestException as e:
            raise ToolProviderCredentialValidationError(
                f"Twilio API error: {e.msg}"
            ) from e
        except KeyError as e:
            raise ToolProviderCredentialValidationError(
                f"Missing required credential: {e}"
            ) from e
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e)) from e
