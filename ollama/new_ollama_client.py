from dotenv import load_dotenv
import os
import json
from new_clients.user_client import UserService
from new_clients.assistant_client import AssistantService
from new_clients.thread_client import ThreadService
from new_clients.message_client import MessageService
from new_clients.run_client import RunService
from ollama import Client

# Load environment variables from .env file
load_dotenv()


class OllamaClient:
    def __init__(self, base_url=os.getenv('ASSISTANTS_BASE_URL'), api_key='your api key'):
        self.base_url = base_url or os.getenv('ASSISTANTS_BASE_URL')
        self.api_key = api_key or os.getenv('API_KEY')
        self.user_service = UserService(self.base_url, self.api_key)
        self.assistant_service = AssistantService(self.base_url, self.api_key)
        self.thread_service = ThreadService(self.base_url, self.api_key)
        self.message_service = MessageService(self.base_url, self.api_key)
        self.run_service = RunService(self.base_url, self.api_key)
        self.ollama_client = Client()

    def create_thread(self):
        return self.thread_service.create_thread(participant_ids=None, meta_data=None)

    def create_message(self, thread_id, content, role, sender_id):
        message = self.message_service.create_message(thread_id=thread_id, content=content, role=role,
                                                      sender_id=sender_id)
        return message

    def streamed_response_helper(self, messages, thread_id, model='llama3.1'):
        try:
            # We assume the last message in 'messages' is the user's message
            user_message = messages[-1]['content']

            response = self.ollama_client.chat(
                model=model,
                messages=messages,  # Send all messages for context
                stream=True
            )

            print("DEBUG: Response received from Ollama client")
            full_response = ""
            for chunk in response:
                content = chunk['message']['content']
                full_response += content
                print(f" {content}", end='', flush=True)
                yield content

            print("\nDEBUG: Finished yielding all chunks")
            print(f"\nFull response: {full_response}")

            # Save the complete assistant message
            saved_message = self.message_service.save_assistant_message_chunk(thread_id, full_response,
                                                                              is_last_chunk=True)

            if saved_message:
                print("Assistant message saved successfully.")
            else:
                print("Failed to save assistant message.")

        except Exception as e:
            error_message = f"Error in send_new_message: {str(e)}"
            print(f"DEBUG: {error_message}")
            yield json.dumps({"error": "An error occurred while generating the response"})

        print("DEBUG: Exiting send_new_message")

    def process_conversation(self, thread_id, model='llama3.1'):


        # Get formatted messages
        messages = self.message_service.get_formatted_messages(thread_id)

        # Generate and stream response
        return self.streamed_response_helper(messages, thread_id, model)


if __name__ == "__main__":
    client = OllamaClient()

    # Create a user
    user1 = client.user_service.create_user(name='Test')
    userid = user1['id']

    # Create an assistant
    assistant = client.assistant_service.create_assistant(
        name='Mathy',
        description='My helpful maths tutor',
        model='llama3.1',
        instructions='Be as kind, intelligent, and helpful',
        tools=[{"type": "code_interpreter"}]
    )

    # Create thread
    thread = client.thread_service.create_thread(participant_ids=[userid], meta_data={"topic": "Test Thread"})
    thread_id = thread['id']

    # Create message

    message = client.create_message(thread_id=thread_id,

                                    content="This is a test message",
                                    role='user',
                                    sender_id=userid)

    for chunk in client.process_conversation(thread_id):
        # In a real application, you might want to do something with each chunk,
        # like sending it to a frontend. Here we're just printing it.
        print(chunk, end='', flush=True)

    print("\nConversation processed successfully.")