import httpx
from typing import List, Dict, Any


class ThreadService:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.Client(base_url=base_url, headers={"Authorization": f"Bearer {api_key}"})

    def create_thread(self, participant_ids: List[str], meta_data: Dict[str, Any] = {}) -> Dict[str, Any]:
        thread_data = {
            "participant_ids": participant_ids,
            "meta_data": meta_data
        }
        response = self.client.post("/v1/threads", json=thread_data)
        response.raise_for_status()
        return response.json()

    def retrieve_thread(self, thread_id: str) -> Dict[str, Any]:
        response = self.client.get(f"/v1/threads/{thread_id}")
        response.raise_for_status()
        return response.json()

    def update_thread(self, thread_id: str, **updates) -> Dict[str, Any]:
        response = self.client.put(f"/v1/threads/{thread_id}", json=updates)
        response.raise_for_status()
        return response.json()

    def list_threads(self, limit: int = 20, order: str = "asc") -> List[Dict[str, Any]]:
        params = {
            "limit": limit,
            "order": order
        }
        response = self.client.get("/v1/threads", params=params)
        response.raise_for_status()
        return response.json()

    def delete_thread(self, thread_id: str) -> Dict[str, Any]:
        response = self.client.delete(f"/v1/threads/{thread_id}")
        response.raise_for_status()
        return response.json()
