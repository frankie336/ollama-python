from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.models import Message, Thread, User
from api.v1.schemas import MessageCreate, MessageRead
from services.identifier_service import IdentifierService
import json
import time


class MessageService:
    def __init__(self, db: Session):
        self.db = db

    def create_message(self, message: MessageCreate) -> MessageRead:
        # Check if thread exists
        db_thread = self.db.query(Thread).filter(Thread.id == message.thread_id).first()
        if not db_thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        # Check if sender exists
        db_user = self.db.query(User).filter(User.id == message.sender_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="Sender not found")

        db_message = Message(
            id=IdentifierService.generate_message_id(),
            assistant_id=None,
            attachments=[],
            completed_at=None,
            content=[content.dict() for content in message.content],
            created_at=int(time.time()),
            incomplete_at=None,
            incomplete_details=None,
            meta_data=json.dumps(message.meta_data),  # Convert dict to JSON string
            object="message",
            role=message.role,
            run_id=None,
            status=None,
            thread_id=message.thread_id,
            sender_id=message.sender_id
        )

        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)

        return MessageRead(
            id=db_message.id,
            assistant_id=db_message.assistant_id,
            attachments=db_message.attachments,
            completed_at=db_message.completed_at,
            content=db_message.content,
            created_at=db_message.created_at,
            incomplete_at=db_message.incomplete_at,
            incomplete_details=db_message.incomplete_details,
            meta_data=json.loads(db_message.meta_data),  # Convert JSON string back to dict
            object=db_message.object,
            role=db_message.role,
            run_id=db_message.run_id,
            status=db_message.status,
            thread_id=db_message.thread_id
        )

    def retrieve_message(self, message_id: str) -> MessageRead:
        db_message = self.db.query(Message).filter(Message.id == message_id).first()
        if not db_message:
            raise HTTPException(status_code=404, detail="Message not found")

        return MessageRead(
            id=db_message.id,
            assistant_id=db_message.assistant_id,
            attachments=db_message.attachments,
            completed_at=db_message.completed_at,
            content=db_message.content,
            created_at=db_message.created_at,
            incomplete_at=db_message.incomplete_at,
            incomplete_details=db_message.incomplete_details,
            meta_data=json.loads(db_message.meta_data),  # Convert JSON string back to dict
            object=db_message.object,
            role=db_message.role,
            run_id=db_message.run_id,
            status=db_message.status,
            thread_id=db_message.thread_id
        )
