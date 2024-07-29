import json
import time
import asyncio
import httpx
import argparse
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

    async def chat(self, payload):
        try:
            response = await self.client.post("/chat", json=payload, headers={"Accept": "text/event-stream"})
            response.raise_for_status()
            return response.aiter_lines()
        except Exception as e:
            logging_utility.error(f"Error in chat: {e}")
            raise

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

async def setup_assistant(client, assistant_name, model):
    assistant = await client.create_assistant(
        name=assistant_name,
        description=f"A Helpful {assistant_name}",
        model=model,
        instructions=f"You are a {assistant_name}. Provide helpful responses.",
        tools=[{"type": "code_interpreter"}]
    )
    assistant_id = assistant['id']
    print(f"Assistant created with ID: {assistant_id}")
    return assistant_id

async def setup_user(client, user_name):
    user = await client.create_user(name=user_name)
    user_id = user["id"]
    print(f"User created with ID: {user_id}")
    return user_id

async def setup_thread(client, user_id, thread_id=None):
    if thread_id:
        print(f"Using provided thread ID: {thread_id}")
        return thread_id
    new_thread = await client.create_thread(user_id)
    thread_id = new_thread["id"]
    print(f"Created new thread with ID: {thread_id}")
    return thread_id

async def setup_message(client, thread_id, user_id, initial_message, role):
    content = [{"text": {"annotations": [], "value": initial_message}, "type": "text"}]
    new_message = await client.create_message(thread_id=thread_id, content=content, role=role, sender_id=user_id)
    message_id = new_message["id"]
    print(f"Created message with ID: {message_id}")
    return message_id

async def retrieve_messages(client, thread_id, user_id):
    thread_messages = await client.list_messages(thread_id=thread_id)
    print(
        f"Retrieved all messages in the thread: {json.dumps(thread_messages, indent=2)}")  # Print the entire response for debugging

    serialized_messages = []
    for message in thread_messages:
        role = message["role"]  # Use the role field directly from the message

        for content in message["content"]:
            serialized_message = {
                "role": role,
                "content": content["text"]["value"]
            }
            serialized_messages.append(serialized_message)

    print(
        f"Serialized messages: {json.dumps(serialized_messages, indent=2)}")  # Print serialized messages for debugging
    return serialized_messages

async def main(assistant_name, user_name, initial_message, model, thread_id, role):
    client = OllamaClient(base_url=base_url, api_key=api_key)

    try:
        # Test server connection
        async with httpx.AsyncClient() as test_client:
            response = await test_client.get(f"{base_url.rsplit('/v1', 1)[0]}/")
            print(f"Server connection test: {response.status_code}")

        # Setup assistant
        assistant_id = await setup_assistant(client, assistant_name, model)

        # Setup user
        user_id = await setup_user(client, user_name)

        # Setup thread
        if thread_id:
            print(f"Using provided thread ID: {thread_id}")
        else:
            print("Creating a new thread...")
        thread_id = await setup_thread(client, user_id, thread_id)

        # Create initial message
        await setup_message(client, thread_id, user_id, initial_message, role)

        # Retrieve all messages in the thread
        serialized_messages = await retrieve_messages(client, thread_id, user_id)

        # Setup and run the chat
        run = await client.create_run(assistant_id=assistant_id, thread_id=thread_id, instructions="")
        run_id = run["id"]
        print(f"Created run with ID: {run_id}")

        # Construct the payload
        payload = {
            "run_id": run_id,
            "model": model,
            "messages": serialized_messages,
            "thread_id": thread_id,  # Ensure thread_id is included
            "stream": True
        }
        logging_utility.info(f"Payload for chat: {json.dumps(payload, indent=2)}")

        # Chat
        response_generator = await client.chat(payload)
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

def run(assistant_name=None, user_name=None, initial_message=None, model=None, thread_id=None, role=None):
    if assistant_name is None:
        assistant_name = "Math Tutor"
    if user_name is None:
        user_name = "Student"
    if initial_message is None:
        initial_message = "This is a test"
    if model is None:
        model = "llama3.1"
    if role is None:
        role = "user"

    asyncio.run(main(assistant_name, user_name, initial_message, model, thread_id, role))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Ollama Client")
    parser.add_argument("--assistant", default=None, help="Name of the assistant")
    parser.add_argument("--user", default=None, help="Name of the user")
    parser.add_argument("--message", default=None, help="Initial message")
    parser.add_argument("--model", default=None, help="Model to use")
    parser.add_argument("--thread_id", default=None, help="Existing thread ID to use")
    parser.add_argument("--role", default="user", help="Role of the sender (user or assistant)")

    args = parser.parse_args()

    run(
        assistant_name=args.assistant,
        user_name=args.user,
        initial_message=args.message,
        model=args.model,
        thread_id="thread_Xf6UhhiVY6m65XbaWbXV9Q",
        role=args.role
    )
