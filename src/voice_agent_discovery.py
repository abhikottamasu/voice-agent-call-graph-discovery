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
        self.max_scenarios = 10  # Maximum number of scenarios to explore

    def discover_scenarios(self, phone_number: str, initial_prompt: str) -> None:
        # Initialize with empty question-answer pairs for first prompt
        print(f"\nInitial prompt: {initial_prompt}")
        initial_prompt = self.analyzer.generate_prompt(initial_prompt, [])
        scenarios_to_explore = [(initial_prompt, [])]  # [] represents empty Q&A path
        scenarios_explored = 0  # Counter for explored scenarios
        
        while scenarios_to_explore and scenarios_explored < self.max_scenarios:
            current_prompt, path = scenarios_to_explore.pop(0)
            scenarios_explored += 1  # Increment counter
            print(f"\nExploring scenario {scenarios_explored} of {self.max_scenarios}")
            print(f"Exploring Path: {path}")
            
            # Start call
            call_response = self.hamming_client.start_call(
                phone_number, 
                current_prompt,
                "https://45de-2600-1700-5168-1220-f157-d417-c1-31fb.ngrok-free.app/webhook"
            )
            
            print("\nCall started, waiting for completion...")
            time.sleep(45)
            
            try:
                audio_path = self.hamming_client.download_recording(call_response['id'])
                transcript = self.transcriber.transcribe(audio_path)
            except Exception as e:
                print(f"Error in call processing: {str(e)}")
                return
            
            # Analyze conversation
            print(f"\nAnalyzing transcript: {transcript} \n")
            extracted_qa_pairs, outcome = self.analyzer.analyze(transcript)
            new_scenarios = self.analyzer.generate_scenarios(extracted_qa_pairs)
            
            # Track scenario with question-answer pairs
            current_qa_path = extracted_qa_pairs
            self.tracker.track_scenario(current_qa_path, outcome)
            print(f"QA Path {scenarios_explored}: {current_qa_path}")
            print(f"Outcome: {outcome}")
            
            # Process new scenarios
            for scenario in new_scenarios:
                if scenarios_explored >= self.max_scenarios:
                    break  # Stop adpathding new scenarios if we've hit the limit
                    
                # TODO: Use LLM to check if the scenario is already discovered
                if not is_scenario_discovered(self.discovered_scenarios, scenario):
                    self.discovered_scenarios.append(scenario)
                    print(f"\nDiscovered scenario: {scenario} \n")
                    scenario_prompt = self.analyzer.generate_prompt('', scenario)
                    scenarios_to_explore.append((scenario_prompt, scenario))
            
            print(f"Scenarios explored: {scenarios_explored}/{self.max_scenarios}")
            self.tracker.export_graph('visual')
        
        print(f"\nExploration complete. Explored {scenarios_explored} scenarios.")
        # print(f"Discovered scenarios: {self.discovered_scenarios}")
        print(f"\nRemaining scenarios to explore: {[scenario for _, scenario in scenarios_to_explore]}")
        #print(f"Scenario Map: {self.tracker.export_graph('json')}")
        self.tracker.export_graph('visual')