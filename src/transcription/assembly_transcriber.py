from abc import ABC, abstractmethod
import assemblyai as aai
from pathlib import Path
import time

class BaseTranscriber(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        pass

class AssemblyTranscriber(BaseTranscriber):
    def __init__(self, api_key):
        aai.settings.api_key = api_key
        self.client = aai.Transcriber()

    def transcribe(self, audio_file_path):
        try:
            # Create an AudioFile object
            audio = aai.AudioFile(audio_file_path)
            
            # Transcribe the local file
            transcript = audio.transcribe()
            
            # Wait for completion
            if transcript.status == aai.TranscriptStatus.error:
                print(transcript.error)
            else:
                return transcript.text
            
        except Exception as e:
            print(f"Detailed error: {str(e)}")
            raise

    def _format_transcript(self, transcript) -> str:
        formatted_transcript = ""
        for utterance in transcript.utterances:
            speaker = "Agent" if utterance.speaker == "A" else "Customer"
            formatted_transcript += f"{speaker}: {utterance.text}\n"
        return formatted_transcript 