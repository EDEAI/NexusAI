import sys
from typing import Dict, Any
from .nodes import Nodes, create_nodes_from_dict
from . import Edges, create_edges_from_list
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent.parent))
from languages import get_language_content

class Graph:
    """
    Represents a workflow graph structure that contains nodes and edges.
    Provides validation and visualization capabilities for the workflow.
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

    def find_related_nodes(self, source_id) -> list:
        """
        Recursively find all target nodes associated with the given source node
        Args:
            source_id: The source node ID to start searching from
            edges: List of edges representing connections between nodes
        Returns:
            List of all node IDs related to the source node (directly or indirectly)
        """
        related_nodes = []

        # Find directly connected target nodes
        direct_targets = [edge.target_node_id for edge in self.edges.edges
                          if edge.source_node_id == source_id]

        if not direct_targets:
            return []

        # Add direct targets to result list
        related_nodes.extend(direct_targets)

        # Recursively find connected nodes for each target
        for target_id in direct_targets:
            child_nodes = self.find_related_nodes(target_id)
            related_nodes.extend(child_nodes)

        return list(set(related_nodes))  # Remove duplicates and return

    def validate(self) -> None:
        """
        Validates the workflow graph structure and node configurations.

        Performs the following validations:
        1. Graph structure validation:
           - Single start node requirement
           - Edge connections validation
           - Node connectivity checks
        2. Node-specific validation:
           - LLM node prompt configuration
           - Agent node prompt configuration
           - Task execution node and its executors
           - Input parameter requirements

        Raises:
            ValueError: When validation fails with specific error message
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
            node_ids.append(node.id)
            incoming_edges[node.id] = 0
            outgoing_edges[node.id] = 0

        for edge in self.edges.edges:
            if edge.source_node_id not in node_ids or edge.target_node_id not in node_ids:
                raise ValueError(get_language_content("graph_validation_errors.nonexistent_edge_nodes"))

            outgoing_edges[edge.source_node_id] += 1
            incoming_edges[edge.target_node_id] += 1
        connected_node_ids = []
        for current_node in self.nodes.nodes:
            node_metadata = current_node.data

            if current_node.data['type'] == 'start':
                if incoming_edges[current_node.id] > 0:
                    raise ValueError(get_language_content("graph_validation_errors.start_node_incoming_edges"))
                if outgoing_edges[current_node.id] > 1:
                    raise ValueError(get_language_content("graph_validation_errors.start_node_outgoing_edges"))
                connected_node_ids = self.find_related_nodes(current_node.id)
                self._validate_node_has_input_properties(node_metadata)

            if current_node.id in connected_node_ids:
                if node_metadata['type'] == 'end':
                    self._validate_node_has_output_properties(node_metadata)
                    continue

                # Validate nodes based on their types
                node_type = current_node.data['type']
                if node_type == 'llm':
                    self._validate_llm_node(node_metadata)
                elif node_type == 'agent':
                    self._validate_agent_node(node_metadata)
                elif node_type == 'recursive_task_execution':
                    self._validate_task_execution_node(node_metadata)
                elif node_type == 'human':
                    self._validate_node_has_input_properties(node_metadata)

                # Only validate input config if node has input and is not a human node
                if 'input' in node_metadata and node_metadata['type'] != 'human':
                    self._validate_input_config(node_metadata)

        if start_node_count != 1:
            raise ValueError(get_language_content("graph_validation_errors.exactly_one_start_node"))
        # if end_node_count != 1:
        #     raise ValueError(get_language_content("graph_validation_errors.exactly_one_end_node"))

    def _validate_node_has_input_properties(self, node_metadata):
        """
        Validates that a node (specifically start and human nodes) has input properties.
        
        Args:
            node_metadata (dict): Node configuration data
            
        Raises:
            ValueError: When the node doesn't have input properties
        """
        if 'input' not in node_metadata or not hasattr(node_metadata['input'], 'properties') or not node_metadata['input'].properties:
            raise ValueError(
                get_language_content("graph_validation_errors.node_missing_input").format(
                    node_title=node_metadata['title']
                )
            )

    def _validate_node_has_output_properties(self, node_metadata):
        """
        Validates that a node (specifically end node) has output properties.
        
        Args:
            node_metadata (dict): Node configuration data
            
        Raises:
            ValueError: When the node doesn't have output properties
        """
        if 'output' not in node_metadata or not hasattr(node_metadata['output'], 'properties') or not node_metadata['output'].properties:
            raise ValueError(
                get_language_content("graph_validation_errors.node_missing_output").format(
                    node_title=node_metadata['title']
                )
            )

    def _validate_llm_node(self, node_metadata):
        """
        Validates Large Language Model node configuration.
        Ensures either system prompt or user prompt is properly configured.

        Args:
            node_metadata (dict): Node configuration data containing prompt settings

        Raises:
            ValueError: When neither system nor user prompt is properly configured
        """
        if 'prompt' in node_metadata:
            prompt = node_metadata['prompt']
            # Check if system prompt exists and has value
            has_system = (hasattr(prompt, 'system') and
                          hasattr(prompt.system, 'value') and
                          prompt.system.value is not None and
                          str(prompt.system.value).strip() != '')
            # Check if user prompt exists and has value
            has_user = (hasattr(prompt, 'user') and
                        hasattr(prompt.user, 'value') and
                        prompt.user.value is not None and
                        str(prompt.user.value).strip() != '')

            if not has_system and not has_user:
                raise ValueError(
                    get_language_content("graph_validation_errors.llm_prompt_required").format(
                        node_title=node_metadata['title']
                    )
                )

    def _validate_agent_node(self, node_metadata):
        """
        Validates Agent node configuration.
        Ensures user prompt is properly configured.

        Args:
            node_metadata (dict): Node configuration data containing prompt settings

        Raises:
            ValueError: When user prompt is not properly configured
        """
        if 'prompt' in node_metadata:
            prompt = node_metadata['prompt']
            # Check if user prompt exists and has value
            has_user = (hasattr(prompt, 'user') and
                        hasattr(prompt.user, 'value') and
                        prompt.user.value is not None and
                        str(prompt.user.value).strip() != '')

            if not has_user:
                raise ValueError(
                    get_language_content("graph_validation_errors.agent_prompt_required").format(
                        node_title=node_metadata['title']
                    )
                )

    def _validate_task_execution_node(self, node_metadata):
        """
        Validates task execution node and its executor configurations.
        """
        executor_list = node_metadata.get('executor_list')

        # Check if executor_list is a Nodes object and has nodes
        if executor_list and hasattr(executor_list, 'nodes'):
            for executor in executor_list.nodes:
                executor_type = executor.data.get('type')
                executor_title = executor.data.get('title', '')

                if executor_type == 'llm':
                    self._validate_executor_llm(executor.data, node_metadata['title'], executor_title)
                elif executor_type == 'agent':
                    self._validate_executor_agent(executor.data, node_metadata['title'], executor_title)

                if 'input' in executor.data:
                    self._validate_input_config(executor.data)

    def _validate_executor_llm(self, executor_data, node_title, executor_title):
        """
        Validates LLM executor configuration within a task execution node.
        Ensures proper prompt configuration for the executor.

        Args:
            executor_data (dict): Executor configuration data
            node_title (str): Parent node title for error messages
            executor_title (str): Executor title for error messages

        Raises:
            ValueError: When prompt configuration is invalid
        """
        if 'prompt' in executor_data:
            prompt = executor_data['prompt']
            # Check if system prompt exists and has value
            has_system = (hasattr(prompt, 'system') and
                          hasattr(prompt.system, 'value') and
                          prompt.system.value is not None and
                          str(prompt.system.value).strip() != '')
            # Check if user prompt exists and has value
            has_user = (hasattr(prompt, 'user') and
                        hasattr(prompt.user, 'value') and
                        prompt.user.value is not None and
                        str(prompt.user.value).strip() != '')

            if not has_system and not has_user:
                raise ValueError(
                    get_language_content("graph_validation_errors.executor_llm_prompt_required").format(
                        node_title=node_title,
                        executor_title=executor_title
                    )
                )

    def _validate_executor_agent(self, executor_data, node_title, executor_title):
        """
        Validates Agent executor configuration within a task execution node.
        Ensures proper user prompt configuration for the executor.

        Args:
            executor_data (dict): Executor configuration data
            node_title (str): Parent node title for error messages
            executor_title (str): Executor title for error messages

        Raises:
            ValueError: When user prompt is not properly configured
        """
        if 'prompt' in executor_data:
            prompt = executor_data['prompt']
            # Check if user prompt exists and has value
            has_user = (hasattr(prompt, 'user') and
                        hasattr(prompt.user, 'value') and
                        prompt.user.value is not None and
                        str(prompt.user.value).strip() != '')

            if not has_user:
                raise ValueError(
                    get_language_content("graph_validation_errors.executor_agent_prompt_required").format(
                        node_title=node_title,
                        executor_title=executor_title
                    )
                )

    def _validate_input_config(self, metadata):
        """
        Validates input configuration and its required properties.
        Only validates when input configuration exists and contains required properties.

        Args:
            metadata (dict): Node/executor metadata containing input configuration

        Debug logs:
            Prints validation status for nodes with required properties

        Raises:
            ValueError: When required parameters are missing or empty
        """
        if 'input' not in metadata:
            return

        input_config = metadata['input']
        if not hasattr(input_config, 'properties'):
            return

        properties = input_config.properties
        if not properties:
            return

        # Only validate required properties
        for prop_name, prop_config in properties.items():
            is_required = hasattr(prop_config, 'required') and getattr(prop_config, 'required', True)
            if is_required:
                prop_value = getattr(prop_config, 'value', None)
                if prop_value is None or str(prop_value).strip() == '':
                    raise ValueError(
                        get_language_content("graph_validation_errors.required_param_missing").format(
                            node_title=metadata['title'],
                            param_name=prop_name
                        )
                    )

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