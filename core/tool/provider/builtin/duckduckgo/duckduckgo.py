from core.tool.provider.builtin_tool_provider import BuiltinTool

class DuckDuckGoProvider(BuiltinTool):
    def __init__(self, credentials: dict):
        """
        Initialize the DuckDuckGoProvider with the given credentials.

        :param credentials: A dictionary containing authentication credentials.
        """
        super().__init__(credentials)

    def validate(self) -> bool:
        """
        Validate the credentials.

        :return: True if the credentials are valid, False otherwise.
        """
        return True