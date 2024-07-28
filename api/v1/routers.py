from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Iterator, Union
import httpx
from fastapi.responses import StreamingResponse
from api.v1.schemas import (
    UserCreate, UserRead, UserUpdate, ThreadCreate, ThreadRead, MessageCreate, MessageRead, Run, AssistantCreate, AssistantRead
)
from db.database import get_db
from services.user_service import UserService
from services.thread_service import ThreadService
from services.message_service import MessageService
from services.run_service import RunService
from services.assistant_service import AssistantService
from services.loggin_service import LoggingUtility

logging_utility = LoggingUtility()

router = APIRouter()

# Helper function to forward requests to the Ollama API
async def forward_to_ollama(path: str, payload: Dict[str, Any], stream: bool = False):
    async with httpx.AsyncClient(base_url="http://localhost:11434") as client:
        try:
            response = await client.post(path, json=payload)
            response.raise_for_status()
            if stream:
                async for line in response.aiter_lines():
                    logging_utility.info("Streaming response line: %s", line)
                    yield line
            else:
                result = response.json()
                logging_utility.info("Response JSON: %s", result)
                yield result
        except httpx.HTTPStatusError as e:
            logging_utility.error("HTTPStatusError in forward_to_ollama: %s", str(e))
            raise
        except Exception as e:
            logging_utility.error("Exception in forward_to_ollama: %s", str(e))
            raise

# Generate endpoint
@router.post("/api/generate")
async def generate_endpoint(payload: Dict[str, Any]):
    logging_utility.info("Received request at /api/generate with payload: %s", payload)
    try:
        result = await forward_to_ollama("/api/generate", payload)
        return result
    except Exception as e:
        logging_utility.error("Error in generate_endpoint: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Chat endpoint
from fastapi.responses import StreamingResponse, JSONResponse

@router.post("/chat")
async def chat_endpoint(payload: Dict[str, Any]):
    logging_utility.info("Received request at /v1/chat with payload: %s", payload)
    try:
        if payload.get("stream", False):
            return StreamingResponse(forward_to_ollama("/api/chat", payload, stream=True), media_type="application/json")
        else:
            result = [item async for item in forward_to_ollama("/api/chat", payload)]
            return JSONResponse(content=result[0] if result else {})
    except Exception as e:
        logging_utility.error("Error in chat_endpoint: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

# User routes
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

# Thread routes
@router.post("/threads", response_model=ThreadRead)
def create_thread(thread: ThreadCreate, db: Session = Depends(get_db)):
    thread_service = ThreadService(db)
    return thread_service.create_thread(thread)

@router.get("/threads/{thread_id}", response_model=ThreadRead)
def get_thread(thread_id: str, db: Session = Depends(get_db)):
    thread_service = ThreadService(db)
    return thread_service.get_thread(thread_id)

# Message routes
@router.post("/messages", response_model=MessageRead)
def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    message_service = MessageService(db)
    return message_service.create_message(message)

@router.get("/messages/{message_id}", response_model=MessageRead)
def get_message(message_id: str, db: Session = Depends(get_db)):
    message_service = MessageService(db)
    return message_service.retrieve_message(message_id)

# Run routes
@router.post("/runs", response_model=Run)
def create_run(run: Run, db: Session = Depends(get_db)):
    run_service = RunService(db)
    return run_service.create_run(run)

@router.get("/runs/{run_id}", response_model=Run)
def get_run(run_id: str, db: Session = Depends(get_db)):
    run_service = RunService(db)
    return run_service.get_run(run_id)

# Assistant routes
@router.post("/assistants", response_model=AssistantRead)
def create_assistant(assistant: AssistantCreate, db: Session = Depends(get_db)):
    assistant_service = AssistantService(db)
    return assistant_service.create_assistant(assistant)

@router.get("/assistants/{assistant_id}", response_model=AssistantRead)
def get_assistant(assistant_id: str, db: Session = Depends(get_db)):
    assistant_service = AssistantService(db)
    return assistant_service.get_assistant(assistant_id)
