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
                    3. When creating the key and values for the question-answer pairs, use values that are concise and crisp. For example, if the answer was 'No, it's not an emergency', the key should be 'No'.
                    4. When creating the outcome, use the outcome of the conversation given the specific transcript. The outcome could be 'transfer to an agent', 'cannot help you' or any other terminal state.
                    5. Make sure to make the outcome a concise string that can be used as a key to compare to the outcomes of other calls. 
                    
                    Here are a few examples:

                    "Are you an existing customer? Yes I am an existing customer. Is this an emergency? No, it's not really an emergency but I am uncomfortable. Okay an agent will call you back." -->
                    {
                        "question_answer_pairs": [
                            {"Are you an existing customer?": "Yes"},
                            {"Is this an emergency": "No"}
                        ],
                        "outcome": "agent_callback"
                    }

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
        print(question_answers)
        print(outcome)
        return question_answers, outcome

    def generate_scenarios(self, question_answers: List[dict[str, str]]) -> List[str]:
        messages = [
            {
                "role": "system",
                "content": """You will receive a scenario of a customer service call in the form of a list of question-answer pairs. Your task is to:
                    1. Understand the question-answer pairs and create a new scenario with slight modifications to the question answer pairs
                    2. Each new scenario should only be a slight modification to the existing scenario.
                    3. In order to create a new scenario, you will keep the same question and change the answer to something different but relevant to the scenario. If the answer is a binary, you want to flip the answer to the opposite.
                    4. Return a list of new variants of the scenario in the same format as the input.
                    5. REMEMBER to keep the same question and change the answer. Also the answers have to be relevant to the situation that you can understand by reading the input question-answer pairs.
                
                IMPORTANT: Use double quotes for all strings in your JSON response.
                
                Respond in the following fixed JSON format:
                {
                    "new_scenarios": [
                        [{"Sample Question": "Sample Answer"}, {"Sample Question": "Sample Answer"}],
                        [{"Sample Question": "Sample Answer"}, {"Sample Question": "Sample Answer"}]
                    ]
                }
                """
            },
            {
                "role": "user",
                "content": f"Here is the list of question-answer pairs:\n{question_answers}"
            }
        ]

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        new_scenarios = response.choices[0].message.content
        
        # Replace single quotes with double quotes to make it valid JSON
        new_scenarios = new_scenarios.replace("'", '"')
        
        try:
            json_response = json.loads(new_scenarios)
            return json_response["new_scenarios"]
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print(f"Raw response: {new_scenarios}")
            return []

    def generate_prompt(self, scenario, question_answers) -> str:
        # Convert question-answer pairs into a formatted string
        qa_instructions = "\nPre-defined responses:"
        for qa_dict in question_answers:
            for question, answer in qa_dict.items():
                qa_instructions += f"\n- When asked '{question}' or something similar, respond with: '{answer}'"
        
        prompt = f"""
        {scenario}
        
        {qa_instructions}
        
        When speaking with the agent:
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