import json
import time
import asyncio
from ollama.new_ollama_client import OllamaClient
from services.loggin_service import LoggingUtility
from ollama import Client

client = OllamaClient()
logging_utility = LoggingUtility()

# Create a user
user1 = client.user_service.create_user(name='Test')
userid = user1['id']

# Create an assistant
assistant = client.assistant_service.create_assistant(
    name='Mathy',
    description='My helpful maths tutor',
    model='llama3.1',
    #instructions='Be as kind, intelligent, and helpful',
)
assistant_id = assistant['id']

# Create thread
thread = client.thread_service.create_thread()
thread_id = thread['id']
#thread_id = "thread_eILawVFGeYN87KDR0ckf3g"
# Create a message
message_content = "This is  a test message"
message = client.create_message(thread_id=thread_id, content=message_content, sender_id=userid, role='user')
message_id = message['id']

# Fetch all messages
serialized_messages = client.message_service.get_formatted_messages(thread_id=thread_id)
print("Serialized messages:", serialized_messages)

# Create Run
run = client.run_service.create_run(assistant_id=assistant_id, thread_id=thread_id)
run_id = run['id']

import asyncio

from ollama import AsyncClient

async def streamed_response_helper(messages, thread_id):
    try:
        async for part in await AsyncClient().chat(
            model='llama3.1',
            messages=messages,
            options={'num_ctx': 8192},
            stream=True
        ):
            content = part['message']['content']
            print(f" {content}", end='', flush=True)
            yield content

        print("\nDEBUG: Finished yielding all chunks")
        full_response = "".join(part['message']['content'] for part in await AsyncClient().chat(model='llama3.1', messages=messages))

        # Save the complete assistant message
        saved_message = await client.message_service.save_assistant_message_chunk(thread_id, full_response, is_last_chunk=True)

        if saved_message:
            print("Assistant message saved successfully.")
        else:
            print("Failed to save assistant message.")

    except Exception as e:
        error_message = f"Error in send_new_message: {str(e)}"
        print(f"DEBUG: {error_message}")
        yield json.dumps({"error": "An error occurred while generating the response"})

    print("DEBUG: Exiting send_new_message")

async def main_coroutine():
    async for chunk in streamed_response_helper(serialized_messages, thread_id):
        # Process the chunk here
        print(f"Processing chunk: {chunk}")

asyncio.run(main_coroutine())