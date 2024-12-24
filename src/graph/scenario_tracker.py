import networkx as nx
import matplotlib.pyplot as plt
import json
from typing import List, Any

class ScenarioTracker:
    def __init__(self):
        self.conversation_graph = {}
        self.nx_graph = nx.DiGraph()

    def track_scenario(self, path: List[dict], outcome: str) -> None:
        """
        Track a conversation scenario where nodes are questions and edges are answers.
        
        Args:
            path: List of dictionaries, each containing one question-answer pair
            outcome: The final outcome of the conversation
        """
        previous_question = None
        
        for qa_dict in path:
            for question, answer in qa_dict.items():
                # Add question as node if it doesn't exist
                if question not in self.nx_graph:
                    self.nx_graph.add_node(question)
                
                # If there's a previous question, add an edge from it to current question
                # The edge label will be the answer to the previous question
                if previous_question:
                    self.nx_graph.add_edge(
                        previous_question[0],  # previous question
                        question,              # current question
                        answer=previous_question[1]  # answer to previous question
                    )
                
                previous_question = (question, answer)
        
        # Add the final outcome
        outcome_node = f"Outcome: {outcome}"
        self.nx_graph.add_node(outcome_node)
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
            plt.figure(figsize=(15, 10))
            pos = nx.spring_layout(self.nx_graph, k=1, iterations=50)
            
            # Draw nodes
            nx.draw_networkx_nodes(
                self.nx_graph, 
                pos,
                node_color='lightblue',
                node_size=3000
            )
            
            # Draw edges
            nx.draw_networkx_edges(self.nx_graph, pos, arrows=True)
            
            # Wrap long labels
            labels = {}
            for node in self.nx_graph.nodes():
                # Split long labels into multiple lines
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
            
            # Draw labels
            nx.draw_networkx_labels(
                self.nx_graph,
                pos,
                labels=labels,
                font_size=8
            )
            
            # Draw edge labels (answers)
            edge_labels = nx.get_edge_attributes(self.nx_graph, 'answer')
            # Wrap long edge labels
            wrapped_edge_labels = {k: v if len(v) < 20 else v[:17] + '...' for k, v in edge_labels.items()}
            
            nx.draw_networkx_edge_labels(
                self.nx_graph,
                pos,
                edge_labels=wrapped_edge_labels,
                font_size=6
            )
            
            plt.savefig('conversation_graph.png', bbox_inches='tight', dpi=300)
            return 'conversation_graph.png' 