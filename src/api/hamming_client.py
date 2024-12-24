import requests
from typing import Dict
import os
from pathlib import Path
import time
import shutil

class HammingClient:
    def __init__(self, api_token: str, base_url: str):
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
        print(f"Downloading recording for call {call_id}...")
        
        for attempt in range(max_retries):
            response = requests.get(
                f"{self.base_url}/media/exercise?id={call_id}",
                headers=self.headers
            )
            
            # Print response info
            # print(f"Response status: {response.status_code}")
            # print(f"Content-Type: {response.headers.get('content-type')}")
            # print(f"Content-Length: {response.headers.get('content-length')} bytes")
            
            if response.status_code == 404:
                # Parse error message from JSON
                error_msg = response.json().get('error', 'Unknown error')
                print(f"Error message: {error_msg}")
                
                if attempt < max_retries - 1:
                    wait_time = 10 * (attempt + 1)  # Increase wait time with each retry
                    print(f"Recording not ready yet. Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception("Max retries reached waiting for recording")
            
            # If we got a successful response
            if response.status_code == 200:
                # Check if it's actually an audio file
                first_bytes = response.content[:12]
                if not first_bytes.startswith(b'RIFF'):
                    raise Exception("Received response is not a valid WAV file")
                
                # Save the audio file in recordings directory
                audio_path = self.recordings_dir / f"temp_{call_id}.wav"
                with open(audio_path, "wb") as f:
                    f.write(response.content)
                
                print(f"Successfully saved audio to: {audio_path}")
                return str(audio_path)  # Convert Path to string
            
            response.raise_for_status()
        
        raise Exception(f"Failed to download recording after {max_retries} attempts")