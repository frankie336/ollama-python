import httpx
from typing import List, Dict, Any, Optional

class MessageService:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.Client(base_url=base_url, headers={"Authorization": f"Bearer {api_key}"})

    def create_message(self, thread_id: str, content: List[Dict[str, Any]], role: str, sender_id: str, meta_data: Optional[Dict[str, Any]] = {}) -> Dict[str, Any]:
        message_data = {
            "thread_id": thread_id,
            "content": content,
            "role": role,
            "sender_id": sender_id,
            "meta_data": meta_data
        }
        response = self.client.post("/v1/messages", json=message_data)
        response.raise_for_status()
        return response.json()

    def retrieve_message(self, message_id: str) -> Dict[str, Any]:
        response = self.client.get(f"/v1/messages/{message_id}")
        response.raise_for_status()
        return response.json()

    def update_message(self, message_id: str, **updates) -> Dict[str, Any]:
        response = self.client.put(f"/v1/messages/{message_id}", json=updates)
        response.raise_for_status()
        return response.json()

    def list_messages(self, thread_id: str, limit: int = 20, order: str = "asc") -> List[Dict[str, Any]]:
        params = {
            "limit": limit,
            "order": order
        }
        response = self.client.get(f"/v1/threads/{thread_id}/messages", params=params)
        response.raise_for_status()
        return response.json()

    def delete_message(self, message_id: str) -> Dict[str, Any]:
        response = self.client.delete(f"/v1/messages/{message_id}")
        response.raise_for_status()
        return response.json()
