import secrets
import string
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class RandomStringTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        length = int(tool_parameters.get("length") or 0)
        if not length or length <= 0:
            yield self.create_text_message("")
            return

        include_alphabets = tool_parameters.get("include_alphabets") or "upper_and_lower"
        include_numbers = tool_parameters.get("include_numbers") or "true"
        include_punctuation = tool_parameters.get("include_punctuation") or "false"
        string_count = int(tool_parameters.get("string_count") or 1)
        separator = tool_parameters.get("separator") or ","

        # Determine all available characters
        chars: str = (self.append_alphabets(include_alphabets)
                      + self.append_numbers(include_numbers)
                      + self.append_punctuation(include_punctuation))
        if not chars:
            raise ValueError("No available character included.")

        if include_punctuation == "true" and separator == ",":
            raise ValueError("The seperator cannot be a comma \",\" when punctuation characters are included"
                             " as comma is a punctuation character.")

        # Generate random string(s)
        result_str = separator.join(self.generate_random_string(chars, length) for _ in range(string_count))

        yield self.create_text_message(result_str)

    @staticmethod
    def generate_random_string(characters: str, length: int) -> str:
        return ''.join(secrets.choice(characters) for _ in range(length))

    @staticmethod
    def append_alphabets(include_alphabets: str) -> str:
        match include_alphabets:
            case "upper_and_lower":
                return string.ascii_letters
            case "uppercase_only":
                return string.ascii_uppercase
            case "lowercase_only":
                return string.ascii_lowercase
            case "not_included":
                return ""
            case _:
                return ""

    @staticmethod
    def append_numbers(include_numbers: str) -> str:
        match include_numbers.lower():
            case "true":
                return string.digits
            case _:
                return ""

    @staticmethod
    def append_punctuation(include_punctuation: str) -> str:
        match include_punctuation.lower():
            case "true":
                return string.punctuation
            case _:
                return ""
