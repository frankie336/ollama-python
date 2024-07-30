from dotenv import load_dotenv
import os
from new_clients.user_client import UserService
from new_clients.assistant_client import AssistantService
from new_clients.thread_client import ThreadService
from new_clients.message_client import MessageService
from new_clients.run_client import RunService

# Load environment variables from .env file
load_dotenv()


class OllamaClient:
    def __init__(self, base_url=os.getenv('ASSISTANTS_BASE_URL'), api_key='your api key'):
        self.base_url = base_url or os.getenv('ASSISTANTS_BASE_URL')
        self.api_key = api_key or os.getenv('API_KEY')
        self.user_service = UserService(self.base_url, self.api_key)
        self.assistant_service = AssistantService(self.base_url, self.api_key)
        self.thead_service = ThreadService(self.base_url, self.api_key)
        self.message_service = MessageService(self.base_url, self.api_key)
        self.run_service = RunService(self.base_url, self.api_key)

    def user_service(self):
        return self.user_service

    def create_message(self, thread_id, content, role, sender_id):
        data = [
            {
                "type": "text",
                "text": {
                    "value": content,
                    "annotations": []
                }
            }
        ]

        message = self.message_service.create_message(thread_id=thread_id, content=data, role=role, sender_id=sender_id)
        return message

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
    thread = client.thead_service.create_thread(participant_ids=[userid], meta_data={"topic": "Test Thread"})
    thread_id = thread['id']

    # Create a message
    message_content = "Hello, can you help me with a math problem?"
    message = client.create_message(thread_id=thread_id, content=message_content, sender_id=userid, role='user')
    print(message)
