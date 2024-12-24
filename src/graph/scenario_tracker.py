import networkx as nx
import matplotlib.pyplot as plt
import json
from typing import List, Any

class ScenarioTracker:
    def __init__(self):
        self.conversation_graph = {}
        self.nx_graph = nx.MultiDiGraph()
        self.nx_graph.add_node("Call Start")

    def track_scenario(self, path: List[dict], outcome: str) -> None:
        """
        Track a conversation scenario where nodes are questions and edges are answers.
        
        Args:
            path: List of dictionaries, each containing one question-answer pair
            outcome: The final outcome of the conversation
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
            
            # Modified edge drawing to handle multiple edges
            for edge in self.nx_graph.edges(data=True, keys=True):
                u, v, k, data = edge
                # Calculate edge offset for multiple edges between same nodes
                offset = 0.2 if k % 2 == 0 else -0.2
                
                # Draw each edge with a slight offset
                edge_pos = [(pos[u][0], pos[u][1]), (pos[v][0], pos[v][1])]
                nx.draw_networkx_edges(self.nx_graph.subgraph([u, v]),
                                     {u: (pos[u][0], pos[u][1] + offset),
                                      v: (pos[v][0], pos[v][1] + offset)},
                                     edgelist=[(u, v, k)],
                                     arrows=True,
                                     arrowsize=50,
                                     edge_color='black',
                                     width=2,
                                     arrowstyle='-|>',
                                     min_source_margin=25,
                                     min_target_margin=25)
            
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
            
            # Modified edge label drawing to handle multiple edges
            edge_labels = {}
            for u, v, k, data in self.nx_graph.edges(data=True, keys=True):
                edge_labels[(u, v, k)] = data.get('answer', '')
            
            # Draw edge labels with offsets
            for (u, v, k), label in edge_labels.items():
                offset = 0.2 if k % 2 == 0 else -0.2
                x = (pos[u][0] + pos[v][0]) / 2
                y = (pos[u][1] + pos[v][1]) / 2 + offset
                plt.text(x, y, label if len(label) < 20 else label[:17] + '...',
                        fontsize=12,
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.7),
                        horizontalalignment='center',
                        verticalalignment='center')
            
            plt.savefig('conversation_graph.png', bbox_inches='tight', dpi=300)
            return 'conversation_graph.png' 