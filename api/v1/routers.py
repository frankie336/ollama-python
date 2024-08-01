import json
from typing import Dict, Any, AsyncGenerator, List
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse, JSONResponse

from api.v1.schemas import (
    UserCreate, UserRead, UserUpdate, ThreadCreate, ThreadRead, MessageCreate, MessageRead, Run, AssistantCreate,
    AssistantRead
)
from db.database import get_db
from services.assistant_service import AssistantService
from services.loggin_service import LoggingUtility
from services.message_service import MessageService
from services.run_service import RunService
from services.thread_service import ThreadService
from services.user_service import UserService

logging_utility = LoggingUtility()

router = APIRouter()


class OllamaClient:
    def __init__(self, base_url: str = "http://172.21.0.2:11434"):
        self.base_url = base_url


base_url = "http://172.21.0.2:11434"
ollama_client = OllamaClient(base_url=base_url)


@router.post("/api/generate")
async def generate_endpoint(payload: Dict[str, Any]):
    logging_utility.info("Received request at /api/generate with payload: %s", payload)
    try:
        result = await ollama_client.forward_to_ollama("/api/generate", payload)
        return next(result)
    except Exception as e:
        logging_utility.error("Error in generate_endpoint: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")



@router.post("/users", response_model=UserRead)
def create_user(user: UserCreate = None, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.create_user(user)


@router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.get_user(user_id)


@router.put("/users/{user_id}", response_model=UserRead)
def update_user(user_id: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.update_user(user_id, user_update)


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user_service = UserService(db)
    user_service.delete_user(user_id)
    return {"detail": "User deleted successfully"}


@router.post("/threads", response_model=ThreadRead)
def create_thread(thread: ThreadCreate, db: Session = Depends(get_db)):
    thread_service = ThreadService(db)
    return thread_service.create_thread(thread)


@router.get("/threads/{thread_id}", response_model=ThreadRead)
def get_thread(thread_id: str, db: Session = Depends(get_db)):
    thread_service = ThreadService(db)
    return thread_service.get_thread(thread_id)


@router.post("/messages", response_model=MessageRead)
def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    message_service = MessageService(db)
    return message_service.create_message(message)


@router.get("/messages/{message_id}", response_model=MessageRead)
def get_message(message_id: str, db: Session = Depends(get_db)):
    message_service = MessageService(db)
    return message_service.retrieve_message(message_id)


@router.get("/threads/{thread_id}/messages", response_model=List[MessageRead])
def list_messages(thread_id: str, limit: int = 20, order: str = "asc", db: Session = Depends(get_db)):
    logging_utility.info(f"Retrieving messages for thread: {thread_id}")
    message_service = MessageService(db)
    return message_service.list_messages(thread_id=thread_id, limit=limit, order=order)


@router.post("/runs", response_model=Run)
def create_run(run: Run, db: Session = Depends(get_db)):
    run_service = RunService(db)
    return run_service.create_run(run)


@router.get("/runs/{run_id}", response_model=Run)
def get_run(run_id: str, db: Session = Depends(get_db)):
    run_service = RunService(db)
    return run_service.get_run(run_id)


@router.post("/assistants", response_model=AssistantRead)
def create_assistant(assistant: AssistantCreate, db: Session = Depends(get_db)):
    assistant_service = AssistantService(db)
    return assistant_service.create_assistant(assistant)


@router.get("/assistants/{assistant_id}", response_model=AssistantRead)
def get_assistant(assistant_id: str, db: Session = Depends(get_db)):
    assistant_service = AssistantService(db)
    return assistant_service.get_assistant(assistant_id)


@router.get("/threads/{thread_id}/formatted_messages", response_model=List[Dict[str, Any]])
def get_formatted_messages(thread_id: str, db: Session = Depends(get_db)):
    message_service = MessageService(db)
    try:
        return message_service.list_messages_for_thread(thread_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/messages/assistant", response_model=MessageRead)
def save_assistant_message(message: MessageCreate, db: Session = Depends(get_db)):
    message_service = MessageService(db)
    return message_service.save_assistant_message_chunk(
        thread_id=message.thread_id,
        content=message.content,
        is_last_chunk=True  # Assuming we're always sending the complete message
    )