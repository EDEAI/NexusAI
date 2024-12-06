import sys
from typing import Dict, Any
from .nodes import Nodes, create_nodes_from_dict
from . import Edges, create_edges_from_list
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent.parent))
from languages import get_language_content

class Graph:
    """
    Represents a graphical representation of a workflow, including nodes, edges, and view properties.
    """

    def __init__(self, nodes: Nodes, edges: Edges, views: Dict[str, Any] = {}):
        """
        Initializes a new instance of the Graph class.

        Args:
            nodes (Nodes): An instance of the Nodes class, representing the nodes in the workflow.
            edges (Edges): An instance of the Edges class, representing the edges in the workflow.
            views (Dict[str, Any]): Data required by the web.
        """
        self.nodes = nodes
        self.edges = edges
        self.views = views

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Graph object into a dictionary representation.

        Returns:
            Dict[str, Any]: A dictionary representing the Graph object, including nodes, edges, and view properties.
        """
        return {
            "nodes": self.nodes.to_dict(),
            "edges": self.edges.to_dict(),
            "views": self.views
        }
        
    def get_total_steps(self) -> int:
        """
        Returns the total number of steps in the workflow.

        Returns:
            int: The total number of steps in the workflow.
        """
        return len(self.edges.edges)
    
    def validate(self) -> None:
        """
        Validates the graph data according to the specified rules.
        
        Raises:
            ValueError: If the graph data is invalid according to the specified rules.
        """
        start_node_count = 0
        end_node_count = 0
        node_ids = []
        incoming_edges = {}
        outgoing_edges = {}
        level_one_edge_found = False
        
        for node in self.nodes.nodes:
            if node.data['type'] == 'start':
                start_node_count += 1
                if start_node_count > 1:
                    raise ValueError(get_language_content("graph_validation_errors.multiple_start_nodes"))
            elif node.data['type'] == 'end':
                end_node_count += 1
                if end_node_count > 1:
                    raise ValueError(get_language_content("graph_validation_errors.multiple_end_nodes"))
            node_ids.append(node.id)
            incoming_edges[node.id] = 0
            outgoing_edges[node.id] = 0

        for edge in self.edges.edges:
            if edge.level == 1:
                if level_one_edge_found:
                    raise ValueError(get_language_content("graph_validation_errors.multiple_level_one_edges"))
                level_one_edge_found = True
                source_node = self.nodes.get_node(edge.source_node_id)
                if edge.source_node_type != 'start' or not source_node or source_node.data['type'] != 'start':
                    raise ValueError(get_language_content("graph_validation_errors.invalid_level_one_edge_source"))

            if edge.source_node_id not in node_ids or edge.target_node_id not in node_ids:
                raise ValueError(get_language_content("graph_validation_errors.nonexistent_edge_nodes"))

            outgoing_edges[edge.source_node_id] += 1
            incoming_edges[edge.target_node_id] += 1

        for node in self.nodes.nodes:
            if node.data['type'] == 'start':
                if incoming_edges[node.id] > 0:
                    raise ValueError(get_language_content("graph_validation_errors.start_node_incoming_edges"))
                if outgoing_edges[node.id] > 1:
                    raise ValueError(get_language_content("graph_validation_errors.start_node_outgoing_edges"))
            elif node.data['type'] == 'end':
                if incoming_edges[node.id] == 0:
                    raise ValueError(get_language_content("graph_validation_errors.end_node_incoming_edges"))
                if outgoing_edges[node.id] > 0:
                    raise ValueError(get_language_content("graph_validation_errors.end_node_outgoing_edges"))
            elif incoming_edges[node.id] == 0 or outgoing_edges[node.id] == 0:
                raise ValueError(get_language_content("graph_validation_errors.node_incoming_outgoing_edges").format(node_id=node.id))

        if start_node_count != 1:
            raise ValueError(get_language_content("graph_validation_errors.exactly_one_start_node"))
        if end_node_count != 1:
            raise ValueError(get_language_content("graph_validation_errors.exactly_one_end_node"))
    
    def display(self) -> None:
        """
        Displays the workflow as a directed graph.
        """
        import matplotlib.pyplot as plt
        import networkx as nx
        from networkx.drawing.nx_agraph import graphviz_layout

        G = nx.DiGraph()

        # Add nodes
        for node in self.nodes.nodes:
            G.add_node(node.id, label=f"{node.data['title']}\n{node.data['type']}")
        # Add edges
        for edge in self.edges.edges:
            G.add_edge(edge.source_node_id, edge.target_node_id)
            G.add_edge(edge.source_node_id, edge.target_node_id, label=str(edge.level))

        # Use graphviz_layout for hierarchical layout
        pos = graphviz_layout(G, prog='dot')
        
        # Estimate figure size based on the number of nodes
        num_nodes = len(G.nodes)
        fig_width = max(10, num_nodes * 1.5)
        fig_height = max(10, num_nodes * 1.5)
        
        # Create a figure with a fixed size
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=7000, node_color='skyblue')
        # Draw edges
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=G.edges(), arrows=True)
        # Draw labels
        labels = nx.get_node_attributes(G, 'label')
        nx.draw_networkx_labels(G, pos, labels, font_size=12, ax=ax)
        # Draw edge labels
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)

        plt.title("Workflow Graph")
        
        # Enable pan and zoom
        plt.tight_layout()
        plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
        
        # Get screen size and adjust figure window size
        # screen_width, screen_height = pyautogui.size()
        # fig.canvas.manager.window.wm_geometry(f"{screen_width}x{screen_height}+0+0")
    
        plt.show()

def create_graph_from_dict(graph_dict: Dict[str, Any]) -> Graph:
    """
    Creates a Graph object from a dictionary representation.

    Args:
        graph_dict (Dict[str, Any]): A dictionary representing a Graph object.

    Returns:
        Graph: An instance of the Graph class.
    """
    nodes = create_nodes_from_dict(graph_dict["nodes"])
    edges = create_edges_from_list(graph_dict["edges"])
    views = graph_dict["views"]
    return Graph(nodes, edges, views)