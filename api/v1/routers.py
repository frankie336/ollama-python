from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.v1.schemas import UserCreate, UserRead, UserUpdate, ThreadCreate, ThreadRead, MessageCreate, MessageRead, Run, AssistantCreate, AssistantRead
from db.database import get_db
from services.user_service import UserService
from services.thread_service import ThreadService
from services.message_service import MessageService
from services.run_service import RunService
from services.identifier_service import IdentifierService
from services.assistant_service import AssistantService

router = APIRouter()

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
    assistant.id = IdentifierService.generate_assistant_id()  # Generate assistant ID
    assistant_service = AssistantService(db)
    return assistant_service.create_assistant(assistant)

@router.get("/assistants/{assistant_id}", response_model=AssistantRead)
def get_assistant(assistant_id: str, db: Session = Depends(get_db)):
    assistant_service = AssistantService(db)
    return assistant_service.get_assistant(assistant_id)
