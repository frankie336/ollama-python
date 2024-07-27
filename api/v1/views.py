from fastapi import APIRouter, Depends, HTTPException
from typing import List
from .serializers import ThreadCreate, ThreadRead, MessageCreate, MessageRead
from services.thread_service import ThreadService
from services.message_service import MessageService

router = APIRouter()

@router.post("/threads/", response_model=ThreadRead)
def create_thread(thread: ThreadCreate, service: ThreadService = Depends()):
    return service.create_thread(thread)

@router.get("/threads/{thread_id}", response_model=ThreadRead)
def get_thread(thread_id: str, service: ThreadService = Depends()):
    return service.get_thread(thread_id)

@router.post("/threads/{thread_id}/messages/", response_model=MessageRead)
def create_message(thread_id: str, message: MessageCreate, service: MessageService = Depends()):
    return service.create_message(thread_id, message)
