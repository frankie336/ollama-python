import httpx
from typing import List, Dict, Any, Optional


class AssistantService:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.Client(base_url=base_url, headers={"Authorization": f"Bearer {api_key}"})

    def create_assistant(self, name: str, description: str, model: str, instructions: str, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        assistant_data = {
            "name": name,
            "description": description,
            "model": model,
            "instructions": instructions,
            "tools": tools,
            "meta_data": {},
            "top_p": 1.0,
            "temperature": 1.0,
            "response_format": "auto"
        }
        response = self.client.post("/v1/assistants", json=assistant_data)
        response.raise_for_status()
        return response.json()

    def retrieve_assistant(self, assistant_id: str) -> Dict[str, Any]:
        response = self.client.get(f"/v1/assistants/{assistant_id}")
        response.raise_for_status()
        return response.json()

    def update_assistant(self, assistant_id: str, **updates) -> Dict[str, Any]:
        response = self.client.put(f"/v1/assistants/{assistant_id}", json=updates)
        response.raise_for_status()
        return response.json()

    def list_assistants(self, limit: int = 20, order: str = "asc") -> List[Dict[str, Any]]:
        params = {
            "limit": limit,
            "order": order
        }
        response = self.client.get("/v1/assistants", params=params)
        response.raise_for_status()
        return response.json()

    def delete_assistant(self, assistant_id: str) -> Dict[str, Any]:
        response = self.client.delete(f"/v1/assistants/{assistant_id}")
        response.raise_for_status()
        return response.json()
