import networkx as nx
import matplotlib.pyplot as plt
import json
from typing import List, Any

class ScenarioTracker:
    def __init__(self):
        self.conversation_graph = {}
        self.nx_graph = nx.DiGraph()
        # Only add Call Start node
        self.nx_graph.add_node("Call Start")

    def track_scenario(self, path: List[dict], outcome: str) -> None:
        """
        Track a conversation scenario where nodes are questions and edges are answers.
        
        Args:
            path: List of dictionaries, each containing one question-answer pair
            outcome: The final outcome of the conversation
        """
        previous_question = ("Call Start", "begin call")  # Start from Call Start
        
        # Connect Call Start to first question if path exists
        if path and path[0]:
            first_question = next(iter(path[0].keys()))
            if first_question not in self.nx_graph:
                self.nx_graph.add_node(first_question)
            self.nx_graph.add_edge("Call Start", first_question, answer="begin call")
        
        for qa_dict in path:
            for question, answer in qa_dict.items():
                # Add question as node if it doesn't exist
                if question not in self.nx_graph:
                    self.nx_graph.add_node(question)
                
                # If there's a previous question, add an edge from it to current question
                if previous_question[0] != "Call Start":  # Skip if it's the Call Start node
                    self.nx_graph.add_edge(
                        previous_question[0],
                        question,
                        answer=previous_question[1]
                    )
                
                previous_question = (question, answer)
        
        # Add the final outcome
        outcome_node = f"Outcome: {outcome}"
        self.nx_graph.add_node(outcome_node, is_outcome=True)
        if previous_question:
            self.nx_graph.add_edge(
                previous_question[0],
                outcome_node,
                answer=previous_question[1]
            )

    def export_graph(self, format: str = 'json') -> Any:
        if format == 'json':
            # Convert networkx graph to JSON format
            graph_data = {
                "nodes": list(self.nx_graph.nodes()),
                "edges": [
                    {
                        "from": u,
                        "to": v,
                        "answer": data.get("answer", "")
                    }
                    for u, v, data in self.nx_graph.edges(data=True)
                ]
            }
            return json.dumps(graph_data, indent=2)
        
        elif format == 'visual':
            plt.figure(figsize=(20, 15))
            
            # Start with basic layout
            pos = nx.spring_layout(self.nx_graph)
            
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
            
            # Draw straight edges with arrows
            nx.draw_networkx_edges(self.nx_graph, pos,
                                 arrows=True,
                                 arrowsize=30,
                                 edge_color='gray',
                                 width=3)
            
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
            
            # Draw edge labels with much larger font
            edge_labels = nx.get_edge_attributes(self.nx_graph, 'answer')
            wrapped_edge_labels = {k: v if len(v) < 20 else v[:17] + '...' 
                                 for k, v in edge_labels.items()}
            
            nx.draw_networkx_edge_labels(
                self.nx_graph,
                pos,
                edge_labels=wrapped_edge_labels,
                font_size=12,  # Much larger font size for edge labels
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)  # Add background to edge labels
            )
            
            plt.savefig('conversation_graph.png', bbox_inches='tight', dpi=300)
            return 'conversation_graph.png' 