from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from sympy import randprime


class RandomPrimeTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        lower_bound = tool_parameters.get("lower_bound")
        upper_bound = tool_parameters.get("upper_bound")

        if not lower_bound:
            raise ValueError("Invalid input lower_bound")
        if not upper_bound:
            raise ValueError("Invalid input upper_bound")

        lower_num = int(lower_bound)
        upper_num = int(upper_bound)
        if lower_num > upper_num:
            raise ValueError(f"Invalid range [{lower_bound}, {upper_bound}],"
                             f" the lower bound should be less than or equal to the upper bound")

        random_prime = None
        try:
            # add 1 to the upper bound,
            # as `randprime` generates prime number from [a, b) range
            random_prime = randprime(lower_num, upper_num + 1)
        except ValueError:
            pass

        # NaN represents no prime number found according to IEEE_754 standard
        random_prime_str = str(random_prime) if random_prime else 'NaN'
        yield self.create_text_message(random_prime_str)
