from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from db.database import Base
from utils.generate_uid import generate_uuid

thread_participants = Table('thread_participants', Base.metadata,
    Column('thread_id', Integer, ForeignKey('threads.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class Thread(Base):
    __tablename__ = 'threads'
    id = Column(Integer, primary_key=True, index=True)
    id = Column(String(255), primary_key=True, default=generate_uuid)
    title = Column(String, index=True)
    participants = relationship('User', secondary=thread_participants, back_populates='threads')
    messages = relationship('Message', back_populates='thread')

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    threads = relationship('Thread', secondary=thread_participants, back_populates='participants')

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, index=True)
    sender_id = Column(Integer, ForeignKey('users.id'))
    thread_id = Column(Integer, ForeignKey('threads.id'))
    thread = relationship('Thread', back_populates='messages')
    sender = relationship('User')
