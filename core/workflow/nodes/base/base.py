import uuid
from typing import Dict, List, Union, Any, Optional
from ...variables import VariableTypes

# Current node id, used when the node references its own input variables
CURRENT_NODE_ID = '536f6e67-bcab-cbd9-cfc0-4d6172637573'


class Node:
    """
    A Node object is used to create a node in a workflow.
    """

    def __init__(
        self,
        type: str,
        title: str,
        desc: str = "",
        flow_data: Dict[str, Any] = {},
        **kwargs
    ):
        """
        Initializes a Node object with enhanced parameter types and structures.

        :param type: str, the type of the node.
        :param title: str, the title of the node.
        :param desc: str, a description of what the node does.
        :param input: VariableTypes, an instance of one of these classes containing all input variables for the node.
        :param agent_id: int, the unique identifier of the agent.
        :param model_config_id: int, the unique identifier of the LLM model configuration.
        :param ability_id: int, the unique identifier of the agent's ability. A value of 0 indicates the default ability.
        :param requirement_category: RequirementCategory, an instance of RequirementCategory for the node.
        :param prompt: Prompt, an instance of Prompt for the node.
        :param retrieval_task_datasets: list, the IDs of the datasets required by the retrieval task.
        :param datasets: list, the IDs of the datasets required by the node.
        :param logic_branches: LogicBranches, an instance of LogicBranches for the node.
        :param skill_id: int, the unique identifier of the skill.
        :param code_dependencies: dict, the packages required to run custom code.
        :param custom_code: dict, the custom code to run.
        :param tool: dict, tool information, including tool name and provider.
        :param executor_list: Nodes, the executor node when the recursive_task_execution node is running, including only LLM/agent nodes
        :param output: VariableTypes, an instance of one of these classes containing all output variables for the node.
        :param requires_upload: bool, indicates whether the node requires file upload.
        :param wait_for_all_predecessors: bool, indicates whether the node should wait for all predecessors to complete before executing.
        :param task_splitting: bool, indicates whether the node requires task splitting.
        :param manual_confirmation: bool, indicates whether the node requires manual confirmation before proceeding.
        :param import_to_knowledge_base: dict, structure: {'input': (bool), 'output': (bool)},
            indicates whether the input file/output data should be imported into the knowledge base.
        :param knowledge_base_mapping: dict, structure: {'input': (dict), 'output': (dict)},
            dict structure: {variable name (str): dataset_id (int) or upload files dict with structure {variable_name (str): dataset_id (int)} },
            specifies the mapping between file/data variables to be imported and the knowledge base datasets.
        :param interrupt_retrieval_memory: bool, indicates whether to interrupt knowledge base retrieval memory.
        :param interrupt_conversation_memory: bool, indicates whether to interrupt conversation memory.
        :param flow_data: dict, data required by the web.
        :param original_node_id: str, the original ID of the node if it's being recreated or duplicated. This parameter is optional.
        """
        if 'original_node_id' in kwargs:
            self.id = kwargs['original_node_id']
            del kwargs['original_node_id']
        else:
            self.id = str(uuid.uuid4())
        self.data: Dict[str, Union[str, VariableTypes, List, Dict, bool]] = {"type": type, "title": title, "desc": desc, **kwargs}
        self.flow_data: Dict[str, Any] = flow_data

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Node object to a dictionary.
        """
        data_dict: Dict[str, Any] = {}
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                continue
            if k == 'data':
                data_dict[k] = {kk: vv.to_dict() if hasattr(vv, 'to_dict') else vv for kk, vv in v.items()}
            else:
                if hasattr(v, 'to_dict'):
                    data_dict[k] = v.to_dict()
                else:
                    data_dict[k] = v
        return data_dict

class Nodes:
    """
    Represents a collection of node objects in a workflow.

    Attributes:
        nodes (List[Node]): A list of node objects, where each node is an instance of a class derived from Node.
    """

    def __init__(self):
        """
        Initializes a new instance of the Nodes class, setting up an empty list to store node objects.
        """
        self.nodes: List[Node] = []

    def add_node(self, node: Node) -> None:
        """
        Adds a node object to the collection.

        Args:
            node (Node): The node object to be added to the collection. Must be an instance of a class derived from Node.
        """
        self.nodes.append(node)

    def to_dict(self) -> List[Dict[str, Any]]:
        """
        Converts the collection of node objects to a list of dictionaries.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a node object.
        """
        return [node.to_dict() for node in self.nodes]
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """
        Retrieves a node object from the collection by its ID.

        Args:
            node_id (str): The ID of the node to retrieve.

        Returns:
            Node: The node object with the specified ID.
        """
        return next((node for node in self.nodes if node.id == node_id), None)