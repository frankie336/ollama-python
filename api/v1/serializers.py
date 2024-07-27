from pydantic import BaseModel
from typing import List, Optional

class MessageCreate(BaseModel):
    content: str
    sender_id: int

class MessageRead(BaseModel):
    id: int
    content: str
    sender_id: int
    thread_id: int

    class Config:
        orm_mode = True

class ThreadCreate(BaseModel):
    title: str
    participant_ids: List[int]

class ThreadRead(BaseModel):
    id: int
    title: str
    participant_ids: List[int]
    messages: List[MessageRead] = []

    class Config:
        orm_mode = True
