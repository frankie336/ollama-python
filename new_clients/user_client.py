import httpx
from typing import Dict, Any


class UserService:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.Client(base_url=base_url, headers={"Authorization": f"Bearer {api_key}"})

    def create_user(self, name: str) -> Dict[str, Any]:
        user_data = {
            "name": name
        }
        response = self.client.post("/v1/users", json=user_data)
        response.raise_for_status()
        return response.json()
