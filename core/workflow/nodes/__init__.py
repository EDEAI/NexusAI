import sys
from pprint import pp
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent.parent.parent))

from typing import Dict, Any, List
from .base import CURRENT_NODE_ID, UPLOAD_FILES_KEY, Node, Nodes, LLMBaseNode, SandboxBaseNode
from .start import StartNode
from .human import HumanNode
from .agent import AgentNode
from .retriever import RetrieverNode
from .memory_interrupt import MemoryInterruptNode
from .llm import LLMNode
from .requirement_category import RequirementCategory, create_requirement_category_from_dict, RequirementCategoryNode
from .condition_branch import LogicCondition, LogicBranch, LogicBranches, create_logic_branches_from_dict, ConditionBranchNode
from .http_request import HttpRequestNode
from .custom_code import CustomCodeNode
from .template_conversion import TemplateConversionNode
from .variable_aggregation import VariableAggregationNode
from .tool import ToolNode
from .skill import SkillNode
from .recursive_task_generation import RecursiveTaskGenerationNode
from .recursive_task_execution import RecursiveTaskExecutionNode
from .end import EndNode
from .constant_variable import ConstantVariableNode
from ..variables import create_variable_from_dict
from core.llm.prompt import create_prompt_from_dict

# List of node types that can correct LLM model outputs
llm_correctable_node_types = ['agent', 'llm', 'recursive_task_generation']

def create_node_from_dict(node_dict: Dict[str, Any]) -> Node:
    """
    Creates a node object from a dictionary representation.

    Args:
        node_dict (Dict[str, Any]): A dictionary representing a node object.

    Returns:
        Node: An instance of a class derived from Node.
    """
    node_id = node_dict.get('id')
    node_dict.pop('id', None)
    node_dict['original_node_id'] = node_id
    
    node_data = node_dict.get('data', {})
    node_type = node_data.get('type')
    node_dict.pop('data', None)
    node_data.pop('type', None)
    
    input_dict = node_data.get('input')
    if input_dict:
        node_data['input'] = create_variable_from_dict(input_dict)
    prompt_dict = node_data.get('prompt')
    if prompt_dict:
        node_data['prompt'] = create_prompt_from_dict(prompt_dict)
    requirement_category_list = node_data.get('requirement_category')
    if requirement_category_list:
        node_data['requirement_category'] = create_requirement_category_from_dict(requirement_category_list)
    branches_dict = node_data.get('logic_branches')
    if branches_dict:
        node_data['logic_branches'] = create_logic_branches_from_dict(branches_dict)
    code_dependencies = node_data.get('code_dependencies')
    if code_dependencies:
        for key, value_list in code_dependencies.items():
            filtered_list = []
            for value in value_list:
                cleaned_value = value.replace(" ", "").replace("，", ",")
                filtered_list.extend(cleaned_value.split(","))
            code_dependencies[key] = [item for item in filtered_list if item]
    executor_list = node_data.get('executor_list')
    if executor_list:
        node_data['executor_list'] = create_nodes_from_dict(executor_list)
    output_dict = node_data.get('output')
    if output_dict:
        node_data['output'] = create_variable_from_dict(output_dict)
    
    node_dict.update(node_data)
    
    if node_type == 'start':
        return StartNode(**node_dict)
    elif node_type == 'human':
        return HumanNode(**node_dict)
    elif node_type == 'agent':
        return AgentNode(**node_dict)
    elif node_type == 'retriever':
        return RetrieverNode(**node_dict)
    elif node_type == 'memory_interrupt':
        return MemoryInterruptNode(**node_dict)
    elif node_type == 'llm':
        return LLMNode(**node_dict)
    elif node_type == 'requirement_category':
        return RequirementCategoryNode(**node_dict)
    elif node_type == 'condition_branch':
        return ConditionBranchNode(**node_dict)
    elif node_type == 'http_request':
        return HttpRequestNode(**node_dict)
    elif node_type == 'custom_code':
        return CustomCodeNode(**node_dict)
    elif node_type == 'template_conversion':
        return TemplateConversionNode(**node_dict)
    elif node_type == 'variable_aggregation':
        return VariableAggregationNode(**node_dict)
    elif node_type == 'tool':
        return ToolNode(**node_dict)
    elif node_type == 'skill':
        return SkillNode(**node_dict)
    elif node_type == 'recursive_task_generation':
        return RecursiveTaskGenerationNode(**node_dict)
    elif node_type == 'recursive_task_execution':
        return RecursiveTaskExecutionNode(**node_dict)
    elif node_type == 'constant_variable':
        return ConstantVariableNode(**node_dict)
    elif node_type == 'end':
        return EndNode(**node_dict)
    else:
        raise ValueError(f"Unknown node type: {node_type}")
    
def create_nodes_from_dict(nodes_dict: List[Dict[str, Any]]) -> Nodes:
    """
    Creates a collection of node objects from a list of dictionaries.

    Args:
        nodes_dict (List[Dict[str, Any]]): A list of dictionaries, each representing a node object.

    Returns:
        Nodes: An instance of the Nodes class containing node objects.
    """
    nodes = Nodes()
    for node_dict in nodes_dict:
        node = create_node_from_dict(node_dict)
        nodes.add_node(node)
    return nodes

__all__ = [
    "CURRENT_NODE_ID",
    "UPLOAD_FILES_KEY",
    "Node",
    "Nodes",
    "LLMBaseNode",
    "SandboxBaseNode",
    "create_node_from_dict",
    "create_nodes_from_dict",
    "llm_correctable_node_types",
    
    "StartNode",
    "HumanNode",
    "AgentNode",
    "RetrieverNode",
    "MemoryInterruptNode",
    "LLMNode",
    "RequirementCategory",
    "create_requirement_category_from_dict",
    "RequirementCategoryNode",
    "LogicCondition", 
    "LogicBranch", 
    "LogicBranches", 
    "create_logic_branches_from_dict", 
    "ConditionBranchNode",
    "HttpRequestNode",
    "CustomCodeNode",
    "TemplateConversionNode",
    "VariableAggregationNode",
    "ToolNode",
    "SkillNode",
    "RecursiveTaskGenerationNode",
    "RecursiveTaskExecutionNode",
    "ConstantVariableNode",
    "EndNode"
]