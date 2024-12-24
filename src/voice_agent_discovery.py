from transcription.assembly_transcriber import AssemblyTranscriber
from analysis.conversation_analyzer import ConversationAnalyzer
from api.hamming_client import HammingClient
from graph.scenario_tracker import ScenarioTracker
from typing import Set, List, Dict, Any
import time

def is_scenario_discovered(discovered_scenarios: List[List[dict]], candidate_scenario: List[dict]) -> bool:
    """
    Compare a candidate scenario with the list of discovered scenarios.
    Returns True if the candidate matches any existing scenario exactly.
    
    Args:
        discovered_scenarios: List of previously discovered scenarios
        candidate_scenario: New scenario to check
        
    Returns:
        bool: True if scenario already exists, False otherwise
    """
    # If no discovered scenarios, definitely not discovered
    if not discovered_scenarios:
        return False
    
    # Compare candidate with each discovered scenario
    for discovered in discovered_scenarios:
        # First check length
        if len(discovered) != len(candidate_scenario):
            continue
            
        # Check each dictionary in the list matches exactly
        matches = True
        for disc_dict, cand_dict in zip(discovered, candidate_scenario):
            # Compare keys and values
            if disc_dict.keys() != cand_dict.keys():
                matches = False
                break
            
            # Compare values for each key
            for key in disc_dict:
                if disc_dict[key] != cand_dict[key]:
                    matches = False
                    break
            
            if not matches:
                break
        
        # If we found a match, return True
        if matches:
            return True
    
    # No matches found
    return False

class VoiceAgentDiscovery:
    def __init__(self, config: dict):
        self.transcriber = AssemblyTranscriber(config['assembly_api_key'])
        self.analyzer = ConversationAnalyzer(config['openai_api_key'])
        self.hamming_client = HammingClient(
            config['hamming_api_token'],
            config['hamming_base_url']
        )
        self.tracker = ScenarioTracker()
        self.discovered_scenarios: List[List[dict]] = []

    def discover_scenarios(self, phone_number: str, initial_prompt: str) -> None:
        initial_prompt = self.analyzer.generate_prompt(initial_prompt, [])
        print(f"\nInitial prompt: {initial_prompt} \n")
        scenarios_to_explore = [(initial_prompt, [])]
        
        while scenarios_to_explore:
            current_prompt, path = scenarios_to_explore.pop(0)
            print(f"\nExploring scenario: {current_prompt} \n")
            
            # Start call
            call_response = self.hamming_client.start_call(
                phone_number, 
                current_prompt,
                "https://12b1-2600-1700-5168-1220-f157-d417-c1-31fb.ngrok-free.app/webhook"
            )
            
            print("Call started, waiting for completion...")
            time.sleep(45)
            
            try:
                audio_path = self.hamming_client.download_recording(call_response['id'])
                transcript = self.transcriber.transcribe(audio_path)
            except Exception as e:
                print(f"Error in call processing: {str(e)}")
                return
            
            # Analyze conversation
            print(f"\n Analyzing transcript: {transcript} \n")
            extracted_scenarios, outcome = self.analyzer.analyze(transcript)
            new_scenarios = self.analyzer.generate_scenarios(extracted_scenarios)
            
            # Track scenario
            current_path = path + [current_prompt]
            self.tracker.track_scenario(current_path, outcome)
            
            for scenario in new_scenarios:
                if not is_scenario_discovered(self.discovered_scenarios, scenario):
                    self.discovered_scenarios.append(scenario)
                    print(f"\n Discovered scenario: {scenario} \n")
                    scenario_prompt = self.analyzer.generate_prompt('', scenario)
                    scenarios_to_explore.append((scenario_prompt, current_path))
            
            print(f"Outcome: {outcome}")
            print(f"Remaining scenarios: {len(scenarios_to_explore)}")
        
        self.tracker.export_graph('visual')