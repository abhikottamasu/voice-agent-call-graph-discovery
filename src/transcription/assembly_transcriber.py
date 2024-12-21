from abc import ABC, abstractmethod
import assemblyai as aai
from pathlib import Path
import time
import os
import shutil

class BaseTranscriber(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        pass

class AssemblyTranscriber(BaseTranscriber):
    def __init__(self, api_key):
        aai.settings.api_key = api_key
        aai.TranscriptionConfig(
            speaker_labels=True,
            language_code="en"
        )
        self.client = aai.Transcriber()
        
        # Create transcripts directory (delete if exists)
        self.transcripts_dir = Path("transcripts")
        if self.transcripts_dir.exists():
            shutil.rmtree(self.transcripts_dir)
        self.transcripts_dir.mkdir(exist_ok=True)

    def transcribe(self, audio_file_path):
        try:
            transcript = self.client.transcribe(audio_file_path)
            
            if transcript.status == aai.TranscriptStatus.error:
                print(transcript.error)
                return None
            
            # Format the transcript
            formatted_transcript = self._format_transcript(transcript)
            
            # Save transcript to file
            audio_filename = Path(audio_file_path).stem  # Get filename without extension
            transcript_path = self.transcripts_dir / f"{audio_filename}_transcript.txt"
            
            with open(transcript_path, "w") as f:
                f.write(f"Transcript for audio file: {audio_file_path}\n")
                f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 50 + "\n\n")
                f.write(formatted_transcript)
            
            print(f"Transcript saved to: {transcript_path}")
            return formatted_transcript
            
        except Exception as e:
            print(f"Detailed error: {str(e)}")
            raise

    def _format_transcript(self, transcript) -> str:
        formatted_transcript = ""
        if not transcript.utterances:
            return transcript.text
        for utterance in transcript.utterances:
            speaker = "Agent" if utterance.speaker == "A" else "Customer"
            formatted_transcript += f"{speaker}: {utterance.text}\n"
        return formatted_transcript 