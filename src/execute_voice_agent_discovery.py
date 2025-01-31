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
    API keys and tokens are loaded from environment variables (.env file)
"""

from voice_agent_discovery import VoiceAgentDiscovery
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

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
    # Load configuration from environment variables
    config = {
        'assembly_api_key': os.getenv('ASSEMBLY_API_KEY'),
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'hamming_api_token': os.getenv('HAMMING_API_TOKEN'),
        'hamming_base_url': os.getenv('HAMMING_BASE_URL')
    }

    # Validate all required environment variables are present
    missing_vars = [key for key, value in config.items() if not value]
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            "Please ensure all required variables are set in your .env file."
        )

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
