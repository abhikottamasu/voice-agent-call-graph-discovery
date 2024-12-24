import json

from openai import OpenAI
from typing import Tuple, List, Set

class ConversationAnalyzer:
    """
    A class for analyzing customer service call transcripts and generating conversation scenarios.
    
    This analyzer uses OpenAI's GPT models to extract question-answer pairs, identify conversation
    outcomes, and generate new conversation scenarios based on existing patterns.
    """

    def __init__(self, api_key: str):
        """
        Initialize the ConversationAnalyzer with OpenAI API credentials.

        Args:
            api_key (str): OpenAI API key for authentication
        """
        self.client = OpenAI(api_key=api_key)

    def analyze(self, transcript: str) -> Tuple[List[dict[str, str]], str]:
        """
        Analyze a call transcript to extract question-answer pairs and conversation outcome.

        This method processes the transcript to identify key interactions between agent and customer,
        standardizing questions and answers into a consistent format.

        Args:
            transcript (str): The text transcript of the customer service call

        Returns:
            Tuple[List[dict[str, str]], str]: A tuple containing:
                - List of dictionaries, each containing one question-answer pair
                - String representing the conversation outcome

        Example:
            >>> analyzer = ConversationAnalyzer(api_key)
            >>> qa_pairs, outcome = analyzer.analyze("Are you an existing customer? Yes...")
            >>> print(qa_pairs)
            [{"Are you an existing customer?": "Yes"}]
            >>> print(outcome)
            "agent_callback"
        """
        messages = [
            {
                "role": "system",
                "content": """You are an expert in analyzing call conversations between a customer and a customer service agent to identify the questions asked by the agent and the answers given by the customer. Your task is to:
                    1. Identify the key questions asked by the agent and the answers given by the customer.
                    2. When creating the list of question-answer pairs, create the list in the order of the conversation.
                    3. When creating the key and values for the question-answer pairs, use values that are concise and crisp. For example, if the answer was 'No, it's not an emergency', the key should be 'No'.
                    4. In addition, if the uses gives an explanation for an answer only encode the unique key as the answer. For example, if the answer is 'my AC isn't cooling properly, it seems to be running...' only encode 'ac_issue'. Extracted answers need to be concise and key-like. 
                    5. In addition, when extracting an answer that is detail-oriented, abstract out the detail. For example, 'What is your name and address' -> 'Alex Blake, 123 New York' should encode the answer as 'name_and_address_provided' 
                    6. Same thing for questions, if the question is 'Are you an existing customer with Anthem Air Conditioning and Plumbing?', the question should be 'Are you an existing customer?'
                    7. The question that is extracted should always end in '?'
                    8. When creating the outcome, use the outcome of the conversation given the specific transcript. The outcome could be 'transfer to an agent', 'cannot help you' or any other terminal state.
                    9. Make sure to make the outcome a concise string that can be used as a key to compare to the outcomes of other calls. 
                    
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
        return question_answers, outcome

    @staticmethod
    def clean_json_string(json_str: str) -> str:
        """
        Clean and validate a JSON string for proper parsing.

        Handles various JSON formatting issues including smart quotes, escaped characters,
        and whitespace to ensure valid JSON structure.

        Args:
            json_str (str): Raw JSON string to be cleaned

        Returns:
            str: Cleaned JSON string ready for parsing

        Raises:
            None: Handles malformed JSON gracefully
        """
        import re
        
        # Remove any whitespace between the string
        json_str = json_str.strip()
        
        # Remove any newlines and extra spaces
        json_str = re.sub(r'\s+', ' ', json_str)
        
        # Handle contractions and possessives by replacing smart quotes with regular quotes
        json_str = json_str.replace('"', '"').replace('"', '"')
        
        # Replace escaped quotes with single quotes
        json_str = json_str.replace('\\"', "'")
        
        # Replace remaining double quotes that are part of contractions with single quotes
        json_str = re.sub(r'(?<=\w)"(?=\w)', "'", json_str)
        
        # Handle any remaining escaped characters
        json_str = json_str.encode().decode('unicode-escape')
        
        return json_str

    def generate_scenarios(self, question_answers: List[dict[str, str]]) -> List[str]:
        """
        Generate new conversation scenarios based on existing question-answer pairs.

        Creates variations of the original scenario by modifying answers while maintaining
        question consistency and scenario relevance.

        Args:
            question_answers (List[dict[str, str]]): List of existing question-answer pairs
                Each dictionary contains one question-answer pair

        Returns:
            List[str]: List of new scenario variations

        Example:
            >>> qa_pairs = [{"Are you an existing customer?": "Yes"}]
            >>> new_scenarios = analyzer.generate_scenarios(qa_pairs)
            >>> print(new_scenarios)
            [[{"Are you an existing customer?": "No"}]]
        """
        messages = [
            {
                "role": "system",
                "content": """You will receive a scenario of a customer service call in the form of a list of question-answer pairs. Your task is to:
                    1. Understand the question-answer pairs and create a new scenario with slight modifications to the question answer pairs
                    2. Each new scenario should only be a slight modification to the existing scenario.
                    3. In order to create a new scenario, you will keep the same question and change the answer to something different but relevant to the scenario. If the answer is a binary, you want to flip the answer to the opposite. For example, 'Are you an existing customer?': 'Yes' should be modified to 'Are you an existing customer?': 'No'
                    4. All questions should end in '?'
                    5. DO NOT modify answers to factual questions. For example, if the question is 'What is your name and address' or 'What is your account number', do not modify the answer. Maintain the same answer in new scenarios too
                    6. Return a list of new variants of the scenario in the same format as the input.
                    7. REMEMBER to keep the same question and change the answer. Also the answers have to be relevant to the situation that you can understand by reading the input question-answer pairs.
                
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
        
        try:
            cleaned_json = self.clean_json_string(new_scenarios)
            # print(f"Cleaned JSON: {cleaned_json}")  # Debug print
            
            json_response = json.loads(cleaned_json)
            return json_response["new_scenarios"]
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print(f"Raw response: {new_scenarios}")
            return []

    def generate_prompt(self, scenario: str, question_answers: List[dict[str, str]], 
                       existing_questions: Set[str], existing_outcomes: Set[str]) -> str:
        """
        Generate a conversation prompt for simulating customer responses.

        Creates a detailed prompt that guides response generation while maintaining
        consistency with existing patterns and encouraging reuse of established
        questions and outcomes.

        Args:
            scenario (str): Current conversation scenario
            question_answers (List[dict[str, str]]): Pre-defined question-answer pairs
            existing_questions (Set[str]): Set of questions from previous scenarios
            existing_outcomes (Set[str]): Set of outcomes from previous scenarios

        Returns:
            str: Formatted prompt for conversation simulation by an LLM
        """
        # Convert question-answer pairs into a formatted string
        qa_instructions = "\nPre-defined responses:"
        for qa_dict in question_answers:
            for question, answer in qa_dict.items():
                qa_instructions += f"\n- When asked '{question}' or something similar, respond with: '{answer}'"
        
        # Add context about existing questions and outcomes
        context = "\nExisting questions that have been asked in other scenarios:"
        for question in existing_questions:
            context += f"\n- {question}"
        
        context += "\n\nExisting outcomes that have occurred:"
        for outcome in existing_outcomes:
            context += f"\n- {outcome}"
        
        context += "\n\nNote: When possible, reuse existing questions and aim for existing outcomes if they fit the scenario. Only create new questions or map scenarios to new outcomes if they are distinctly different."
        
        prompt = f"""
        {scenario}
        
        {context}
        
        {qa_instructions}
        
        When speaking with the agent:
- DO NOT interrupt the agent and only answer when the agent asks a question
- Always keep your answers to just 1 sentence. NO MORE THAN 1 sentence.
- If asked a question similar to the pre-defined ones above, use those responses
- If asked something different, provide a realistic response based on your character and situation. Be detailed in your response. For example, if the question is 'What is your issue', DO NOT respond 'YES' and instead respond with something detailed like 'My AC is not cooling properly'.
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