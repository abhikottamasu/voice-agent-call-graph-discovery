from abc import ABC, abstractmethod
import assemblyai as aai
from pathlib import Path

class BaseTranscriber(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        pass

class AssemblyTranscriber(BaseTranscriber):
    def __init__(self, api_key: str):
        self.client = aai.Client(api_key=api_key)

    def transcribe(self, audio_path: str) -> str:
        try:
            config = aai.TranscriptionConfig(
                speaker_labels=True,
                language_code="en"
            )
            
            transcript = self.client.transcribe(
                audio_path,
                config=config
            )

            while transcript.status != 'completed':
                transcript = self.client.wait_for_completion(transcript)
            
            return self._format_transcript(transcript)
        
        finally:
            Path(audio_path).unlink(missing_ok=True)

    def _format_transcript(self, transcript) -> str:
        formatted_transcript = ""
        for utterance in transcript.utterances:
            speaker = "Agent" if utterance.speaker == "A" else "Customer"
            formatted_transcript += f"{speaker}: {utterance.text}\n"
        return formatted_transcript 