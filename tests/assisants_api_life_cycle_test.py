from new_clients.assistant_client import AssistantService
from new_clients.thread_client import ThreadService
from new_clients.message_client import MessageService
from new_clients.ollama_client import OllamaClient, RunService
from services.loggin_service import LoggingUtility

logging_utility = LoggingUtility()

# Base URL and API key
base_url = "http://localhost:8000"
api_key = "your_api_key"

# Initialize the services
thread_service = ThreadService(base_url, api_key)
message_service = MessageService(base_url, api_key)
assistant_service = AssistantService(base_url, api_key)
run_service = RunService(base_url, api_key)

# Initialize the OllamaClient
client = OllamaClient(base_url=base_url, api_key=api_key, run_service=run_service)

# Create an assistant
assistant = assistant_service.create_assistant(
    name="Mathy",
    description="A Helpful Math tutor",
    model="llama3.1",
    instructions="You are a personal math tutor. Write and run code to answer math questions.",
    tools=[{"type": "code_interpreter"}]
)
assistant_id = assistant['id']
print(f"Assistant created with ID: {assistant_id}")

# Create a user
user1 = thread_service.create_user(name="User 1")
user1_id = user1["id"]

# Create a thread
new_thread = thread_service.create_thread(participant_ids=[user1_id], meta_data={"topic": "Test Thread"})
thread_id = new_thread["id"]
print(f"Created thread with ID: {thread_id}")

# Create a message
content = [{"text": {"annotations": [], "value": "I need to solve the equation `3x + 11 = 14`. Can you help me?"}, "type": "text"}]
new_message = message_service.create_message(thread_id=thread_id, content=content, role="user", sender_id=user1_id)
message_id = new_message["id"]
print(f"Created message with ID: {message_id}")

# Retrieve the created message to verify
retrieved_message = message_service.retrieve_message(message_id)
print(f"Retrieved message: {retrieved_message}")

# Set up the run
run = run_service.create_run(assistant_id=assistant_id, thread_id=thread_id, instructions="")
run_id = run["id"]
print(f"Created run with ID: {run_id}")

# Test the chat endpoint
response = client.chat(run_id=run_id, model="llama3.1", messages=[{"role": "user", "content": "I need to solve the equation `3x + 11 = 14`. Can you help me?"}], stream=True)

for chunk in response.iter_lines():
    print(chunk.decode('utf-8'), end='', flush=True)
