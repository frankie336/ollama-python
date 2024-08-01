import httpx
from typing import List, Dict, Any, Optional
from services.loggin_service import LoggingUtility

# Initialize logging utility
logging_utility = LoggingUtility()


class ThreadService:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.Client(base_url=base_url, headers={"Authorization": f"Bearer {api_key}"})
        logging_utility.info("ThreadService initialized with base_url: %s", self.base_url)

    def create_user(self, name: str) -> Dict[str, Any]:
        logging_utility.info("Creating user with name: %s", name)
        user_data = {"name": name}
        try:
            response = self.client.post("/v1/users", json=user_data)
            response.raise_for_status()
            created_user = response.json()
            logging_utility.info("User created successfully with id: %s", created_user.get('id'))
            return created_user
        except httpx.HTTPStatusError as e:
            logging_utility.error("HTTP error occurred while creating user: %s", str(e))
            raise
        except Exception as e:
            logging_utility.error("An error occurred while creating user: %s", str(e))
            raise

    def create_thread(self, participant_ids: Optional[List[str]] = None, meta_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if participant_ids is None:
            participant_ids = []
        if meta_data is None:
            meta_data = {}

        thread_data = {
            "participant_ids": participant_ids,
            "meta_data": meta_data
        }
        logging_utility.info("Creating thread with %d participants", len(participant_ids))
        try:
            response = self.client.post("/v1/threads", json=thread_data)
            response.raise_for_status()
            created_thread = response.json()
            logging_utility.info("Thread created successfully with id: %s", created_thread.get('id'))
            return created_thread
        except httpx.HTTPStatusError as e:
            logging_utility.error("HTTP error occurred while creating thread: %s", str(e))
            logging_utility.error("Status code: %d, Response text: %s", e.response.status_code, e.response.text)
            raise
        except Exception as e:
            logging_utility.error("An error occurred while creating thread: %s", str(e))
            raise

    def retrieve_thread(self, thread_id: str) -> Dict[str, Any]:
        logging_utility.info("Retrieving thread with id: %s", thread_id)
        try:
            response = self.client.get(f"/v1/threads/{thread_id}")
            response.raise_for_status()
            thread = response.json()
            logging_utility.info("Thread retrieved successfully")
            return thread
        except httpx.HTTPStatusError as e:
            logging_utility.error("HTTP error occurred while retrieving thread: %s", str(e))
            raise
        except Exception as e:
            logging_utility.error("An error occurred while retrieving thread: %s", str(e))
            raise

    def update_thread(self, thread_id: str, **updates) -> Dict[str, Any]:
        logging_utility.info("Updating thread with id: %s", thread_id)
        try:
            response = self.client.put(f"/v1/threads/{thread_id}", json=updates)
            response.raise_for_status()
            updated_thread = response.json()
            logging_utility.info("Thread updated successfully")
            return updated_thread
        except httpx.HTTPStatusError as e:
            logging_utility.error("HTTP error occurred while updating thread: %s", str(e))
            raise
        except Exception as e:
            logging_utility.error("An error occurred while updating thread: %s", str(e))
            raise

    def list_threads(self, limit: int = 20, order: str = "asc") -> List[Dict[str, Any]]:
        logging_utility.info("Listing threads with limit: %d, order: %s", limit, order)
        params = {
            "limit": limit,
            "order": order
        }
        try:
            response = self.client.get("/v1/threads", params=params)
            response.raise_for_status()
            threads = response.json()
            logging_utility.info("Retrieved %d threads", len(threads))
            return threads
        except httpx.HTTPStatusError as e:
            logging_utility.error("HTTP error occurred while listing threads: %s", str(e))
            raise
        except Exception as e:
            logging_utility.error("An error occurred while listing threads: %s", str(e))
            raise

    def delete_thread(self, thread_id: str) -> Dict[str, Any]:
        logging_utility.info("Deleting thread with id: %s", thread_id)
        try:
            response = self.client.delete(f"/v1/threads/{thread_id}")
            response.raise_for_status()
            result = response.json()
            logging_utility.info("Thread deleted successfully")
            return result
        except httpx.HTTPStatusError as e:
            logging_utility.error("HTTP error occurred while deleting thread: %s", str(e))
            raise
        except Exception as e:
            logging_utility.error("An error occurred while deleting thread: %s", str(e))
            raise

if __name__ == "__main__":
    # Replace with your actual base URL and API key
    base_url = "http://localhost:8000"
    api_key = "your_api_key"

    logging_utility.info("Starting ThreadService test")

    # Initialize the client
    thread_service = ThreadService(base_url, api_key)

    try:
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

        logging_utility.info("Created thread with ID: %s", thread_id)

        # Optionally, retrieve the created thread to verify
        retrieved_thread = thread_service.retrieve_thread(thread_id)
        logging_utility.info("Retrieved thread: %s", retrieved_thread)

    except Exception as e:
        logging_utility.error("An error occurred during ThreadService test: %s", str(e))