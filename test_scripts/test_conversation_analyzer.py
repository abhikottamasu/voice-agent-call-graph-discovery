import os
from pathlib import Path
from dotenv import load_dotenv
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.analysis.conversation_analyzer import ConversationAnalyzer

def analyze_transcript(transcript_name):
    # Load environment variables
    load_dotenv()
    
    # Initialize analyzer
    analyzer = ConversationAnalyzer(os.getenv('OPENAI_API_KEY'))
    
    # Construct path to transcript
    transcript_path = Path("transcripts") / transcript_name
    
    if not transcript_path.exists():
        print(f"Error: Transcript not found at {transcript_path}")
        return
    
    print(f"\nAnalyzing transcript: {transcript_name}")
    
    try:
        # Read the transcript
        with open(transcript_path, 'r') as f:
            # Skip the header lines (first 4 lines)
            lines = f.readlines()[4:]
            transcript_content = ''.join(lines)
        
        # Analyze the transcript
        scenarios, outcome = analyzer.analyze(transcript_content)
        
        print("\nAnalysis Results:")
        print("Scenarios discovered:", scenarios)
        print("Outcome:", outcome)
        
        # Test prompt generation for each scenario
        print("\nGenerated Prompts:")
        for scenario in scenarios:
            prompt = analyzer.generate_prompt(scenario)
            print(f"\nScenario: {scenario}")
            print(f"Generated Prompt: {prompt}")
            
    except Exception as e:
        print(f"Error processing transcript: {str(e)}")

if __name__ == "__main__":
    transcript_name = "temp_cm4ynuqxu01c3snlw0gznwvil_transcript.txt"
    analyze_transcript(transcript_name) 