from transcription.assembly_transcriber import AssemblyTranscriber
from analysis.conversation_analyzer import ConversationAnalyzer
from api.hamming_client import HammingClient
from graph.scenario_tracker import ScenarioTracker
from typing import Set, List, Dict, Any
import time

class VoiceAgentDiscovery:
    """
    Orchestrates the discovery of voice agent conversation scenarios.

    Coordinates multiple components to discover and analyze different conversation
    paths through automated calls, transcription, and analysis.

    Attributes:
        transcriber (AssemblyTranscriber): Handles audio transcription
        analyzer (ConversationAnalyzer): Analyzes conversations and generates scenarios
        hamming_client (HammingClient): Makes automated phone calls
        tracker (ScenarioTracker): Tracks and visualizes discovered scenarios
        discovered_scenarios (List[List[dict]]): List of unique scenarios found
        max_scenarios (int): Maximum number of scenarios to explore
        existing_questions (Set[str]): Set of known questions
        existing_outcomes (Set[str]): Set of known outcomes
    """

    def __init__(self, config: dict):
        """
        Initialize the voice agent discovery system.

        Sets up all necessary components using the provided configuration.

        Args:
            config (dict): Configuration dictionary containing:
                - assembly_api_key: For transcription service
                - openai_api_key: For conversation analysis
                - hamming_api_token: For making calls
                - hamming_base_url: Base URL for Hamming API
        """
        self.transcriber = AssemblyTranscriber(config['assembly_api_key'])
        self.analyzer = ConversationAnalyzer(config['openai_api_key'])
        self.hamming_client = HammingClient(
            config['hamming_api_token'],
            config['hamming_base_url']
        )
        self.tracker = ScenarioTracker()
        self.discovered_scenarios: List[List[dict]] = []
        self.max_scenarios = 10
        # Add tracking for questions and outcomes
        self.existing_questions: Set[str] = set()
        self.existing_outcomes: Set[str] = set()

    def discover_scenarios(self, phone_number: str, initial_prompt: str) -> None:
        """
        Execute the scenario discovery process.

        Systematically explores different conversation paths by making calls,
        analyzing responses, and generating new scenarios based on findings.

        Args:
            phone_number (str): Target phone number to call
            initial_prompt (str): Initial conversation scenario to explore

        Example:
            >>> discovery = VoiceAgentDiscovery(config)
            >>> discovery.discover_scenarios(
            ...     "+1234567890",
            ...     "Customer calling about AC issues"
            ... )

        Note:
            - Limits exploration to max_scenarios
            - Generates visual graph of discovered scenarios
            - Tracks unique questions and outcomes
            - Implements breadth-first exploration of scenarios
        """
        print(f"\nInitial prompt: {initial_prompt} \n")
        initial_prompt = self.analyzer.generate_prompt(initial_prompt, [], 
                                                     self.existing_questions, 
                                                     self.existing_outcomes)
        scenarios_to_explore = [(initial_prompt, [])]
        scenarios_explored = 0
        
        while scenarios_to_explore and scenarios_explored < self.max_scenarios:
            current_prompt, path = scenarios_to_explore.pop(0)
            print(f"\nExploring scenario {scenarios_explored + 1} of {self.max_scenarios}")
            print(f"Exploring Path: {path}")
            scenarios_explored += 1
            
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
            
            # Update existing questions and outcomes
            for qa_dict in extracted_qa_pairs:
                for question in qa_dict.keys():
                    self.existing_questions.add(question)
            self.existing_outcomes.add(outcome)
            
            # Process new scenarios with existing Q&A knowledge
            for scenario in new_scenarios:
                if scenarios_explored >= self.max_scenarios:
                    break
                    
                if not self._is_scenario_discovered(self.discovered_scenarios, scenario):
                    self.discovered_scenarios.append(scenario)
                    print(f"\nDiscovered scenario: {scenario} \n")
                    scenario_prompt = self.analyzer.generate_prompt('', scenario,
                                                                 self.existing_questions,
                                                                 self.existing_outcomes)
                    scenarios_to_explore.append((scenario_prompt, scenario))
            
            print(f"Scenarios explored: {scenarios_explored}/{self.max_scenarios}")
            self.tracker.export_graph('visual')
        
        print(f"\nExploration complete. Explored {scenarios_explored} scenarios.")
        # print(f"Discovered scenarios: {self.discovered_scenarios}")
        print(f"\nRemaining scenarios to explore: {[scenario for _, scenario in scenarios_to_explore]}")
        #print(f"Scenario Map: {self.tracker.export_graph('json')}")
        self.tracker.export_graph('visual')

    @staticmethod
    def _is_scenario_discovered(discovered_scenarios: List[List[dict]], candidate_scenario: List[dict]) -> bool:
        """
        Compare a candidate scenario with the list of discovered scenarios.

        Performs a deep comparison between scenarios to determine if the candidate
        scenario has already been discovered.

        Args:
            discovered_scenarios (List[List[dict]]): List of previously discovered scenarios
            candidate_scenario (List[dict]): New scenario to check for uniqueness

        Returns:
            bool: True if scenario already exists, False otherwise

        Example:
            >>> discovered = [[{"Q1": "A1"}, {"Q2": "A2"}]]
            >>> candidate = [{"Q1": "A1"}, {"Q2": "A2"}]
            >>> VoiceAgentDiscovery._is_scenario_discovered(discovered, candidate)
            True
        """
        # If no discovered scenarios, definitely not discovered
        if not discovered_scenarios:
            return False
        
        # Compare candidate with each discovered scenario
        for discovered in discovered_scenarios:
            if len(discovered) != len(candidate_scenario):
                continue
                
            matches = True
            for disc_dict, cand_dict in zip(discovered, candidate_scenario):
                if disc_dict.keys() != cand_dict.keys():
                    matches = False
                    break
                
                for key in disc_dict:
                    if disc_dict[key] != cand_dict[key]:
                        matches = False
                        break
                
                if not matches:
                    break
            
            if matches:
                return True
        
        return False