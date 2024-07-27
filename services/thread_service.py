from http.client import HTTPException

from models import Thread, User, Message
from api.v1.serializers import ThreadCreate, ThreadRead
from sqlalchemy.orm import Session
from typing import List

class ThreadService:
    def __init__(self, db: Session):
        self.db = db

    def create_thread(self, thread: ThreadCreate) -> ThreadRead:
        db_thread = Thread(title=thread.title)
        self.db.add(db_thread)
        self.db.commit()
        self.db.refresh(db_thread)

        # Add participants to the thread
        participants = self.db.query(User).filter(User.id.in_(thread.participant_ids)).all()
        for participant in participants:
            db_thread.participants.append(participant)
        self.db.commit()

        return ThreadRead.from_orm(db_thread)

    def get_thread(self, thread_id: int) -> ThreadRead:
        db_thread = self.db.query(Thread).filter(Thread.id == thread_id).first()
        if not db_thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        return ThreadRead.from_orm(db_thread)
