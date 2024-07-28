from sqlalchemy.orm import Session
from models.models import Assistant
from api.v1.schemas import AssistantCreate, AssistantRead
from fastapi import HTTPException
import time


class AssistantService:
    def __init__(self, db: Session):
        self.db = db

    def create_assistant(self, assistant_data: AssistantCreate) -> AssistantRead:
        assistant_data.created_at = int(time.time())  # Set the created_at field
        db_assistant = Assistant(**assistant_data.dict())
        self.db.add(db_assistant)
        self.db.commit()
        self.db.refresh(db_assistant)
        return AssistantRead.from_orm(db_assistant)

    def get_assistant(self, assistant_id: str) -> AssistantRead:
        db_assistant = self.db.query(Assistant).filter(Assistant.id == assistant_id).first()
        if not db_assistant:
            raise HTTPException(status_code=404, detail="Assistant not found")
        return AssistantRead.from_orm(db_assistant)
