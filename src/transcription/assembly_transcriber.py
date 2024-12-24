from abc import ABC, abstractmethod
import assemblyai as aai
from pathlib import Path
import time
import os
import shutil

class BaseTranscriber(ABC):
    """
    Abstract base class for audio transcription services.
    
    Defines the interface that all transcriber implementations must follow.
    """
    
    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe an audio file to text.

        Args:
            audio_path (str): Path to the audio file to transcribe

        Returns:
            str: Transcribed text from the audio file

        Raises:
            NotImplementedError: Must be implemented by concrete classes
        """
        pass

class AssemblyTranscriber(BaseTranscriber):
    """
    AssemblyAI implementation of the transcription service.
    
    Handles audio transcription using the AssemblyAI API, including speaker
    diarization and transcript formatting. Maintains a local directory for
    storing formatted transcripts.

    Attributes:
        transcripts_dir (Path): Directory where formatted transcripts are stored
        client (aai.Transcriber): AssemblyAI transcription client
    """

    def __init__(self, api_key: str):
        """
        Initialize the AssemblyAI transcriber.

        Sets up the API client with speaker diarization enabled and creates
        a clean directory for storing transcripts.

        Args:
            api_key (str): AssemblyAI API key for authentication

        Note:
            This will delete and recreate the transcripts directory if it already exists
        """
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

    def transcribe(self, audio_file_path: str) -> str:
        """
        Transcribe an audio file and save the formatted transcript.

        Processes the audio file through AssemblyAI, formats the transcript
        with speaker labels, and saves it to a text file.

        Args:
            audio_file_path (str): Path to the audio file to transcribe

        Returns:
            str: Formatted transcript text with speaker labels

        Raises:
            Exception: If transcription fails or file operations fail

        Example:
            >>> transcriber = AssemblyTranscriber(api_key)
            >>> transcript = transcriber.transcribe("call_recording.wav")
            >>> print(transcript)
            Agent: Hello, how can I help you today?
            Customer: I'm calling about my AC...
        """
        try:
            transcript = self.client.transcribe(audio_file_path)
            
            if transcript.status == aai.TranscriptStatus.error:
                print(transcript.error)
                return None
            
            formatted_transcript = self._format_transcript(transcript)
            
            # Save transcript to file with metadata
            audio_filename = Path(audio_file_path).stem
            transcript_path = self.transcripts_dir / f"{audio_filename}_transcript.txt"
            
            with open(transcript_path, "w") as f:
                f.write(f"Transcript for audio file: {audio_file_path}\n")
                f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 50 + "\n\n")
                f.write(formatted_transcript)
            
            return formatted_transcript
            
        except Exception as e:
            print(f"Detailed error: {str(e)}")
            raise

    def _format_transcript(self, transcript) -> str:
        """
        Format a transcript with speaker labels.

        Converts AssemblyAI transcript format to a human-readable format
        with clear speaker labels.

        Args:
            transcript (aai.Transcript): AssemblyAI transcript object

        Returns:
            str: Formatted transcript with speaker labels

        Note:
            - Speaker 'A' is labeled as 'Agent'
            - Speaker 'B' is labeled as 'Customer'
            - Falls back to raw text if no speaker diarization is available
        """
        formatted_transcript = ""
        if not transcript.utterances:
            return transcript.text
        for utterance in transcript.utterances:
            speaker = "Agent" if utterance.speaker == "A" else "Customer"
            formatted_transcript += f"{speaker}: {utterance.text}\n"
        return formatted_transcript 