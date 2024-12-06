import sys, re
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))

from typing import Dict, Any
from core.workflow.variables import Variable, replace_value_in_variable
from core.workflow.context import Context

class Prompt:
    """
    Represents a prompt with system, user, and assistant attributes.
    Each attribute's value can include placeholders to be replaced with actual values from a Context object.
    """

    def __init__(self, system: str = "", user: str = "", assistant: str = ""):
        """
        Initializes a Prompt object with system, user, and assistant attributes.

        :param system: str, the system's part of the prompt.
        :param user: str, the user's part of the prompt.
        :param assistant: str, the assistant's part of the prompt.
        """
        self.system = Variable(name="system", type="string", value=system) if system else None
        self.user = Variable(name="user", type="string", value=user) if user else None
        self.assistant = Variable(name="assistant", type="string", value=assistant) if assistant else None
        
    def get_system(self) -> str:
        """
        Returns the system's part of the prompt.

        :return: str, the system's part of the prompt.
        """
        return self.system.value if self.system else ""
    
    def get_user(self) -> str:
        """
        Returns the user's part of the prompt.

        :return: str, the user's part of the prompt.
        """
        return self.user.value if self.user else ""
    
    def get_assistant(self) -> str:
        """
        Returns the assistant's part of the prompt.

        :return: str, the assistant's part of the prompt.
        """
        return self.assistant.value if self.assistant else ""
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Prompt object to a dictionary representation.

        :return: dict, a dictionary representation of the Prompt object.
        """
        return {
            "system": self.system.to_dict() if self.system else None,
            "user": self.user.to_dict() if self.user else None,
            "assistant": self.assistant.to_dict() if self.assistant else None
        }
        
def create_prompt_from_dict(prompt_dict: Dict[str, Any]) -> Prompt:
    """
    Creates a Prompt object from a dictionary representation.

    :param prompt_dict: dict, a dictionary representing a Prompt object.

    :return: Prompt, an instance of the Prompt class.
    """
    return Prompt(
        system=prompt_dict["system"]["value"] if prompt_dict["system"] else "",
        user=prompt_dict["user"]["value"] if prompt_dict["user"] else "",
        assistant=prompt_dict["assistant"]["value"] if prompt_dict["assistant"] else ""
    )

def replace_prompt_with_context(prompt: Prompt, context: Context, duplicate_braces: bool = False):
    """
    Searches for placeholders in the prompt's attributes and replaces them with actual values from the context.

    :param prompt: The Prompt object containing placeholders to be replaced.
    :param context: The Context object containing variables that may replace the placeholders.
    :param duplicate_braces: bool, whether to duplicate braces in variables in the context.
    """
    def replace_in_attribute(original_variable: Variable):
        placeholders = re.findall(r'<<([0-9a-fA-F\-]+)\.(inputs|outputs)\.([^>]+)>>', original_variable.value)
        for node_id, source, var_name in placeholders:
            for record in context.records:
                if record['node_id'] == node_id:
                    replace_value_in_variable(original_variable, record[source], node_id, source, var_name, duplicate_braces, False)
                    break

    if prompt.system:
        replace_in_attribute(prompt.system)
    if prompt.user:
        replace_in_attribute(prompt.user)
    if prompt.assistant:
        replace_in_attribute(prompt.assistant)