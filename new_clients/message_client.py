import json
import httpx
from typing import List, Dict, Any, Optional


class MessageService:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.Client(base_url=base_url, headers={"Authorization": f"Bearer {api_key}"})
        self.message_chunks: Dict[str, List[str]] = {}  # Temporary storage for message chunks

    def create_message(self, thread_id: str, content: str, sender_id: str, role: str = 'user',
                       meta_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if meta_data is None:
            meta_data = {}

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

    def get_formatted_messages(self, thread_id: str) -> List[Dict[str, Any]]:
        try:
            response = self.client.get(f"/v1/threads/{thread_id}/formatted_messages")
            response.raise_for_status()
            formatted_messages = response.json()

            if not isinstance(formatted_messages, list):
                raise ValueError("Expected a list of messages")

            if not formatted_messages or formatted_messages[0].get('role') != 'system':
                formatted_messages.insert(0, {
                    "role": "system",
                    "content": "Be as kind, intelligent, and helpful"
                })

            return formatted_messages
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Thread not found: {thread_id}")
            else:
                raise RuntimeError(f"HTTP error occurred: {e}")
        except Exception as e:
            raise RuntimeError(f"An error occurred: {str(e)}")

    def delete_message(self, message_id: str) -> Dict[str, Any]:
        response = self.client.delete(f"/v1/messages/{message_id}")
        response.raise_for_status()
        return response.json()

    def save_assistant_message_chunk(self, thread_id: str, content: str, is_last_chunk: bool = False) -> Optional[Dict[str, Any]]:
        message_data = {
            "thread_id": thread_id,
            "content": content,
            "role": "assistant",
            "sender_id": "assistant",
            "meta_data": {}
        }

        try:
            response = self.client.post("/v1/messages/assistant", json=message_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred while saving assistant message: {e}")
            return None
        except Exception as e:
            print(f"An error occurred while saving assistant message: {str(e)}")
            return None