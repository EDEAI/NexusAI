from typing import Any, Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
from twilio.rest import Client


class TwilioAPIWrapper:
    """Messaging Client using Twilio.

    To use, you should have the ``twilio`` python package installed,
    and the environment variables ``TWILIO_ACCOUNT_SID``, ``TWILIO_AUTH_TOKEN``, and
    ``TWILIO_FROM_NUMBER``, or pass `account_sid`, `auth_token`, and `from_number` as
    named parameters to the constructor.
    """

    client: Client = None
    from_number: str = None

    def run(self, body: str, to: str) -> str:
        """Run body through Twilio and respond with message sid.

        Args:
            body: The text of the message you want to send. Can be up to 1,600
                characters in length.
            to: The destination phone number in
                [E.164](https://www.twilio.com/docs/glossary/what-e164) format for
                SMS/MMS or
                [Channel user address](https://www.twilio.com/docs/sms/channels#channel-addresses)
                for other 3rd-party channels.
        """
        message = self.client.messages.create(to, from_=self.from_number, body=body)
        return message.sid

    def check(self, sid: str) -> str:
        pass


class SendMessageTool(Tool):
    """
    A tool for sending messages using Twilio API.

    Args:
        user_id (str): The ID of the user invoking the tool.
        tool_parameters (Dict[str, Any]): The parameters required for sending the message.

    Returns:
        Union[ToolInvokeMessage, List[ToolInvokeMessage]]: The result of invoking the tool,
         which includes the status of the message sending operation.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        account_sid = self.runtime.credentials["account_sid"]
        auth_token = self.runtime.credentials["auth_token"]
        from_number = self.runtime.credentials["from_number"]
        message = tool_parameters["message"]
        to_number = tool_parameters["to_number"]
        if to_number.startswith("whatsapp:"):
            from_number = f"whatsapp: {from_number}"
        twilio = TwilioAPIWrapper()
        twilio.client = Client(account_sid, auth_token)
        twilio.from_number = from_number
        twilio.run(message, to_number)
        yield self.create_text_message(text="Message sent successfully.")
