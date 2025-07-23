from typing import Generator, Union
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class GetListsFromBoardTool(Tool):
    """
    Tool for retrieving all lists from a specified Trello board by its ID.
    """

    def _invoke(
        self, tool_parameters: dict[str, Union[str, int, bool]]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invoke the tool to get all lists from a specified Trello board.

        Args:
            user_id (str): The ID of the user invoking the tool.
            tool_parameters (dict[str, Union[str, int, bool]]): The parameters for the tool invocation,
             including the board ID.

        Returns:
            ToolInvokeMessage: The result of the tool invocation.
        """
        api_key = self.runtime.credentials.get("trello_api_key")
        token = self.runtime.credentials.get("trello_api_token")
        board_id = tool_parameters.get("boardId")
        if not (api_key and token and board_id):
            yield self.create_text_message(
                "Missing required parameters: API key, token, or board ID."
            )
            return
        url = f"https://api.trello.com/1/boards/{board_id}/lists?key={api_key}&token={token}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            lists = response.json()
        except requests.exceptions.RequestException:
            yield self.create_text_message("Failed to retrieve lists")
            return
        lists_info = "\n".join([f"{list['name']} (ID: {list['id']})" for list in lists])
        yield self.create_text_message(
            text=f"Lists on Board ID {board_id}:\n{lists_info}"
        )
