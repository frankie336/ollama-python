import json
import time
import httpx
import argparse
from services.loggin_service import LoggingUtility

logging_utility = LoggingUtility()

# Base URL and API key
base_url = "http://localhost:8000/v1"
api_key = "your_api_key"


class StreamingAssistantsClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.Client(base_url=base_url, headers={"Authorization": f"Bearer {api_key}"})

    def create_assistant(self, name, description, model, instructions, tools):
        try:
            response = self.client.post("/assistants", json={
                "name": name,
                "description": description,
                "model": model,
                "instructions": instructions,
                "tools": tools
            })
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logging_utility.error(f"HTTP error occurred: {e.response.text}")
            raise
        except Exception as e:
            logging_utility.error(f"An error occurred: {e}")
            raise

    def create_user(self, name):
        try:
            response = self.client.post("/users", json={"name": name})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging_utility.error(f"Error creating user: {e}")
            raise

    def create_thread(self, participant_ids, meta_data):
        try:
            response = self.client.post("/threads", json={
                "participant_ids": participant_ids,
                "meta_data": meta_data
            })
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging_utility.error(f"Error creating thread: {e}")
            raise

    def create_message(self, thread_id, content, role, sender_id, meta_data=None):
        if meta_data is None:
            meta_data = {}
        try:
            response = self.client.post("/messages", json={
                "thread_id": thread_id,
                "content": content,
                "role": role,
                "sender_id": sender_id,
                "meta_data": meta_data
            })
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging_utility.error(f"Error creating message: {e}")
            raise

    def list_messages(self, thread_id):
        try:
            response = self.client.get(f"/threads/{thread_id}/messages")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging_utility.error(f"Error listing messages: {e}")
            raise

    def create_run(self, assistant_id, thread_id, instructions):
        try:
            response = self.client.post("/runs", json={
                "assistant_id": assistant_id,
                "thread_id": thread_id,
                "instructions": instructions
            })
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging_utility.error(f"Error creating run: {e}")
            raise

    def chat(self, payload):
        try:
            response = self.client.post("/chat", json=payload, headers={"Accept": "text/event-stream"})
            response.raise_for_status()
            for line in response.iter_lines():
                yield line
        except Exception as e:
            logging_utility.error(f"Error in chat: {e}")
            raise


def process_stream(response_generator):
    print("Starting process_stream")
    for chunk in response_generator:
        print(f"Received chunk: {chunk}")
        if chunk.startswith("data: "):
            try:
                data = json.loads(chunk[6:])  # Remove "data: " prefix
                print(f"Parsed data: {data}")
                content = data.get('content', '')
                if content:
                    print(f"Yielding content: {content}")
                    yield json.dumps({"content": content})
                if data.get('done', False):
                    print("Received done signal")
                    break
            except json.JSONDecodeError:
                print(f"Failed to parse JSON: {chunk}")
        elif chunk.strip() == "":
            print("Skipping empty line")
            continue  # Skip empty lines
        else:
            print(f"Unexpected chunk format: {chunk}")
    print("Finished process_stream")
def setup_assistant(client, assistant_name, model):
    assistant = client.create_assistant(
        name=assistant_name,
        description=f"A Helpful {assistant_name}",
        model=model,
        instructions=f"You are a {assistant_name}. Provide helpful responses.",
        tools=[{"type": "code_interpreter"}]
    )
    assistant_id = assistant['id']
    print(f"Assistant created with ID: {assistant_id}")
    return assistant_id

def setup_user(client, user_name):
    user = client.create_user(name=user_name)
    user_id = user["id"]
    print(f"User created with ID: {user_id}")
    return user_id

def setup_thread(client, user_id, thread_id=None):
    if thread_id:
        print(f"Using provided thread ID: {thread_id}")
        return thread_id
    new_thread = client.create_thread(user_id)
    thread_id = new_thread["id"]
    print(f"Created new thread with ID: {thread_id}")
    return thread_id

def setup_message(client, thread_id, user_id, initial_message, role):
    content = [{"text": {"annotations": [], "value": initial_message}, "type": "text"}]
    new_message = client.create_message(thread_id=thread_id, content=content, role=role, sender_id=user_id)
    message_id = new_message["id"]
    print(f"Created message with ID: {message_id}")
    return message_id

def retrieve_messages(client, thread_id, system_message="This is a system message"):
    # Retrieve all messages in the thread
    thread_messages = client.list_messages(thread_id=thread_id)
    print(f"Retrieved all messages in the thread: {json.dumps(thread_messages, indent=2)}")  # Print the entire response for debugging

    serialized_messages = []
    last_role = None

    for message in thread_messages:
        role = message["role"]  # Use the role field directly from the message

        for content in message["content"]:
            serialized_message = {
                "role": role,
                "content": content["text"]["value"]
            }
            # Ensure alternating roles
            if last_role and last_role == role:
                continue
            serialized_messages.append(serialized_message)
            last_role = role

    # Insert the system message at the top of the serialized_messages list
    if system_message:
        serialized_messages.insert(0, {"role": "system", "content": system_message})

    print(f"Serialized messages with system message: {json.dumps(serialized_messages, indent=2)}")  # Print serialized messages for debugging
    return serialized_messages

def run(assistant_id=None, assistant_name=None, user_name=None, initial_message=None, model=None, thread_id=None, role=None):
    client = StreamingAssistantsClient(base_url=base_url, api_key=api_key)

    try:
        # Setup assistant
        if not assistant_id:
            if assistant_name is None or model is None:
                raise ValueError("Assistant name and model must be provided if no assistant ID is given.")
            assistant_id = setup_assistant(client, assistant_name, model)

        # Setup user
        if user_name is None:
            raise ValueError("User name must be provided.")
        user_id = setup_user(client, user_name)

        # Setup thread
        if thread_id:
            print(f"Using provided thread ID: {thread_id}")
        else:
            print("Creating a new thread...")
        thread_id = setup_thread(client, user_id, thread_id)

        # Create initial message
        if initial_message is None:
            raise ValueError("Initial message must be provided.")
        setup_message(client, thread_id, user_id, initial_message, role)

        # Retrieve all messages in the thread
        serialized_messages = retrieve_messages(client, thread_id)

        # Setup and run the chat
        run_data = client.create_run(assistant_id=assistant_id, thread_id=thread_id, instructions="")
        run_id = run_data["id"]
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
        response_generator = client.chat(payload)
        complete_message = process_stream(response_generator)
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
    parser = argparse.ArgumentParser(description="Run Ollama Client")
    parser.add_argument("--assistant_id", default=None, help="ID of the assistant")
    parser.add_argument("--assistant", default=None, help="Name of the assistant")
    parser.add_argument("--user", default=None, help="Name of the user")
    parser.add_argument("--message", default=None, help="Initial message")
    parser.add_argument("--model", default=None, help="Model to use")
    parser.add_argument("--thread_id", default=None, help="Existing thread ID to use")
    parser.add_argument("--role", default="user", help="Role of the sender (user or assistant)")
    args = parser.parse_args()

    run(
        assistant_id=args.assistant_id,
        assistant_name=args.assistant,
        user_name=args.user,
        initial_message=args.message,
        model=args.model,
        thread_id=args.thread_id,
        role=args.role
    )
