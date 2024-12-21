import networkx as nx
import matplotlib.pyplot as plt
import json
from typing import List, Any

class ScenarioTracker:
    def __init__(self):
        self.conversation_graph = {}
        self.nx_graph = nx.DiGraph()

    def track_scenario(self, path: List[str], outcome: str) -> None:
        current_node = self.conversation_graph
        previous_step = None

        for step in path:
            if step not in current_node:
                current_node[step] = {}
            
            self.nx_graph.add_node(step)
            if previous_step:
                self.nx_graph.add_edge(previous_step, step)
            
            previous_step = step
            current_node = current_node[step]
        
        current_node['outcome'] = outcome
        if previous_step:
            self.nx_graph.add_edge(previous_step, f"Outcome: {outcome}")

    def export_graph(self, format: str = 'json') -> Any:
        if format == 'json':
            return json.dumps(self.conversation_graph, indent=2)
        
        elif format == 'visual':
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(self.nx_graph)
            nx.draw(
                self.nx_graph,
                pos,
                with_labels=True,
                node_color='lightblue',
                node_size=2000,
                font_size=8,
                arrows=True
            )
            plt.savefig('conversation_graph.png')
            return 'conversation_graph.png' 