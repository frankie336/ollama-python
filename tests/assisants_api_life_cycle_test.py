import asyncio
import time

import httpx
import json
from services.loggin_service import LoggingUtility

logging_utility = LoggingUtility()

# Base URL and API key
base_url = "http://localhost:8000/v1"  # Updated to include /v1
api_key = "your_api_key"

class OllamaClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    async def create_assistant(self, name, description, model, instructions, tools):
        try:
            logging_utility.info(f"Sending request to {self.base_url}/assistants")
            response = await self.client.post("/assistants", json={
                "name": name,
                "description": description,
                "model": model,
                "instructions": instructions,
                "tools": tools
            })
            logging_utility.info(f"Response status: {response.status_code}")
            logging_utility.info(f"Response content: {response.text}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logging_utility.error(f"HTTP error occurred: {e}")
            raise
        except Exception as e:
            logging_utility.error(f"An error occurred: {e}")
            raise

    async def create_user(self, name):
        try:
            response = await self.client.post("/users", json={"name": name})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging_utility.error(f"Error creating user: {e}")
            raise

    async def create_thread(self, user_id):
        try:
            response = await self.client.post("/threads", json={
                "participant_ids": [user_id],
                "meta_data": {"topic": "Test Thread"}
            })
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging_utility.error(f"Error creating thread: {e}")
            raise

    async def create_message(self, thread_id, content, role, sender_id):
        try:
            response = await self.client.post("/messages", json={
                "thread_id": thread_id,
                "content": content,
                "role": role,
                "sender_id": sender_id
            })
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging_utility.error(f"Error creating message: {e}")
            raise

    async def list_messages(self, thread_id):
        try:
            response = await self.client.get(f"/threads/{thread_id}/messages")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging_utility.error(f"Error listing messages: {e}")
            raise

    async def create_run(self, assistant_id, thread_id, instructions):
        try:
            current_time = int(time.time())
            run_data = {
                "id": f"run_{assistant_id}_{thread_id}",
                "assistant_id": assistant_id,
                "thread_id": thread_id,
                "instructions": instructions,
                "meta_data": {},
                "cancelled_at": None,
                "completed_at": None,
                "created_at": current_time,
                "expires_at": current_time + 3600,  # 1 hour from now
                "failed_at": None,
                "incomplete_details": None,
                "last_error": None,
                "max_completion_tokens": 1000,
                "max_prompt_tokens": 500,
                "model": "gpt-4",  # You might want to make this configurable
                "object": "run",
                "parallel_tool_calls": False,
                "required_action": None,
                "response_format": "text",
                "started_at": None,
                "status": "pending",
                "tool_choice": "none",
                "tools": [],
                "truncation_strategy": {},
                "usage": None,
                "temperature": 0.7,
                "top_p": 0.9,
                "tool_resources": {}
            }
            response = await self.client.post("/runs", json=run_data)
            logging_utility.info(f"Create run response status: {response.status_code}")
            logging_utility.info(f"Create run response content: {response.text}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging_utility.error(f"Error creating run: {e}")
            raise
    async def chat(self, run_id, model, messages, stream=True):
        try:
            response = await self.client.post("/chat", json={
                "run_id": run_id,
                "model": model,
                "messages": messages,
                "stream": stream
            }, headers={"Accept": "text/event-stream"})
            response.raise_for_status()
            return response.aiter_lines()
        except Exception as e:
            logging_utility.error(f"Error in chat: {e}")
            raise

client = OllamaClient(base_url=base_url, api_key=api_key)

async def process_stream(response_generator):
    complete_message = ""
    async for chunk in response_generator:
        print(f"Raw chunk received: {chunk}")
        if chunk.startswith("data: "):
            try:
                data = json.loads(chunk[6:])  # Remove "data: " prefix
                content = data.get('content', '')
                complete_message += content
                print(f"Received content: {content}")
                print(f"Current message: {complete_message}")
                print("-" * 50)  # Separator for readability

                if data.get('done', False):
                    print("\nStream completed.")
                    break
            except json.JSONDecodeError:
                print(f"Failed to parse JSON: {chunk}")
        elif chunk.strip() == "":
            continue  # Skip empty lines
        else:
            print(f"Unexpected chunk format: {chunk}")

    return complete_message

async def main():
    try:
        # Test server connection
        async with httpx.AsyncClient() as test_client:
            response = await test_client.get(f"{base_url.rsplit('/v1', 1)[0]}/")
            logging_utility.info(f"Server connection test: {response.status_code}")

        # Create an assistant
        assistant = await client.create_assistant(
            name="Mathy",
            description="A Helpful Math tutor",
            model="llama3.1",
            instructions="You are a personal math tutor. Write and run code to answer math questions.",
            tools=[{"type": "code_interpreter"}]
        )
        assistant_id = assistant['id']
        print(f"Assistant created with ID: {assistant_id}")

        # Create a user
        user1 = await client.create_user(name="User 1")
        user1_id = user1["id"]

        # Create a thread
        new_thread = await client.create_thread(user1_id)
        thread_id = new_thread["id"]
        print(f"Created thread with ID: {thread_id}")

        # Create a message
        content = [{"text": {"annotations": [], "value": "Send me a poem"}, "type": "text"}]
        new_message = await client.create_message(thread_id=thread_id, content=content, role="user", sender_id=user1_id)
        message_id = new_message["id"]
        print(f"Created message with ID: {message_id}")

        # Retrieve all messages in the thread
        thread_messages = await client.list_messages(thread_id=thread_id)
        print(f"Retrieved all messages in the thread: {thread_messages}")

        # Serialize the messages for the chat endpoint
        serialized_messages = [
            {"role": "user" if message["sender_id"] == user1_id else "assistant",
             "content": message["content"][0]["text"]["value"]}
            for message in thread_messages
        ]
        print(f"Serialized messages: {serialized_messages}")

        # Set up the run
        run = await client.create_run(assistant_id=assistant_id, thread_id=thread_id, instructions="")
        run_id = run["id"]
        print(f"Created run with ID: {run_id}")

        # Chat
        response_generator = await client.chat(run_id=run_id, model="llama3.1", messages=serialized_messages, stream=True)
        complete_message = await process_stream(response_generator)
        print(f"\nFinal Complete Assistant Message:\n{complete_message}")

    except httpx.HTTPStatusError as e:
        print(f"HTTPStatusError: {e.response.status_code} - {e.response.text}")
        print(f"Request URL: {e.request.url}")
        print(f"Request method: {e.request.method}")
        print(f"Request headers: {e.request.headers}")
        print(f"Request content: {e.request.content}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())