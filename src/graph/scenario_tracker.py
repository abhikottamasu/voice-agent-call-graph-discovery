import networkx as nx
import matplotlib.pyplot as plt
import json
from typing import List, Any

class ScenarioTracker:
    def __init__(self):
        self.conversation_graph = {}
        self.nx_graph = nx.DiGraph()
        # Add start node
        self.nx_graph.add_node("Start")

    def track_scenario(self, path: List[dict], outcome: str) -> None:
        """
        Track a conversation scenario where nodes are questions and edges are answers.
        
        Args:
            path: List of dictionaries, each containing one question-answer pair
            outcome: The final outcome of the conversation
        """
        previous_question = ("Start", None)  # Start from the Start node
        
        # Add Call Start node and connect it to first question
        call_start = "Call Start"
        if call_start not in self.nx_graph:
            self.nx_graph.add_node(call_start)
            self.nx_graph.add_edge("Start", call_start, answer="begin call")
        
        # Connect Call Start to first question if path exists
        if path and path[0]:
            first_question = next(iter(path[0].keys()))
            self.nx_graph.add_edge(call_start, first_question, answer="starts")
        
        for qa_dict in path:
            for question, answer in qa_dict.items():
                # Add question as node if it doesn't exist
                if question not in self.nx_graph:
                    self.nx_graph.add_node(question)
                
                # If there's a previous question, add an edge from it to current question
                if previous_question[1]:  # Skip if it's the start node's None answer
                    self.nx_graph.add_edge(
                        previous_question[0],
                        question,
                        answer=previous_question[1]
                    )
                
                previous_question = (question, answer)
        
        # Add the final outcome
        outcome_node = f"Outcome: {outcome}"
        self.nx_graph.add_node(outcome_node, is_outcome=True)  # Mark as outcome node
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
            plt.figure(figsize=(20, 15))  # Increased figure size
            
            # Use kamada_kawai layout
            pos = nx.kamada_kawai_layout(self.nx_graph)
            
            # Center Call Start at the top
            max_y = max(coord[1] for coord in pos.values())
            pos["Call Start"] = (0.5, max_y + 0.2)  # Center x-coordinate at 0.5
            
            # Adjust outcome nodes to be at the bottom
            outcome_nodes = [node for node in self.nx_graph.nodes() if node.startswith("Outcome:")]
            min_y = min(coord[1] for coord in pos.values())
            for node in outcome_nodes:
                pos[node] = (pos[node][0], min_y - 0.2)
            
            # Categorize nodes
            regular_nodes = [node for node in self.nx_graph.nodes() 
                           if not node.startswith("Outcome:") and node != "Call Start"]
            outcome_nodes = [node for node in self.nx_graph.nodes() 
                           if node.startswith("Outcome:")]
            start_nodes = ["Call Start"]
            
            # Draw nodes with different shapes and colors
            # Square for Call Start
            nx.draw_networkx_nodes(self.nx_graph, pos,
                                 nodelist=start_nodes,
                                 node_color='lightgray',
                                 node_size=7000,  # Increased size
                                 node_shape='s')  # Square shape
            
            # Circles for questions
            nx.draw_networkx_nodes(self.nx_graph, pos, 
                                 nodelist=regular_nodes,
                                 node_color='lightblue',
                                 node_size=7000,  # Increased size
                                 node_shape='o')  # Circle shape
            
            # Diamonds for outcomes
            nx.draw_networkx_nodes(self.nx_graph, pos,
                                 nodelist=outcome_nodes,
                                 node_color='lightgreen',
                                 node_size=7000,  # Increased size
                                 node_shape='d')  # Diamond shape
            
            # Draw edges with more prominent arrows
            nx.draw_networkx_edges(self.nx_graph, pos,
                                 arrows=True,
                                 arrowsize=30,  # Increased arrow size
                                 edge_color='gray',
                                 width=3,       # Increased edge width
                                 arrowstyle='->',  # Explicit arrow style
                                 connectionstyle='arc3,rad=0.1')  # Slightly curved edges
            
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