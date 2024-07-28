import httpx
from typing import List, Dict, Any


class ThreadService:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.Client(base_url=base_url, headers={"Authorization": f"Bearer {api_key}"})

    def create_user(self, name: str) -> Dict[str, Any]:
        user_data = {"name": name}
        response = self.client.post("/v1/users", json=user_data)
        response.raise_for_status()
        return response.json()

    def create_thread(self, participant_ids: List[str], meta_data: Dict[str, Any] = {}) -> Dict[str, Any]:
        thread_data = {
            "participant_ids": participant_ids,
            "meta_data": meta_data
        }
        response = self.client.post("/v1/threads", json=thread_data)
        if response.status_code != 200:
            print("Failed to create thread:")
            print("Status code:", response.status_code)
            print("Response text:", response.text)
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


if __name__ == "__main__":
    # Replace with your actual base URL and API key
    base_url = "http://localhost:8000"
    api_key = "your_api_key"

    # Initialize the client
    thread_service = ThreadService(base_url, api_key)

    # Create users
    user1 = thread_service.create_user(name="User 1")
    user2 = thread_service.create_user(name="User 2")

    # Get user IDs
    user1_id = user1["id"]
    user2_id = user2["id"]

    # Create a thread
    new_thread = thread_service.create_thread(participant_ids=[user1_id, user2_id], meta_data={"topic": "Test Thread"})

    # Retrieve the thread ID from the response
    thread_id = new_thread["id"]

    print(f"Created thread with ID: {thread_id}")

    # Optionally, retrieve the created thread to verify
    retrieved_thread = thread_service.retrieve_thread(thread_id)
    print(f"Retrieved thread: {retrieved_thread}")
