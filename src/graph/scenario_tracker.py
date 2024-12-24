import networkx as nx
import matplotlib.pyplot as plt
import json
from typing import List, Any

class ScenarioTracker:
    """
    A class for tracking and visualizing conversation scenarios in a directed graph.
    
    This tracker maintains a graph structure where:
    - Nodes represent questions or outcomes
    - Edges represent answers
    - Special nodes include "Call Start" and outcome nodes
    - Multiple edges between the same nodes are supported for different answers
    
    The graph can be exported in either JSON format or as a visual representation.

    Attributes:
        conversation_graph (dict): Legacy storage for conversation data
        nx_graph (nx.MultiDiGraph): NetworkX graph storing the conversation structure
    """

    def __init__(self):
        """
        Initialize a new ScenarioTracker.

        Creates an empty MultiDiGraph and adds the initial "Call Start" node.
        """
        self.conversation_graph = {}
        self.nx_graph = nx.MultiDiGraph()
        self.nx_graph.add_node("Call Start")

    def track_scenario(self, path: List[dict], outcome: str) -> None:
        """
        Track a conversation scenario by adding its path and outcome to the graph.

        Builds a path through the graph representing a conversation, where each step
        is a question-answer pair, ending with an outcome node.

        Args:
            path (List[dict]): List of dictionaries, each containing one question-answer pair
                Format: [{"question1": "answer1"}, {"question2": "answer2"}, ...]
            outcome (str): The final outcome of the conversation

        Example:
            >>> tracker = ScenarioTracker()
            >>> tracker.track_scenario(
            ...     [{"Are you an existing customer?": "Yes"},
            ...      {"Is this an emergency?": "No"}],
            ...     "schedule_service"
            ... )
        """
        previous_question = ("Call Start", "begin call")
        
        # Connect Call Start to first question if path exists
        if path and path[0]:
            first_question = next(iter(path[0].keys()))
            if first_question not in self.nx_graph:
                self.nx_graph.add_node(first_question)
            self.nx_graph.add_edge("Call Start", first_question, answer="begin call")
        
        for qa_dict in path:
            for question, answer in qa_dict.items():
                if question not in self.nx_graph:
                    self.nx_graph.add_node(question)
                
                if previous_question[0] != "Call Start":
                    self.nx_graph.add_edge(
                        previous_question[0],
                        question,
                        answer=previous_question[1]
                    )
                
                previous_question = (question, answer)
        
        outcome_node = f"Outcome: {outcome}"
        self.nx_graph.add_node(outcome_node, is_outcome=True)
        if previous_question:
            self.nx_graph.add_edge(
                previous_question[0],
                outcome_node,
                answer=previous_question[1]
            )

    def export_graph(self, format: str = 'json') -> Any:
        """
        Export the conversation graph in either JSON or visual format.

        Provides two export options:
        1. JSON: A serialized representation of nodes and edges
        2. Visual: A matplotlib visualization saved as PNG

        Args:
            format (str, optional): Export format, either 'json' or 'visual'. Defaults to 'json'.

        Returns:
            Any: 
                - If format='json': JSON string containing graph structure
                - If format='visual': Path to saved PNG file ('conversation_graph.png')

        Example:
            >>> tracker = ScenarioTracker()
            >>> # Export as JSON
            >>> json_data = tracker.export_graph('json')
            >>> # Export as visualization
            >>> png_path = tracker.export_graph('visual')

        Visual Format Features:
            - Node colors: lightgray (start), lightblue (questions), lightgreen (outcomes)
            - Node shapes: square (start), circle (questions), diamond (outcomes)
            - Curved edges for multiple paths between same nodes
            - Edge labels showing answers
            - Hierarchical layout with layers
            - Automatic text wrapping for long labels
            - High-resolution output (300 DPI)

        JSON Format Structure:
            {
                "nodes": ["Call Start", "Question 1", "Outcome: X", ...],
                "edges": [
                    {"from": "Node A", "to": "Node B", "answer": "Yes", "key": 0},
                    ...
                ]
            }
        """
        if format == 'json':
            # Modified JSON format to handle multiple edges
            graph_data = {
                "nodes": list(self.nx_graph.nodes()),
                "edges": [
                    {
                        "from": u,
                        "to": v,
                        "answer": data.get("answer", ""),
                        "key": k  # Include edge key for multiple edges
                    }
                    for u, v, k, data in self.nx_graph.edges(data=True, keys=True)
                ]
            }
            return json.dumps(graph_data, indent=2)
        
        elif format == 'visual':
            plt.figure(figsize=(20, 15))
            
            # Use kamada_kawai layout
            pos = nx.kamada_kawai_layout(self.nx_graph)
            
            # Create layers based on distance from Call Start
            layers = {}
            layers[0] = ["Call Start"]
            
            # Find all paths from Call Start to identify question order
            paths = []
            for node in self.nx_graph.nodes():
                if node != "Call Start" and not node.startswith("Outcome:"):
                    try:
                        path = nx.shortest_path(self.nx_graph, "Call Start", node)
                        paths.append(path)
                    except nx.NetworkXNoPath:
                        continue
            
            # Group nodes by their layer (distance from Call Start)
            max_layer = 1
            for path in paths:
                for i, node in enumerate(path[1:], 1):  # Skip Call Start
                    if i not in layers:
                        layers[i] = []
                    if node not in layers[i]:
                        layers[i].append(node)
                    max_layer = max(max_layer, i)
            
            # Add outcomes to the final layer
            outcome_layer = max_layer + 1
            layers[outcome_layer] = [node for node in self.nx_graph.nodes() if node.startswith("Outcome:")]
            
            # Position nodes in layers
            for layer, nodes in layers.items():
                y_coord = 1.0 - (layer * (1.0 / (len(layers) + 1)))  # Distribute layers evenly
                for i, node in enumerate(nodes):
                    x_coord = (i + 1) / (len(nodes) + 1)  # Distribute nodes within layer
                    pos[node] = (x_coord, y_coord)
            
            # Rest of the drawing code remains the same
            regular_nodes = [node for node in self.nx_graph.nodes() 
                           if not node.startswith("Outcome:") and node != "Call Start"]
            outcome_nodes = [node for node in self.nx_graph.nodes() 
                           if node.startswith("Outcome:")]
            start_nodes = ["Call Start"]
            
            # Draw nodes with different shapes and colors
            nx.draw_networkx_nodes(self.nx_graph, pos,
                                 nodelist=start_nodes,
                                 node_color='lightgray',
                                 node_size=7000,
                                 node_shape='s')
            
            nx.draw_networkx_nodes(self.nx_graph, pos, 
                                 nodelist=regular_nodes,
                                 node_color='lightblue',
                                 node_size=7000,
                                 node_shape='o')
            
            nx.draw_networkx_nodes(self.nx_graph, pos,
                                 nodelist=outcome_nodes,
                                 node_color='lightgreen',
                                 node_size=7000,
                                 node_shape='d')
            
            # Modified edge drawing to handle multiple edges without duplicates
            edges_by_nodes = {}
            # Group edges by their endpoints and answers
            for u, v, k, data in self.nx_graph.edges(data=True, keys=True):
                answer = data.get('answer', '')
                if (u, v) not in edges_by_nodes:
                    edges_by_nodes[(u, v)] = {}
                # Only add if this answer doesn't exist yet
                if answer not in edges_by_nodes[(u, v)]:
                    edges_by_nodes[(u, v)][answer] = k
            
            # Draw edges with proper offsets
            for (u, v), answers in edges_by_nodes.items():
                unique_answers = list(answers.keys())
                for idx, answer in enumerate(unique_answers):
                    # Calculate offset based on number of unique answers
                    if len(unique_answers) == 1:
                        offset = 0
                    else:
                        offset = 0.2 * (idx - (len(unique_answers) - 1) / 2)
                    
                    # Create curved path
                    nx.draw_networkx_edges(self.nx_graph,
                                         pos,
                                         edgelist=[(u, v)],
                                         arrows=True,
                                         arrowsize=20,
                                         edge_color='black',
                                         width=1.5,
                                         arrowstyle='-|>',
                                         connectionstyle=f'arc3, rad={offset}')
                    
                    # Add edge label
                    x = (pos[u][0] + pos[v][0]) / 2
                    y = (pos[u][1] + pos[v][1]) / 2
                    if offset != 0:
                        # Adjust label position for curved edges
                        y += offset * 0.5
                    plt.text(x, y, answer if len(answer) < 20 else answer[:17] + '...',
                            fontsize=12,
                            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7),
                            horizontalalignment='center',
                            verticalalignment='center')
            
            # Draw labels with larger font
            labels = {}
            for node in self.nx_graph.nodes():
                if len(str(node)) > 20:
                    words = str(node).split()
                    lines = []
                    current_line = []
                    current_length = 0
                    
                    for word in words:
                        if current_length + len(word) > 20:
                            lines.append(' '.join(current_line))
                            current_line = [word]
                            current_length = len(word)
                        else:
                            current_line.append(word)
                            current_length += len(word) + 1
                    
                    if current_line:
                        lines.append(' '.join(current_line))
                    
                    labels[node] = '\n'.join(lines)
                else:
                    labels[node] = node
            
            nx.draw_networkx_labels(
                self.nx_graph,
                pos,
                labels=labels,
                font_size=12  # Increased font size
            )
            
            plt.savefig('conversation_graph.png', bbox_inches='tight', dpi=300)
            return 'conversation_graph.png' 