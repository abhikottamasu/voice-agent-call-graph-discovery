import requests
from typing import Dict
import os
from pathlib import Path
import time
import shutil

class HammingClient:
    """
    A client for interacting with the Hamming API service.
    
    This client handles making calls, downloading recordings, and managing audio files.
    It maintains a local directory for storing downloaded recordings and provides
    retry logic for handling temporary failures.

    Attributes:
        recordings_dir (Path): Directory where downloaded recordings are stored
    """

    def __init__(self, api_token: str, base_url: str):
        """
        Initialize the Hamming API client.

        Creates a new client instance with authentication headers and sets up
        a clean recordings directory for storing downloaded audio files.

        Args:
            api_token (str): Authentication token for the Hamming API
            base_url (str): Base URL of the Hamming API service

        Note:
            This will delete and recreate the recordings directory if it already exists
        """
        self.api_token = api_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        # Create recordings directory (delete if exists)
        self.recordings_dir = Path("recordings")
        if self.recordings_dir.exists():
            shutil.rmtree(self.recordings_dir)
        self.recordings_dir.mkdir(exist_ok=True)

    def start_call(self, phone_number: str, prompt: str, webhook_url: str) -> Dict:
        """
        Initiate a new call through the Hamming API.

        Makes a POST request to start a new call with specified parameters.

        Args:
            phone_number (str): Target phone number to call
            prompt (str): Initial prompt for the conversation
            webhook_url (str): URL for receiving call status updates

        Returns:
            Dict: API response containing call details

        Example:
            >>> client = HammingClient(api_token, base_url)
            >>> response = client.start_call(
            ...     "+1234567890",
            ...     "Hello, how can I help you?",
            ...     "https://example.com/webhook"
            ... )
        """
        payload = {
            "phone_number": phone_number,
            "prompt": prompt,
            "webhook_url": webhook_url
        }

        response = requests.post(
            f"{self.base_url}/rest/exercise/start-call",
            headers=self.headers,
            json=payload
        )
        return response.json()

    def download_recording(self, call_id: str, max_retries: int = 3) -> str:
        """
        Download and save a call recording.

        Attempts to download the recording for a specific call, implementing retry logic
        for handling cases where the recording isn't immediately available.

        Args:
            call_id (str): ID of the call to download
            max_retries (int, optional): Maximum number of download attempts. Defaults to 3.

        Returns:
            str: Path to the downloaded audio file

        Raises:
            Exception: If max retries are reached or if the response isn't a valid WAV file

        Example:
            >>> client = HammingClient(api_token, base_url)
            >>> audio_path = client.download_recording("call_123")
            >>> print(f"Recording saved to: {audio_path}")

        Note:
            - Implements exponential backoff for retries
            - Validates that the downloaded content is a valid WAV file
            - Stores recordings in the recordings_dir with format: temp_{call_id}.wav
        """
        print(f"Downloading recording for call {call_id}...")
        
        for attempt in range(max_retries):
            response = requests.get(
                f"{self.base_url}/media/exercise?id={call_id}",
                headers=self.headers
            )
            
            if response.status_code == 404:
                error_msg = response.json().get('error', 'Unknown error')
                print(f"Error message: {error_msg}")
                
                if attempt < max_retries - 1:
                    wait_time = 10 * (attempt + 1)
                    print(f"Recording not ready yet. Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception("Max retries reached waiting for recording")
            
            if response.status_code == 200:
                first_bytes = response.content[:12]
                if not first_bytes.startswith(b'RIFF'):
                    raise Exception("Received response is not a valid WAV file")
                
                audio_path = self.recordings_dir / f"temp_{call_id}.wav"
                with open(audio_path, "wb") as f:
                    f.write(response.content)
                
                print(f"Successfully saved audio to: {audio_path}")
                return str(audio_path)
            
            response.raise_for_status()
        
        raise Exception(f"Failed to download recording after {max_retries} attempts")