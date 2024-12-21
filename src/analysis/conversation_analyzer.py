from openai import OpenAI
from typing import Tuple, List

class ConversationAnalyzer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def analyze(self, transcript: str) -> Tuple[List[str], str]:
        print("Analyzing transcript...")
        
        messages = [
            {"role": "system", "content": "You are an expert at analyzing customer service conversations."},
            {"role": "user", "content": f"""
                Analyze this conversation and identify:
                1. The main scenario being discussed
                2. Any potential alternative scenarios that could be explored
                3. The outcome of the conversation

                Conversation:
                {transcript}
            """}
        ]

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        # Extract the response content
        analysis = response.choices[0].message.content

        # Parse the analysis to extract scenarios and outcome
        # This is a simple implementation - you might want to make it more robust
        scenarios = []  # Extract scenarios from analysis
        outcome = "Unknown"  # Extract outcome from analysis

        return scenarios, outcome

    def generate_prompt(self, scenario: str) -> str:
        messages = [
            {"role": "system", "content": "You are an expert at creating customer service scenarios."},
            {"role": "user", "content": f"Create a natural prompt for this scenario: {scenario}"}
        ]

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )

        return response.choices[0].message.content