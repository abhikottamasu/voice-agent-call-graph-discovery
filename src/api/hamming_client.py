import requests
from typing import Dict

class HammingClient:
    def __init__(self, api_token: str, base_url: str):
        self.api_token = api_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

    def start_call(self, phone_number: str, prompt: str, webhook_url: str) -> Dict:
        payload = {
            "phone_number": phone_number,
            "prompt": prompt,
            "webhook_url": webhook_url
        }

        response = requests.post(
            f"{self.base_url}/start-call",
            headers=self.headers,
            json=payload
        )
        return response.json()

    def download_recording(self, call_id: str) -> str:
        response = requests.get(
            f"{self.base_url}/media/exercise?id={call_id}",
            headers=self.headers
        )
        
        audio_path = f"temp_{call_id}.wav"
        with open(audio_path, "wb") as f:
            f.write(response.content)
        
        return audio_path 