from typing import Generator, Union
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class DeleteCardByIdTool(Tool):
    """
    Tool for deleting a Trello card by its ID.
    """

    def _invoke(
        self, tool_parameters: dict[str, Union[str, int, bool]]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invoke the tool to delete a Trello card by its ID.

        Args:
            user_id (str): The ID of the user invoking the tool.
            tool_parameters (dict[str, Union[str, int, bool]]): The parameters for the tool invocation,
             including the card ID.

        Returns:
            ToolInvokeMessage: The result of the tool invocation.
        """
        api_key = self.runtime.credentials.get("trello_api_key")
        token = self.runtime.credentials.get("trello_api_token")
        card_id = tool_parameters.get("id")
        if not (api_key and token and card_id):
            yield self.create_text_message(
                "Missing required parameters: API key, token, or card ID."
            )
            return
        url = f"https://api.trello.com/1/cards/{card_id}?key={api_key}&token={token}"
        try:
            response = requests.delete(url)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            yield self.create_text_message("Failed to delete card")
            return
        yield self.create_text_message(
            text=f"Card with ID {card_id} has been successfully deleted."
        )
