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
                "content": """You are an expert in analyzing call conversations between a customer and a customer service agent to identify their structure, decision points, and possible scenarios. Your task is to:
                    1. Identify the key decision points and their possible variables. These will be the questions that were asked by the agent.
                    2. Define each decision point and its possible values (e.g., customer status: existing or new).
                    3. Generate an exhaustive list of scenarios that would capture all potential branches of the conversation.

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
            {"role": "system", "content": """You are an expert at creating prompts that simulate realistic customer behavior.
            
            Create prompts that will make an LLM act like a customer who:
            - Has specific personal details (name, address, account numbers, etc.)
            - Speaks naturally and conversationally
            - Has realistic emotions and reactions
            - Will ONLY respond to questions from a customer service agent and will not speak unless asked
            - Has a clear backstory and context
            
            The prompt should help the LLM roleplay as a realistic customer who:
            1. Will ONLY respond to questions from a customer service agent and will not speak unless asked
            2. Has consistent personal details throughout the conversation
            3. Shows authentic emotions and concerns"""},
            
            {"role": "user", "content": f"""Create a prompt that will make an LLM act like a customer in this scenario: {scenario}
            
            Format your response to include both personal details and emotional context.
            
            Here's an example of the format:
            "You are Sarah Johnson, a customer who is facing a broken AC at their house: 123 Maple Street, Portland, OR 97201. 
            
            Use these specific details consistently in your responses:
            - Name: Sarah Johnson
            - Address: 123 Maple Street, Portland, OR 97201
            - Phone: (503) 555-0123
            - Account: #12345
            - Problem: AC is broken
            
            When speaking with the agent:
            - Will ONLY respond to questions from a customer service agent and will not speak unless asked
            - DO NOT end the conversation. ONLY the agent will end the conversation.
            - Express your concern
            - Provide your details when asked
            
            Now, create a similar prompt for the given scenario: {scenario}"""}
        ]

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content