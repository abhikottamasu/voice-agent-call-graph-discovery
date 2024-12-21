import sys
import os
from dotenv import load_dotenv
# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.transcription.assembly_transcriber import AssemblyTranscriber

def test_transcriber():
    load_dotenv()

    # Get API key from environment
    api_key = os.getenv('ASSEMBLY_API_KEY')
    
    # Initialize transcriber
    transcriber = AssemblyTranscriber(api_key)
    
    # Path to your test audio file
    audio_file_path = "/Users/abhikottamasu/Desktop/hammingai-challenge/temp_cm4yiwcjq0186snlwmjdnen6d.wav"  # Update this path
    
    # Test transcription
    try:
        transcript = transcriber.transcribe(audio_file_path)
        print("Transcription successful!")
        print("Transcript:", transcript)
    except Exception as e:
        print("Error during transcription:", str(e))

if __name__ == "__main__":
    test_transcriber() 