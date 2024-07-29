import time

from services.loggin_service import LoggingUtility
logging_utility = LoggingUtility
import json
from new_clients.streaming_message_client import StreamingMessageClient, setup_user, setup_thread, setup_message, setup_assistant, retrieve_messages, process_stream

# Define the base URL and API key
base_url = "http://localhost:8000/v1"
api_key = "your_api_key"

# Initialize the OllamaClient
client = StreamingMessageClient(base_url=base_url, api_key=api_key)

# Create a user (this step is necessary because a thread requires a user)
user_name = "Student"
user_id = setup_user(client, user_name)
print(f"Created user with ID: {user_id}")




# Create an assistant
assistant_name = "Math Tutor"
assistant_model = "llama3.1"
assistant = client.create_assistant(name=assistant_name,
                                    description='Test assistant',
                                    model=assistant_model,
                                    instructions='You are test AI entity called Arakis',
                                    tools=[{"type": "code_interpreter"}]
                                    )

assistant_id = assistant['id']
#assistant_id= "asst_CBWTyfVtzNLCDwh3JPQh9M"
print(f"Created assistant with ID: {assistant_id}")













# Create a thread for the user
thread = client.create_thread(user_id=user_id)
# thread_id = thread['id']
thread_id="thread_gphpw3J12OFsVbFOBFBff7"
print(f"Created thread with ID: {thread_id}")


# Set up initial message
initial_message = "what is your name?"
role = "user"
setup_message(client, thread_id, user_id, initial_message, role)
print("Initial message set up successfully.")




# Set up run
instructions = ""
run_data = client.create_run(assistant_id=assistant_id, thread_id=thread_id, instructions=instructions)
run_id = run_data["id"]
print(f"Created run with ID: {run_id}")



# Retrieve all messages in the thread
serialized_messages = retrieve_messages(client, thread_id, system_message=assistant['instructions'])
print("Retrieved and serialized all messages in the thread.")



# Construct the payload
payload = {
    "run_id": run_id,
    "model": assistant_model,
    "messages": serialized_messages,
    "thread_id": thread_id,
    "stream": True
}


# Chat
response_generator = client.chat(payload)
complete_message = process_stream(response_generator)
print(f"\nFinal Complete Assistant Message:\n{complete_message}")
