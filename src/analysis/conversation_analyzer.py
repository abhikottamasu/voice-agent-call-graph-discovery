import json

from openai import OpenAI
from typing import Tuple, List

class ConversationAnalyzer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def analyze(self, transcript: str) -> Tuple[List[dict[str, str]], str]:
        messages = [
            {
                "role": "system",
                "content": """You are an expert in analyzing call conversations between a customer and a customer service agent to identify the questions asked by the agent and the answers given by the customer. Your task is to:
                    1. Identify the key questions asked by the agent and the answers given by the customer.
                    2. When creating the list of question-answer pairs, create the list in the order of the conversation.
                    3. When creating the key and values for the question-answer pairs, use values that are concise.
                    4. When creating the outcome, use the outcome of the conversation given the specific transcript. The outcome could be 'transfer to an agent', 'cannot help you' or any other terminal state.
                    5. Make sure to make the outcome a concise string that can be used as a key to compare to the outcomes of other calls. 
                    
                    Respond in the following fixed JSON format:
                    {
                        "question_answer_pairs": [
                            {<Sample Question>: <Sample Answer>},
                            {<Sample Question>: <Sample Answer>}
                        ],
                        "outcome": "<Outcome Key>"
                    }
                """
            },
            {
                "role": "user",
                "content": f"""Given the following transcript of a customer service call:
                    {transcript}

                    Analyze the conversation and:
                    1. Identify the key question-answer pairs
                    2. Identify the outcome of the conversation
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
        question_answers = json_response["question_answer_pairs"]
        outcome = json_response["outcome"]
        return question_answers, outcome

    def generate_scenarios(self, question_answers: List[dict[str, str]]) -> List[str]:
        messages = [
            {
                "role": "system",
                "content": """You are an expert in generating new variants of scenarios from a list of question-answer pairs. Your task is to:
                    1. Understand the question-answer pairs.
                    2. Modify the question-answer pairs to create new variants of the scenario.
                    3. Return a list of new variants of the scenario in the same format as the input.
                """
            }
        ]

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        new_scenarios = response.choices[0].message.content
        print(new_scenarios)
        return new_scenarios

    def generate_prompt(self, question_answers: List[dict[str, str]]) -> str:
        # Convert question-answer pairs into a formatted string
        qa_instructions = "\nPre-defined responses:"
        for qa_dict in question_answers:
            for question, answer in qa_dict.items():
                qa_instructions += f"\n- When asked '{question}' or something similar, respond with: '{answer}'"
        
        prompt = f"""When speaking with the agent:
- DO NOT interrupt the agent and only answer when the agent asks a question
- If asked a question similar to the pre-defined ones above, use those responses
- If asked something different, provide a realistic response based on your character and situation
- DO NOT volunteer information unless specifically asked
- DO NOT end the conversation. ONLY the agent will end the conversation
- Express appropriate emotions based on the scenario
- Provide your personal details only when asked and feel free to make up details as long as they are consistent with the scenario

Remember:
1. Stick to the pre-defined answers when the questions match
2. For new questions, stay in character and provide realistic responses
3. Only speak when asked a question
4. Be consistent with your personal details
5. Show appropriate emotions but remain respectful"""

        return prompt