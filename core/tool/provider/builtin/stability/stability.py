from core.tool.provider.builtin_tool_provider import BuiltinTool
from core.tool.provider.builtin.stability.tool.base import BaseAuthorization

class StabilityToolProvider(BuiltinTool, BaseAuthorization):
    """
    This class is responsible for providing the stability tool.
    """

    def __init__(self, credentials: dict):
        """
        Initializes the StabilityToolProvider with the given credentials.

        :param credentials: A dictionary containing the credentials required for authorization.
        """
        super().__init__(credentials)

    def validate(self) -> bool:
        """
        Validates the credentials to ensure they are correct and authorized.

        :return: Returns True if the credentials are valid, otherwise raises an exception.
        """
        self.sd_validate_credentials(self.credentials)
        return True