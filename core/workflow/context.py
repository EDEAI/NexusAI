import re
from typing import Dict, List, Any
from .nodes.base import Node
from .variables import Variable, ArrayVariable, ObjectVariable, VariableTypes, create_variable_from_dict, replace_value_in_variable

class Context:
    """
    Represents the inputs and outputs of all nodes in a workflow.

    Attributes:
        records (List[Dict[str, Any]]): A list of records, each containing the input and output information of a node.
    """

    def __init__(self):
        """
        Initializes a new instance of the Context class.
        """
        self.records: List[Dict[str, Any]] = []

    def add_node(self, level: int, node: Node) -> None:
        """
        Adds the input and output data of a node to the records. If a record with the same
        level and node_id already exists, it updates the existing record.

        Args:
            level (int): The level of the node in the workflow.
            node (Node): The node object.
        """
        for record in self.records:
            if record["level"] == level and record["node_id"] == node.id:
                outputs = node.data.get("output", None)
                record.update({
                    "node_title": node.data["title"],
                    "node_type": node.data["type"],
                    "inputs": node.data.get("input", None),
                    "outputs": outputs
                })
                return
            
        outputs = node.data.get("output", None)
        self.records.append({
            "level": level,
            "node_id": node.id,
            "node_title": node.data["title"],
            "node_type": node.data["type"],
            "inputs": node.data.get("input", None),
            "outputs": outputs
        })

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Context object into a dictionary representation.
        This method ensures that each input and output in the records list is properly converted to a dictionary representation before being included in the output dictionary.
        Returns:
            Dict[str, Any]: A dictionary representing the Context object.
        """
        return [{
            "level": record["level"],
            "node_id": record["node_id"],
            "node_title": record["node_title"],
            "node_type": record["node_type"],
            "inputs": record["inputs"].to_dict() if record["inputs"] else None,
            "outputs": record["outputs"].to_dict() if record["outputs"] else None
        } for record in self.records]
        
    def get_related_records(self, level: int, node_ids: List[str]) -> 'Context':
        """
        Retrieves all records with a level less than or equal to the given level and with node IDs in the given list.

        Args:
            level (int): The current node level.
            node_ids (List[str]): A list of node IDs to filter the records.

        Returns:
            Context: A new Context object containing the filtered records.
        """
        new_context = Context()
        for record in self.records:
            if record["level"] <= level and record["node_id"] in node_ids:
                new_context.records.append(record)
        return new_context

def create_context_from_dict(context_dict: List[Dict[str, Any]]) -> Context:
    """
    Creates a Context object from a list representation.

    Args:
        context_dict (List[Dict[str, Any]]): A list of dictionaries representing the records in the context.

    Returns:
        Context: An instance of the Context class.
    """
    context = Context()
    for record in context_dict:
        context.records.append({
            "level": record["level"],
            "node_id": record["node_id"],
            "node_title": record["node_title"],
            "node_type": record["node_type"],
            "inputs": create_variable_from_dict(record["inputs"]) if record["inputs"] else None,
            "outputs": create_variable_from_dict(record["outputs"]) if record["outputs"] else None
        })
    return context

def replace_variable_value_with_context(original_variable: VariableTypes, context: Context, partial_replacement: bool = False):
    """
    Searches for placeholders in the original variable's value (if it's a Variable type) or in its properties/values
    (if it's an ObjectVariable or ArrayVariable type) and replaces them with actual values from the context based on node IDs and sources and variable names.

    Parameters:
    - original_variable: The variable (of type VariableTypes) containing placeholders to be replaced.
    - context: The context containing variables that may replace the placeholders.
    - partial_replacement: Whether to perform partial replacement (only replace placeholders without changing variable type). Default is False.

    Returns:
    None. The function directly modifies the original_variable's value or its properties/values.
    """
    if isinstance(original_variable, Variable) and isinstance(original_variable.value, str):
        placeholders = re.findall(r'<<([0-9a-fA-F\-]+)\.(inputs|outputs)\.([^>]+)>>', original_variable.value)
        for node_id, source, var_name in placeholders:
            for record in context.records:
                if record['node_id'] == node_id:
                    replace_value_in_variable(original_variable, record[source], node_id, source, var_name, is_prompt=partial_replacement)
                    break
    elif isinstance(original_variable, ArrayVariable):
        for value in original_variable.values:
            replace_variable_value_with_context(value, context, partial_replacement)
    elif isinstance(original_variable, ObjectVariable):
        for value in original_variable.properties.values():
            replace_variable_value_with_context(value, context, partial_replacement)