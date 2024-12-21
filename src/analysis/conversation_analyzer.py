import json

from openai import OpenAI
from typing import Tuple, List

class ConversationAnalyzer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def analyze(self, transcript: str) -> Tuple[List[str], str]:
        messages = [
            {
                "role": "system",
                "content": """You are an expert in analyzing customer service conversations to identify their structure, decision points, and possible scenarios. Your task is to:
                    1. Identify the key decision points and their possible variables.
                    2. Define each variable and its possible values (e.g., customer status: existing or new).
                    3. Generate an exhaustive list of scenarios that represent all potential branches of the conversation.

                    Respond in the following fixed JSON format:
                    {
                        "definitions_of_variables": {
                            "variable_name_1": "definition_of_variable_1",
                            "variable_name_2": "definition_of_variable_2",
                            ...
                        },
                        "scenario_list": [
                            "Scenario 1: Description",
                            "Scenario 2: Description",
                            ...
                        ],
                        "outcome": "The outcome of the conversation given the specific transcript"
                    }
                """
            },
            {
                "role": "user",
                "content": f"""Given the following transcript of a customer service call:
                    {transcript}

                    Analyze the conversation and:
                    1. Identify the key decision points and their possible variables.
                    2. Define each variable and its possible values.
                    3. Generate an exhaustive list of scenarios that represent all potential branches of the conversation.
                    """
            }
        ]

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        # Extract the response content
        analysis = response.choices[0].message.content
        json_response = json.loads(analysis)
        scenarios = json_response["scenario_list"]
        outcome = json_response["outcome"]
        return scenarios, outcome

    def generate_prompt(self, scenario: str) -> str:
        messages = [
            {"role": "system", "content": "You are given a scenario that a real person is facing and you need to create a system prompt for an LLM to behave like that real person in that scenario."},
            {"role": "user", "content": f"Create a system prompt for an LLM to perform like a real person in this scenario: {scenario}."}
        ]

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )

        return response.choices[0].message.content