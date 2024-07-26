from sqlalchemy import Column, Integer, String, Text
from .database import Base

class Thread(Base):
    __tablename__ = "threads"
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, unique=True, index=True)
    content = Column(Text)
