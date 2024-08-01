from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class UserBase(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True
        from_attributes = True

class UserCreate(BaseModel):
    name: Optional[str] = "Anonymous User"

class UserRead(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None

class ThreadCreate(BaseModel):
    participant_ids: Optional[List[str]] = None
    meta_data: Optional[Dict[str, Any]] = {}

class ThreadRead(BaseModel):
    id: str
    created_at: int
    meta_data: Dict[str, Any]
    object: str
    tool_resources: Dict[str, Any]

    class Config:
        orm_mode = True
        from_attributes = True

class ThreadParticipant(UserBase):
    pass

class ThreadReadDetailed(ThreadRead):
    participants: List[UserBase]

    class Config:
        orm_mode = True
        from_attributes = True

class MessageCreate(BaseModel):
    content: str
    thread_id: str
    sender_id: str
    role: str = "user"
    meta_data: Optional[Dict[str, Any]] = {}

    class Config:
        schema_extra = {
            "example": {
                "content": "Hello, this is a test message.",
                "thread_id": "example_thread_id",
                "sender_id": "example_sender_id",
                "meta_data": {"key": "value"},
                "role": "user"
            }
        }
class MessageRead(BaseModel):
    id: str
    assistant_id: Optional[str]
    attachments: List[Any]
    completed_at: Optional[int]
    content: str  # Changed from List[Content] to str
    created_at: int
    incomplete_at: Optional[int]
    incomplete_details: Optional[Dict[str, Any]]
    meta_data: Dict[str, Any]
    object: str
    role: str
    run_id: Optional[str]
    status: Optional[str]
    thread_id: str
    sender_id: str

    class Config:
        orm_mode = True
        from_attributes = True

class Tool(BaseModel):
    type: str
    function: Optional[Dict[str, Any]] = None
    file_search: Optional[Any] = None


class Run(BaseModel):
    id: str
    assistant_id: str
    cancelled_at: Optional[int]
    completed_at: Optional[int]
    created_at: int
    expires_at: int
    failed_at: Optional[int]
    incomplete_details: Optional[Dict[str, Any]]
    instructions: str
    last_error: Optional[str]
    max_completion_tokens: Optional[int]
    max_prompt_tokens: Optional[int]
    meta_data: Dict[str, Any]
    model: str
    object: str
    parallel_tool_calls: bool
    required_action: Optional[str]
    response_format: str
    started_at: Optional[int]
    status: str
    thread_id: str
    tool_choice: str
    tools: List[Tool]
    truncation_strategy: Dict[str, Any]
    usage: Optional[Any]
    temperature: float
    top_p: float
    tool_resources: Dict[str, Any]

    class Config:
        orm_mode = True
        from_attributes = True


class AssistantCreate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    model: str
    instructions: Optional[str] = None
    tools: Optional[List[Tool]] = None
    meta_data: Optional[Dict[str, Any]] = {}
    top_p: Optional[float] = 1.0
    temperature: Optional[float] = 1.0
    response_format: Optional[str] = "auto"


class AssistantRead(BaseModel):
    id: str
    object: str
    created_at: int
    name: str
    description: Optional[str]
    model: str
    instructions: Optional[str]
    tools: Optional[List[Tool]]
    meta_data: Dict[str, Any]
    top_p: float
    temperature: float
    response_format: str

    class Config:
        orm_mode = True
        from_attributes = True