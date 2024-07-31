import time
from new_clients.new_ollama_client import OllamaClient

client = OllamaClient()
from services.loggin_service import LoggingUtility

logging_utility = LoggingUtility
from new_clients.streaming_message_client import StreamingAssistantsClient, setup_user, retrieve_messages, \
    process_stream

# The assistant api contains a number of end points designed to maintain state management to text completions
# Similar to the @OpenAI assistants api. Below is an example of how to build a prompt.

# create a user

user1 = client.user_service.create_user(name='Test')
userid = user1['id']

# Create an assistant
assistant = client.assistant_service.create_assistant(
    name='Mathy',
    description='My helpful maths tutor',
    model='llama3.1',
    instructions='Be as kind, intelligent, and helpful',
)
assistant_id = assistant['id']

# Create thread
thread = client.thead_service.create_thread(participant_ids=[userid], meta_data={"topic": "Test Thread"})
thread_id = thread['id']

# Create a message

message_content = "Hello, can you help me with a math problem?"
message = client.create_message(thread_id=thread_id, content=message_content, sender_id=userid, role='user')


# Create Run
# At this stage the prompt s in state and ready to be sent to the assistant for processing.

run = client.run_service.create_run(assistant_id=assistant_id,
                                    thread_id=thread_id,
                                    )
run_id = run['id']
print(run_id)

# Define the base URL and API key
base_url = "http://localhost:9000/v1"
api_key = "your_api_key"
# Initialize the OllamaClient
client = StreamingAssistantsClient(base_url=base_url, api_key=api_key)
# Create a user (this step is necessary because a thread requires a user)
user_name = "Student"
user_id = setup_user(client, user_name)
print(f"Created user with ID: {user_id}")

# Retrieve all messages in the thread
serialized_messages = retrieve_messages(client, thread_id, system_message=assistant['instructions'])
print("Retrieved and serialized all messages in the thread.")

# Construct the payload
payload = {
    "run_id": run_id,
    "model": assistant['model'],
    "messages": serialized_messages,
    "thread_id": thread_id,
    "stream": True
}

# Chat
response_generator = client.chat(payload)
complete_message = process_stream(response_generator)
print(f"\nFinal Complete Assistant Message:\n{complete_message}")
