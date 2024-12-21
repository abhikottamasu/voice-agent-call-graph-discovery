import requests
import time
import json
from deepgram import Deepgram
import asyncio
from typing import Dict, List, Any
import networkx as nx
import matplotlib.pyplot as plt

class VoiceAgentDiscovery:
    def __init__(self):
        self.API_BASE = "https://app.hamming.ai/api/rest/exercise"
        self.API_TOKEN = "sk-2629df12b920117989d58f6ab10ee710"
        self.DEEPGRAM_API_KEY = "YOUR_DEEPGRAM_API_KEY"
        self.discovered_scenarios = set()
        self.conversation_graph = {}
        self.WEBHOOK_URL = "http://your-domain:5000/webhook"  # Update with your actual domain
        self.nx_graph = nx.DiGraph()

    async def transcribe_audio(self, audio_file):
        dg = Deepgram(self.DEEPGRAM_API_KEY)
        
        with open(audio_file, 'rb') as audio:
            source = {'buffer': audio, 'mimetype': 'audio/wav'}
            response = await dg.transcription.prerecorded(source, {'punctuate': True})
            return response['results']['channels'][0]['alternatives'][0]['transcript']

    def start_call(self, phone_number, prompt):
        headers = {
            "Authorization": f"Bearer {self.API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "phone_number": phone_number,
            "prompt": prompt,
            "webhook_url": self.WEBHOOK_URL
        }

        response = requests.post(
            f"{self.API_BASE}/start-call",
            headers=headers,
            json=payload
        )
        return response.json()

    def get_recording(self, call_id):
        response = requests.get(
            f"https://app.hamming.ai/media/exercise?id={call_id}",
            headers={"Authorization": f"Bearer {self.API_TOKEN}"}
        )
        
        # Save audio file temporarily
        with open(f"temp_{call_id}.wav", "wb") as f:
            f.write(response.content)
        return f"temp_{call_id}.wav"

    def analyze_conversation(self, transcript):
        # Here we would implement logic to analyze the conversation
        # and identify decision points, paths, and outcomes
        pass

    def discover_scenarios(self, phone_number: str, initial_prompt: str) -> None:
        scenarios_to_explore = [(initial_prompt, [])]
        
        while scenarios_to_explore:
            current_prompt, path = scenarios_to_explore.pop(0)
            
            # Start call and get transcript
            call_response = self.start_call(phone_number, current_prompt)
            call_id = call_response['id']
            
            # Wait for recording to be available
            time.sleep(10)  # Adjust based on actual call duration
            
            # Get and transcribe recording
            audio_file = self.get_recording(call_id)
            transcript = asyncio.run(self.transcribe_audio(audio_file))
            
            # Analyze conversation
            new_scenarios, outcome = self.analyze_conversation(transcript)
            
            # Track this conversation path
            current_path = path + [current_prompt]
            self.track_scenario(current_path, outcome)
            
            # Add new scenarios to explore
            for scenario in new_scenarios:
                if scenario not in self.discovered_scenarios:
                    self.discovered_scenarios.add(scenario)
                    scenarios_to_explore.append((scenario, current_path))
        
        # After discovery is complete, export the graph
        self.export_graph('visual')

    def track_scenario(self, path: List[str], outcome: str) -> None:
        """
        Tracks a conversation scenario by adding it to the graph structure.
        
        Args:
            path: List of conversation steps (e.g., ["initial greeting", "ask about service", "schedule appointment"])
            outcome: The final result of this conversation path
        """
        # Start at the root of the conversation graph
        current_node = self.conversation_graph
        previous_step = None

        # Build the nested dictionary structure
        for step in path:
            if step not in current_node:
                current_node[step] = {}
            
            # Add to networkx graph for visualization
            self.nx_graph.add_node(step)
            if previous_step:
                self.nx_graph.add_edge(previous_step, step)
            
            previous_step = step
            current_node = current_node[step]
        
        # Add the outcome
        current_node['outcome'] = outcome
        if previous_step:
            self.nx_graph.add_edge(previous_step, f"Outcome: {outcome}")

    def export_graph(self, format: str = 'json') -> Any:
        """
        Exports the conversation graph in the specified format.
        
        Args:
            format: 'json' or 'visual' for different output types
        
        Returns:
            Either a JSON string or saves a visualization file
        """
        if format == 'json':
            return json.dumps(self.conversation_graph, indent=2)
        
        elif format == 'visual':
            # Create visualization using networkx
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