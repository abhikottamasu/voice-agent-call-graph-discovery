from transcription.assembly_transcriber import AssemblyTranscriber
from analysis.conversation_analyzer import ConversationAnalyzer
from api.hamming_client import HammingClient
from graph.scenario_tracker import ScenarioTracker
from typing import Set
import time

class VoiceAgentDiscovery:
    def __init__(self, config: dict):
        self.transcriber = AssemblyTranscriber(config['assembly_api_key'])
        self.analyzer = ConversationAnalyzer(config['openai_api_key'])
        self.hamming_client = HammingClient(
            config['hamming_api_token'],
            config['hamming_base_url']
        )
        self.tracker = ScenarioTracker()
        self.discovered_scenarios: Set[str] = set()

    def discover_scenarios(self, phone_number: str, initial_prompt: str) -> None:
        scenarios_to_explore = [(initial_prompt, [])]
        
        while scenarios_to_explore:
            current_prompt, path = scenarios_to_explore.pop(0)
            print(f"\nExploring scenario: {current_prompt}")
            
            # Start call
            call_response = self.hamming_client.start_call(
                phone_number, 
                current_prompt,
                "https://530f-2600-1700-5168-1220-f157-d417-c1-31fb.ngrok-free.app/webhook"
            )
            
            # Get audio and transcript
            audio_path = self.hamming_client.download_recording(call_response['id'])
            transcript = self.transcriber.transcribe(audio_path)
            import pdb; pdb.set_trace()
            
            # Analyze conversation
            new_scenarios, outcome = self.analyzer.analyze(transcript)
            
            # Track scenario
            current_path = path + [current_prompt]
            self.tracker.track_scenario(current_path, outcome)
            
            # Process new scenarios
            for scenario in new_scenarios:
                if scenario not in self.discovered_scenarios:
                    self.discovered_scenarios.add(scenario)
                    scenario_prompt = self.analyzer.generate_prompt(scenario)
                    scenarios_to_explore.append((scenario_prompt, current_path))
            
            print(f"Outcome: {outcome}")
            print(f"Remaining scenarios: {len(scenarios_to_explore)}")
        
        self.tracker.export_graph('visual')