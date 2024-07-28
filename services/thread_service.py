from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.models import Thread, User
from api.v1.schemas import ThreadCreate, ThreadRead, UserBase
from services.identifier_service import IdentifierService
import json
import time

class ThreadService:
    def __init__(self, db: Session):
        self.db = db

    def create_thread(self, thread: ThreadCreate) -> ThreadRead:
        # Check if all users exist
        existing_users = self.db.query(User).filter(User.id.in_(thread.participant_ids)).all()
        if len(existing_users) != len(thread.participant_ids):
            raise HTTPException(status_code=400, detail="Invalid user IDs")

        db_thread = Thread(
            id=IdentifierService.generate_thread_id(),
            created_at=int(time.time()),
            meta_data=json.dumps(thread.meta_data),  # Convert dict to JSON string
            object="thread",  # Set object_type
            tool_resources=json.dumps({})  # Initialize tool_resources as JSON string
        )
        self.db.add(db_thread)

        for user in existing_users:
            db_thread.participants.append(user)

        self.db.commit()
        self.db.refresh(db_thread)

        participants = [UserBase.from_orm(user) for user in db_thread.participants]

        return ThreadRead(
            id=db_thread.id,
            created_at=db_thread.created_at,
            meta_data=json.loads(db_thread.meta_data),  # Convert JSON string back to dict
            object=db_thread.object,
            tool_resources=json.loads(db_thread.tool_resources),  # Convert JSON string back to dict
            participants=participants  # Include participants in the response
        )

    def get_thread(self, thread_id: str) -> ThreadRead:
        thread = self.db.query(Thread).filter(Thread.id == thread_id).first()
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        participants = [UserBase.from_orm(user) for user in thread.participants]
        return ThreadRead(
            id=thread.id,
            created_at=thread.created_at,
            meta_data=json.loads(thread.meta_data),
            object=thread.object,
            tool_resources=json.loads(thread.tool_resources),
            participants=participants
        )

    def update_thread(self, thread_id: str, thread_update: ThreadCreate) -> ThreadRead:
        db_thread = self.db.query(Thread).filter(Thread.id == thread_id).first()
        if not db_thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        # Update fields
        if thread_update.meta_data is not None:
            db_thread.meta_data = json.dumps(thread_update.meta_data)

        # Update participants if provided
        if thread_update.participant_ids:
            existing_users = self.db.query(User).filter(User.id.in_(thread_update.participant_ids)).all()
            if len(existing_users) != len(thread_update.participant_ids):
                raise HTTPException(status_code=400, detail="Invalid user IDs")
            db_thread.participants = existing_users

        self.db.commit()
        self.db.refresh(db_thread)

        participants = [UserBase.from_orm(user) for user in db_thread.participants]

        return ThreadRead(
            id=db_thread.id,
            created_at=db_thread.created_at,
            meta_data=json.loads(db_thread.meta_data),
            object=db_thread.object,
            tool_resources=json.loads(db_thread.tool_resources),
            participants=participants
        )

    def delete_thread(self, thread_id: str) -> None:
        db_thread = self.db.query(Thread).filter(Thread.id == thread_id).first()
        if not db_thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        self.db.delete(db_thread)
        self.db.commit()

    def add_participant(self, thread_id: str, user_id: str) -> ThreadRead:
        db_thread = self.db.query(Thread).filter(Thread.id == thread_id).first()
        if not db_thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user not in db_thread.participants:
            db_thread.participants.append(user)
            self.db.commit()
            self.db.refresh(db_thread)

        participants = [UserBase.from_orm(user) for user in db_thread.participants]

        return ThreadRead(
            id=db_thread.id,
            created_at=db_thread.created_at,
            meta_data=json.loads(db_thread.meta_data),
            object=db_thread.object,
            tool_resources=json.loads(db_thread.tool_resources),
            participants=participants
        )

    def remove_participant(self, thread_id: str, user_id: str) -> ThreadRead:
        db_thread = self.db.query(Thread).filter(Thread.id == thread_id).first()
        if not db_thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user in db_thread.participants:
            db_thread.participants.remove(user)
            self.db.commit()
            self.db.refresh(db_thread)

        participants = [UserBase.from_orm(user) for user in db_thread.participants]

        return ThreadRead(
            id=db_thread.id,
            created_at=db_thread.created_at,
            meta_data=json.loads(db_thread.meta_data),
            object=db_thread.object,
            tool_resources=json.loads(db_thread.tool_resources),
            participants=participants
        )
