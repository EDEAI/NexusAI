import uuid
from typing import Any, Dict, List, Optional

class Edge:
    """
    Represents an edge in a workflow, connecting two nodes.
    """

    def __init__(
        self, 
        level: int,
        source_node_id: str, 
        target_node_id: str, 
        source_node_type: str, 
        target_node_type: str, 
        is_logical_branch: bool = False, 
        condition_id: Optional[str] = None,
        views: Dict[str, Any] = {},
        original_edge_id: Optional[str] = None
    ) -> None:
        """
        Initializes a new instance of the Edge class.

        Args:
            level (int): The level of the edge in the workflow.
            source_node_id (str): The ID of the source node.
            target_node_id (str): The ID of the target node.
            source_node_type (str): The type of the source node.
            target_node_type (str): The type of the target node.
            is_logical_branch (bool): Indicates if the edge is part of a logical branch.
            condition_id (Optional[str]): The condition identifier to match against the source node's output.
            views (Dict[str, Any]): Data required by the web.
            original_edge_id (Optional[str]): The original ID of the edge if it's being recreated or duplicated. If provided, this ID is used instead of generating a new one.
        """
        self.id: str = original_edge_id if original_edge_id is not None else str(uuid.uuid4())
        self.level: int = level
        self.source_node_id: str = source_node_id
        self.target_node_id: str = target_node_id
        self.source_node_type: str = source_node_type
        self.target_node_type: str = target_node_type
        self.is_logical_branch: bool = is_logical_branch
        self.views: int = views
        if condition_id is not None:
            self.condition_id: str = condition_id
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Edge object to a dictionary.

        Returns:
            Dict[str, Any]: A dictionary representation of the Edge object.
        """
        data = {
            "id": self.id,
            "level": self.level,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "source_node_type": self.source_node_type,
            "target_node_type": self.target_node_type,
            "is_logical_branch": self.is_logical_branch,
            "views": self.views
        }
        if hasattr(self, "condition_id"):
            data["condition_id"] = self.condition_id
        return data
        
class Edges:
    """
    Represents a collection of Edge instances in a workflow.

    Attributes:
        edges (List[Edge]): A list of Edge instances.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the Edges class.
        """
        self.edges: List[Edge] = []

    def add_edge(self, edge: Edge) -> None:
        """
        Adds an Edge instance to the collection.

        Args:
            edge (Edge): The Edge instance to be added.
        """
        self.edges.append(edge)

    def to_dict(self) -> List[Dict[str, Any]]:
        """
        Converts the collection of Edge instances to a list of dictionaries.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing an Edge instance.
        """
        return [edge.to_dict() for edge in self.edges]
    
    def build_edge_maps(self) -> Dict[str, Dict[str, List[Edge]]]:
        """
        Builds mappings of nodes to their incoming and outgoing edges.

        Returns:
            Dict[str, Dict[str, List[Edge]]]: A dictionary containing two dictionaries:
                - 'incoming': Maps node IDs to lists of incoming edges.
                - 'outgoing': Maps node IDs to lists of outgoing edges.
        """
        node_to_incoming_edges = {}
        node_to_outgoing_edges = {}

        for edge in self.edges:
            if edge.source_node_id not in node_to_outgoing_edges:
                node_to_outgoing_edges[edge.source_node_id] = []
            node_to_outgoing_edges[edge.source_node_id].append(edge)

            if edge.target_node_id not in node_to_incoming_edges:
                node_to_incoming_edges[edge.target_node_id] = []
            node_to_incoming_edges[edge.target_node_id].append(edge)

        return {
            'incoming': node_to_incoming_edges,
            'outgoing': node_to_outgoing_edges
        }
        
    def get_all_ancestor_node_ids(self, node_id: str) -> List[str]:
        """
        Recursively finds all ancestor node IDs for a given node ID.

        Args:
            node_id (str): The ID of the node to find ancestors for.

        Returns:
            List[str]: A list of all ancestor node IDs.
        """
        ancestor_node_ids = []

        def find_ancestors(current_node_id: str):
            for edge in self.edges:
                if edge.target_node_id == current_node_id:
                    if edge.source_node_id not in ancestor_node_ids:
                        ancestor_node_ids.append(edge.source_node_id)
                        find_ancestors(edge.source_node_id)

        find_ancestors(node_id)
        return ancestor_node_ids
    
def create_edge_from_dict(edge_dict: Dict[str, Any]) -> Edge:
    """
    Creates an Edge instance from a dictionary representation.

    Args:
        edge_dict (Dict[str, Any]): A dictionary representing an Edge instance.

    Returns:
        Edge: An Edge instance created from the dictionary.
    """
    return Edge(
        level=edge_dict["level"],
        source_node_id=edge_dict["source_node_id"], 
        target_node_id=edge_dict["target_node_id"], 
        source_node_type=edge_dict["source_node_type"],
        target_node_type=edge_dict["target_node_type"],
        is_logical_branch=edge_dict["is_logical_branch"],
        views=edge_dict["views"],
        original_edge_id=edge_dict.get("id"),
        **({"condition_id": edge_dict["condition_id"]} if "condition_id" in edge_dict else {})
    )

def create_edges_from_list(edge_list: List[Dict[str, Any]]) -> Edges:
    """
    Creates an Edges instance from a list of dictionaries.

    Args:
        edge_list (List[Dict[str, Any]]): A list of dictionaries representing Edge instances.

    Returns:
        Edges: An Edges instance containing Edge instances created from the list of dictionaries.
    """
    edges = Edges()
    for edge_dict in edge_list:
        edges.add_edge(create_edge_from_dict(edge_dict))
    return edges