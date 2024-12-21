from voice_agent_discovery import VoiceAgentDiscovery

OPENAI_API_KEY = '''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'''
HAMMING_API_TOKEN = 'sk-2629df12b920117989d58f6ab10ee710'
HAMMING_BASE_URL = 'https://app.hamming.ai/api/'
ASSEMBLY_API_KEY = '5ae53e90d6ec454bb29a32e83555d153'

def main():
    config = {
        'assembly_api_key': ASSEMBLY_API_KEY,
        'openai_api_key': OPENAI_API_KEY,
        'hamming_api_token': HAMMING_API_TOKEN,
        'hamming_base_url': HAMMING_BASE_URL
    }

    discovery = VoiceAgentDiscovery(config)
    
    phone_numbers = [
        "+14153580761",  # AC and Plumbing
        "+16508798564"   # Auto Dealership
    ]

    for phone in phone_numbers:
        discovery.discover_scenarios(phone, "Customer calling to report an issue with their AC")

if __name__ == "__main__":
    main()
