from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.models import Message, Thread, User
from api.v1.schemas import MessageCreate, MessageRead
from services.identifier_service import IdentifierService
import json
import time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class MessageService:
    def __init__(self, db: Session):
        self.db = db

    def create_message(self, message: MessageCreate) -> MessageRead:
        logger.info("Creating message with content: %s", message.content)

        # Check if thread exists
        db_thread = self.db.query(Thread).filter(Thread.id == message.thread_id).first()
        if not db_thread:
            logger.error("Thread not found: %s", message.thread_id)
            raise HTTPException(status_code=404, detail="Thread not found")

        # Check if sender exists
        db_user = self.db.query(User).filter(User.id == message.sender_id).first()
        if not db_user:
            logger.error("Sender not found: %s", message.sender_id)
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
            sender_id=message.sender_id  # Ensure sender_id is set
        )

        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)

        logger.info("Message created with ID: %s", db_message.id)

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
            thread_id=db_message.thread_id,
            sender_id=db_message.sender_id  # Ensure sender_id is returned
        )

    def retrieve_message(self, message_id: str) -> MessageRead:
        logger.info("Retrieving message with ID: %s", message_id)

        db_message = self.db.query(Message).filter(Message.id == message_id).first()
        if not db_message:
            logger.error("Message not found: %s", message_id)
            raise HTTPException(status_code=404, detail="Message not found")

        logger.info("Message retrieved with ID: %s", db_message.id)

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
            thread_id=db_message.thread_id,
            sender_id=db_message.sender_id  # Ensure sender_id is returned
        )

    def list_messages(self, thread_id: str, limit: int = 20, order: str = "asc") -> List[MessageRead]:
        logger.info("Listing messages for thread ID: %s", thread_id)

        db_thread = self.db.query(Thread).filter(Thread.id == thread_id).first()
        if not db_thread:
            logger.error("Thread not found: %s", thread_id)
            raise HTTPException(status_code=404, detail="Thread not found")

        query = self.db.query(Message).filter(Message.thread_id == thread_id)
        if order == "asc":
            query = query.order_by(Message.created_at.asc())
        else:
            query = query.order_by(Message.created_at.desc())

        db_messages = query.limit(limit).all()

        logger.info("Retrieved %d messages for thread ID: %s", len(db_messages), thread_id)

        return [
            MessageRead(
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
                thread_id=db_message.thread_id,
                sender_id=db_message.sender_id  # Ensure sender_id is returned
            )
            for db_message in db_messages
        ]

    def save_assistant_message(self, thread_id: str, content: str):
        logger.info("Saving assistant message for thread ID: %s", thread_id)

        db_thread = self.db.query(Thread).filter(Thread.id == thread_id).first()
        if not db_thread:
            logger.error("Thread not found: %s", thread_id)
            raise HTTPException(status_code=404, detail="Thread not found")

        db_message = Message(
            id=IdentifierService.generate_message_id(),
            assistant_id="assistant_id",  # Set a proper assistant ID
            attachments=[],
            completed_at=int(time.time()),
            content=[{"text": {"value": content, "annotations": []}, "type": "text"}],
            created_at=int(time.time()),
            incomplete_at=None,
            incomplete_details=None,
            meta_data=json.dumps({}),  # Add any relevant metadata
            object="message",
            role="assistant",
            run_id=None,
            status=None,
            thread_id=thread_id,
            sender_id=None  # Assistant messages might not need a sender_id
        )

        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)

        logger.info("Assistant message saved with ID: %s", db_message.id)

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
            thread_id=db_message.thread_id,
            sender_id=db_message.sender_id
        )
