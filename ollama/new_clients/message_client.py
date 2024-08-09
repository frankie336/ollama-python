# new_clients/message_client.py
from typing import List, Dict, Any, Optional

import httpx
from pydantic import ValidationError

from api.v1.schemas import MessageCreate, MessageRead, MessageUpdate
from ollama.new_clients.loggin_service import LoggingUtility


# Initialize logging utility
logging_utility = LoggingUtility()


class MessageService:
    def __init__(self, base_url="http://localhost:9000/", api_key="api-key"):
        self.base_url = base_url.rstrip('/')  # Remove trailing slash if present
        self.api_key = api_key
        self.client = httpx.Client(base_url=self.base_url, headers={"Authorization": f"Bearer {api_key}"})
        self.message_chunks: Dict[str, List[str]] = {}  # Temporary storage for message chunks
        logging_utility.info("MessageService initialized with base_url: %s", self.base_url)

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

        logging_utility.info("Creating message for thread_id: %s, role: %s", thread_id, role)
        logging_utility.debug(f"Message data: {message_data}")

        try:
            validated_data = MessageCreate(**message_data)  # Validate data using Pydantic model
            url = "/v1/messages"
            logging_utility.debug(f"Sending POST request to: {self.base_url}{url}")
            logging_utility.debug(f"Request payload: {validated_data.model_dump()}")

            response = self.client.post(url, json=validated_data.model_dump())
            logging_utility.debug(f"Response status code: {response.status_code}")
            logging_utility.debug(f"Response content: {response.text}")

            response.raise_for_status()
            created_message = response.json()
            logging_utility.info("Message created successfully with id: %s", created_message.get('id'))
            return created_message
        except ValidationError as e:
            logging_utility.error("Validation error: %s", e.json())
            raise ValueError(f"Validation error: {e}")
        except httpx.HTTPStatusError as e:
            logging_utility.error("HTTP error occurred while creating message: %s", str(e))
            logging_utility.error(f"Response content: {e.response.text}")
            raise
        except Exception as e:
            logging_utility.error("An error occurred while creating message: %s", str(e))
            raise

    def retrieve_message(self, message_id: str) -> MessageRead:
        logging_utility.info("Retrieving message with id: %s", message_id)
        try:
            url = f"/v1/messages/{message_id}"
            logging_utility.debug(f"Sending GET request to: {self.base_url}{url}")

            response = self.client.get(url)
            logging_utility.debug(f"Response status code: {response.status_code}")
            logging_utility.debug(f"Response content: {response.text}")

            response.raise_for_status()
            message = response.json()
            validated_message = MessageRead(**message)  # Validate data using Pydantic model
            logging_utility.info("Message retrieved successfully")
            return validated_message
        except ValidationError as e:
            logging_utility.error("Validation error: %s", e.json())
            raise ValueError(f"Validation error: {e}")
        except httpx.HTTPStatusError as e:
            logging_utility.error("HTTP error occurred while retrieving message: %s", str(e))
            logging_utility.error(f"Response content: {e.response.text}")
            raise
        except Exception as e:
            logging_utility.error("An error occurred while retrieving message: %s", str(e))
            raise

    def update_message(self, message_id: str, **updates) -> MessageRead:
        logging_utility.info("Updating message with id: %s", message_id)
        logging_utility.debug(f"Update data: {updates}")
        try:
            validated_data = MessageUpdate(**updates)  # Validate data using Pydantic model
            url = f"/v1/messages/{message_id}"
            logging_utility.debug(f"Sending PUT request to: {self.base_url}{url}")
            logging_utility.debug(f"Request payload: {validated_data.model_dump(exclude_unset=True)}")

            response = self.client.put(url, json=validated_data.model_dump(exclude_unset=True))
            logging_utility.debug(f"Response status code: {response.status_code}")
            logging_utility.debug(f"Response content: {response.text}")

            response.raise_for_status()
            updated_message = response.json()
            validated_response = MessageRead(**updated_message)  # Validate response using Pydantic model
            logging_utility.info("Message updated successfully")
            return validated_response
        except ValidationError as e:
            logging_utility.error("Validation error: %s", e.json())
            raise ValueError(f"Validation error: {e}")
        except httpx.HTTPStatusError as e:
            logging_utility.error("HTTP error occurred while updating message: %s", str(e))
            logging_utility.error(f"Response content: {e.response.text}")
            raise
        except Exception as e:
            logging_utility.error("An error occurred while updating message: %s", str(e))
            raise

    def list_messages(self, thread_id: str, limit: int = 20, order: str = "asc") -> List[Dict[str, Any]]:
        logging_utility.info("Listing messages for thread_id: %s, limit: %d, order: %s", thread_id, limit, order)
        params = {
            "limit": limit,
            "order": order
        }
        try:
            url = f"/v1/threads/{thread_id}/messages"
            logging_utility.debug(f"Sending GET request to: {self.base_url}{url}")

            response = self.client.get(url, params=params)
            logging_utility.debug(f"Response status code: {response.status_code}")
            logging_utility.debug(f"Response content: {response.text}")

            response.raise_for_status()
            messages = response.json()
            validated_messages = [MessageRead(**message) for message in messages]  # Validate response using Pydantic model
            logging_utility.info("Retrieved %d messages", len(validated_messages))
            return [message.model_dump() for message in validated_messages]  # Convert Pydantic models to dictionaries
        except ValidationError as e:
            logging_utility.error("Validation error: %s", e.json())
            raise ValueError(f"Validation error: {e}")
        except httpx.HTTPStatusError as e:
            logging_utility.error("HTTP error occurred while listing messages: %s", str(e))
            logging_utility.error(f"Response content: {e.response.text}")
            raise
        except Exception as e:
            logging_utility.error("An error occurred while listing messages: %s", str(e))
            raise

    def get_formatted_messages(self, thread_id: str, system_message: str = "") -> List[Dict[str, Any]]:
        logging_utility.info("Getting formatted messages for thread_id: %s", thread_id)
        logging_utility.info("Using system message: %s", system_message)
        try:
            url = f"/v1/threads/{thread_id}/formatted_messages"
            logging_utility.debug(f"Sending GET request to: {self.base_url}{url}")

            response = self.client.get(url)
            logging_utility.debug(f"Response status code: {response.status_code}")
            logging_utility.debug(f"Response content: {response.text}")

            response.raise_for_status()
            formatted_messages = response.json()

            if not isinstance(formatted_messages, list):
                raise ValueError("Expected a list of messages")

            logging_utility.debug("Initial formatted messages: %s", formatted_messages)

            # Replace the system message if one already exists, otherwise insert it at the beginning
            if formatted_messages and formatted_messages[0].get('role') == 'system':
                formatted_messages[0]['content'] = system_message
                logging_utility.debug("Replaced existing system message with: %s", system_message)
            else:
                formatted_messages.insert(0, {
                    "role": "system",
                    "content": system_message
                })
                logging_utility.debug("Inserted new system message: %s", system_message)

            logging_utility.info("Formatted messages after insertion: %s", formatted_messages)
            logging_utility.info("Retrieved %d formatted messages", len(formatted_messages))
            return formatted_messages
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logging_utility.error("Thread not found: %s", thread_id)
                raise ValueError(f"Thread not found: {thread_id}")
            else:
                logging_utility.error("HTTP error occurred: %s", str(e))
                logging_utility.error(f"Response content: {e.response.text}")
                raise RuntimeError(f"HTTP error occurred: {e}")
        except Exception as e:
            logging_utility.error("An error occurred: %s", str(e))
            raise RuntimeError(f"An error occurred: {str(e)}")

    def delete_message(self, message_id: str) -> Dict[str, Any]:
        logging_utility.info("Deleting message with id: %s", message_id)
        try:
            url = f"/v1/messages/{message_id}"
            logging_utility.debug(f"Sending DELETE request to: {self.base_url}{url}")

            response = self.client.delete(url)
            logging_utility.debug(f"Response status code: {response.status_code}")
            logging_utility.debug(f"Response content: {response.text}")

            response.raise_for_status()
            result = response.json()
            logging_utility.info("Message deleted successfully")
            return result
        except httpx.HTTPStatusError as e:
            logging_utility.error("HTTP error occurred while deleting message: %s", str(e))
            logging_utility.error(f"Response content: {e.response.text}")
            raise
        except Exception as e:
            logging_utility.error("An error occurred while deleting message: %s", str(e))
            raise

    def save_assistant_message_chunk(self, thread_id: str, content: str, is_last_chunk: bool = False) -> Optional[Dict[str, Any]]:
        logging_utility.info("Saving assistant message chunk for thread_id: %s, is_last_chunk: %s", thread_id, is_last_chunk)
        message_data = {
            "thread_id": thread_id,
            "content": content,
            "role": "assistant",
            "sender_id": "assistant",
            "meta_data": {}
        }
        logging_utility.debug(f"Message data: {message_data}")

        try:
            url = "/v1/messages/assistant"
            logging_utility.debug(f"Sending POST request to: {self.base_url}{url}")
            logging_utility.debug(f"Request payload: {message_data}")

            response = self.client.post(url, json=message_data)
            logging_utility.debug(f"Response status code: {response.status_code}")
            logging_utility.debug(f"Response content: {response.text}")

            response.raise_for_status()
            saved_message = response.json()
            logging_utility.info("Assistant message chunk saved successfully")
            return saved_message
        except httpx.HTTPStatusError as e:
            logging_utility.error("HTTP error occurred while saving assistant message chunk: %s", str(e))
            logging_utility.error(f"Response content: {e.response.text}")
            return None
        except Exception as e:
            logging_utility.error("An error occurred while saving assistant message chunk: %s", str(e))
            return None


if __name__ == "__main__":
    # Replace with your actual base URL and API key
    base_url = "http://localhost:9000"
    api_key = "your_api_key"
    #user_client = UserService(base_url, api_key)
    #user = user_client.create_user(name="test"
    #user_id = user.id
    message_service = MessageService(base_url, api_key)
    message_list = message_service.list_messages(thread_id="thread_bfkqar4tGoo25V5Hjrtf0n")
    print(message_list)

