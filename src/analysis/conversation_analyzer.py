from openai import OpenAI
from typing import Tuple, List
import json

class ConversationAnalyzer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def analyze(self, transcript: str) -> Tuple[List[str], str]:
        system_prompt = """
        You are an expert in analyzing customer service conversations...
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze this conversation transcript:\n\n{transcript}"}
                ],
                response_format={ "type": "json_object" }
            )

            analysis = json.loads(response.choices[0].message.content)
            new_scenarios = [
                path["new_scenario"] 
                for path in analysis["alternative_paths"]
            ]

            return new_scenarios, analysis["outcome"]

        except Exception as e:
            print(f"Error analyzing conversation: {str(e)}")
            return [], "error_analyzing_conversation"

    def generate_prompt(self, scenario: str) -> str:
        system_prompt = """
        Given a scenario for a customer service conversation...
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": scenario}
                ],
                response_format={ "type": "json_object" }
            )

            prompt_data = json.loads(response.choices[0].message.content)
            return prompt_data["prompt"]
        except Exception as e:
            return scenario 