# new_clients/assistant_client.py
import httpx
from typing import List, Dict, Any, Optional
from services.loggin_service import LoggingUtility


# Initialize logging utility
logging_utility = LoggingUtility()


class AssistantService:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.Client(base_url=base_url, headers={"Authorization": f"Bearer {api_key}"})
        logging_utility.info("AssistantService initialized with base_url: %s", self.base_url)

    def create_assistant(self, model: str, name: str = "", description: str = "", instructions: str = "",
                         tools: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        if tools is None:
            tools = []

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
        logging_utility.info("Creating assistant with model: %s, name: %s", model, name)
        try:
            response = self.client.post("/v1/assistants", json=assistant_data)
            response.raise_for_status()
            created_assistant = response.json()
            logging_utility.info("Assistant created successfully with id: %s", created_assistant.get('id'))
            return created_assistant
        except httpx.HTTPStatusError as e:
            logging_utility.error("HTTP error occurred while creating assistant: %s", str(e))
            raise
        except Exception as e:
            logging_utility.error("An error occurred while creating assistant: %s", str(e))
            raise

    def retrieve_assistant(self, assistant_id: str) -> Dict[str, Any]:
        logging_utility.info("Retrieving assistant with id: %s", assistant_id)
        try:
            response = self.client.get(f"/v1/assistants/{assistant_id}")
            response.raise_for_status()
            assistant = response.json()
            logging_utility.info("Assistant retrieved successfully")
            return assistant
        except httpx.HTTPStatusError as e:
            logging_utility.error("HTTP error occurred while retrieving assistant: %s", str(e))
            raise
        except Exception as e:
            logging_utility.error("An error occurred while retrieving assistant: %s", str(e))
            raise

    def update_assistant(self, assistant_id: str, **updates) -> Dict[str, Any]:
        logging_utility.info("Updating assistant with id: %s", assistant_id)
        try:
            response = self.client.put(f"/v1/assistants/{assistant_id}", json=updates)
            response.raise_for_status()
            updated_assistant = response.json()
            logging_utility.info("Assistant updated successfully")
            return updated_assistant
        except httpx.HTTPStatusError as e:
            logging_utility.error("HTTP error occurred while updating assistant: %s", str(e))
            raise
        except Exception as e:
            logging_utility.error("An error occurred while updating assistant: %s", str(e))
            raise

    def list_assistants(self, limit: int = 20, order: str = "asc") -> List[Dict[str, Any]]:
        logging_utility.info("Listing assistants with limit: %d, order: %s", limit, order)
        params = {
            "limit": limit,
            "order": order
        }
        try:
            response = self.client.get("/v1/assistants", params=params)
            response.raise_for_status()
            assistants = response.json()
            logging_utility.info("Retrieved %d assistants", len(assistants))
            return assistants
        except httpx.HTTPStatusError as e:
            logging_utility.error("HTTP error occurred while listing assistants: %s", str(e))
            raise
        except Exception as e:
            logging_utility.error("An error occurred while listing assistants: %s", str(e))
            raise

    def delete_assistant(self, assistant_id: str) -> Dict[str, Any]:
        logging_utility.info("Deleting assistant with id: %s", assistant_id)
        try:
            response = self.client.delete(f"/v1/assistants/{assistant_id}")
            response.raise_for_status()
            result = response.json()
            logging_utility.info("Assistant deleted successfully")
            return result
        except httpx.HTTPStatusError as e:
            logging_utility.error("HTTP error occurred while deleting assistant: %s", str(e))
            raise
        except Exception as e:
            logging_utility.error("An error occurred while deleting assistant: %s", str(e))
            raise