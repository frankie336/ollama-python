from sqlalchemy import Column, String, Integer, Boolean, JSON, DateTime, Table, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
import time

Base = declarative_base()

# Association table for many-to-many relationship between Thread and User
thread_participants = Table(
    'thread_participants',
    Base.metadata,
    Column('thread_id', String(64), ForeignKey('threads.id'), primary_key=True),
    Column('user_id', String(64), ForeignKey('users.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, index=True)  # Specify length for VARCHAR
    name = Column(String(128), index=True)  # Specify length for VARCHAR
    threads = relationship('Thread', secondary=thread_participants, back_populates='participants')

class Thread(Base):
    __tablename__ = "threads"

    id = Column(String(64), primary_key=True, index=True)  # Specify length for VARCHAR
    created_at = Column(Integer, nullable=False)
    meta_data = Column(JSON, nullable=False, default={})  # renamed metadata to meta_data
    object = Column(String(64), nullable=False)  # Specify length for VARCHAR
    tool_resources = Column(JSON, nullable=False, default={})
    participants = relationship('User', secondary=thread_participants, back_populates='threads')

class Message(Base):
    __tablename__ = "messages"

    id = Column(String(64), primary_key=True, index=True)  # Specify length for VARCHAR
    assistant_id = Column(String(64), index=True)  # Specify length for VARCHAR
    attachments = Column(JSON, default=[])
    completed_at = Column(Integer, nullable=True)
    content = Column(JSON, nullable=False)
    created_at = Column(Integer, nullable=False)
    incomplete_at = Column(Integer, nullable=True)
    incomplete_details = Column(JSON, nullable=True)
    meta_data = Column(JSON, nullable=False, default={})  # renamed metadata to meta_data
    object = Column(String(64), nullable=False)  # Specify length for VARCHAR
    role = Column(String(32), nullable=False)  # Specify length for VARCHAR
    run_id = Column(String(64), nullable=True)  # Specify length for VARCHAR
    status = Column(String(32), nullable=True)  # Specify length for VARCHAR
    thread_id = Column(String(64), nullable=False)  # Specify length for VARCHAR
    sender_id = Column(String(64), nullable=False)  # Specify length for VARCHAR

class Run(Base):
    __tablename__ = "runs"

    id = Column(String(64), primary_key=True)  # Specify length for VARCHAR
    assistant_id = Column(String(64), nullable=False)  # Specify length for VARCHAR
    cancelled_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(Integer, default=lambda: int(time.time()))
    expires_at = Column(Integer, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    incomplete_details = Column(String(256), nullable=True)  # Specify length for VARCHAR
    instructions = Column(String(1024), nullable=True)  # Specify length for VARCHAR
    last_error = Column(String(256), nullable=True)  # Specify length for VARCHAR
    max_completion_tokens = Column(Integer, nullable=True)
    max_prompt_tokens = Column(Integer, nullable=True)
    meta_data = Column(JSON, nullable=True)  # renamed metadata to meta_data
    model = Column(String(64), nullable=True)  # Specify length for VARCHAR
    object = Column(String(64), nullable=False)  # Specify length for VARCHAR
    parallel_tool_calls = Column(Boolean, default=False)
    required_action = Column(String(256), nullable=True)  # Specify length for VARCHAR
    response_format = Column(String(64), nullable=True)  # Specify length for VARCHAR
    started_at = Column(DateTime, nullable=True)
    status = Column(String(32), nullable=False)  # Specify length for VARCHAR
    thread_id = Column(String(64), nullable=False)  # Specify length for VARCHAR
    tool_choice = Column(String(64), nullable=True)  # Specify length for VARCHAR
    tools = Column(JSON, nullable=True)  # Updated to be JSON
    truncation_strategy = Column(JSON, nullable=True)
    usage = Column(JSON, nullable=True)
    temperature = Column(Integer, nullable=True)
    top_p = Column(Integer, nullable=True)
    tool_resources = Column(JSON, nullable=True)
