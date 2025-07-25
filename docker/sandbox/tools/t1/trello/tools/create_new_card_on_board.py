from typing import Generator, Union
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class CreateNewCardOnBoardTool(Tool):
    """
    Tool for creating a new card on a Trello board.
    """

    def _invoke(
        self, tool_parameters: dict[str, Union[str, int, bool, None]]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invoke the tool to create a new card on a Trello board.

        Args:
            user_id (str): The ID of the user invoking the tool.
            tool_parameters (dict[str, Union[str, int, bool, None]]): The parameters for the tool invocation,
             including details for the new card.

        Returns:
            ToolInvokeMessage: The result of the tool invocation.
        """
        api_key = self.runtime.credentials.get("trello_api_key")
        token = self.runtime.credentials.get("trello_api_token")
        if "name" not in tool_parameters or "idList" not in tool_parameters:
            yield self.create_text_message(
                "Missing required parameters: name or idList."
            )
            return
        url = "https://api.trello.com/1/cards"
        params = {**tool_parameters, "key": api_key, "token": token}
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            new_card = response.json()
        except requests.exceptions.RequestException:
            yield self.create_text_message("Failed to create card")
            return
        yield self.create_text_message(
            text=f"New card '{new_card['name']}' created successfully with ID {new_card['id']}."
        )
