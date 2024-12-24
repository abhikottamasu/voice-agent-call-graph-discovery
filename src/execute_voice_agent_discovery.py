"""
Voice Agent Discovery Execution Script

This script serves as the entry point for running the voice agent discovery process.
It configures and executes automated calls to test various customer service scenarios.

Configuration:
    - OpenAI API key for conversation analysis
    - Hamming API credentials for making calls
    - AssemblyAI API key for transcription
    - Target phone numbers for testing

Note:
    API keys and tokens should be moved to environment variables or a secure
    configuration management system in a production environment.
"""

from voice_agent_discovery import VoiceAgentDiscovery

OPENAI_API_KEY = '''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'''
HAMMING_API_TOKEN = 'sk-2629df12b920117989d58f6ab10ee710'
HAMMING_BASE_URL = 'https://app.hamming.ai/api/'
ASSEMBLY_API_KEY = '5ae53e90d6ec454bb29a32e83555d153'

def main():
    """
    Main execution function for voice agent discovery.

    Sets up the configuration and initiates the discovery process for a
    specific phone number and initial scenario.

    Configuration includes:
        - assembly_api_key: For transcription services
        - openai_api_key: For conversation analysis
        - hamming_api_token: For making calls
        - hamming_base_url: Base URL for Hamming API

    Example:
        >>> python execute_voice_agent_discovery.py
    
    Note:
        Currently configured for testing with:
        1. AC and Plumbing service (+14153580761)
        2. Auto Dealership (+16508798564)
    """
    config = {
        'assembly_api_key': ASSEMBLY_API_KEY,
        'openai_api_key': OPENAI_API_KEY,
        'hamming_api_token': HAMMING_API_TOKEN,
        'hamming_base_url': HAMMING_BASE_URL
    }

    discovery = VoiceAgentDiscovery(config)
    
    phone_numbers = [
        ("+14153580761", "Customer calling to report an issue with their AC"),  # AC and Plumbing
        ("+16508798564", "Customer calling to buy a new car")   # Auto Dealership
    ]
    phone_number_to_call = phone_numbers[1][0]
    input_scenario = phone_numbers[1][1]

    discovery.discover_scenarios(
        phone_number_to_call,
        input_scenario
    )

if __name__ == "__main__":
    main()
