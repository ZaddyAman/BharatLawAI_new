from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import List, Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    full_name: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None

class User(UserBase):
    id: int
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    phone_number: Optional[str]
    is_active: bool
    email_verified: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    is_admin: Optional[bool] = None
    role: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class MessageBase(BaseModel):
    type: str
    content: str
    source: Optional[str]

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    conversation_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class ConversationBase(BaseModel):
    title: str

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    messages: List[Message] = []

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class JudgmentBase(BaseModel):
    case_title: str
    judgment_date: str
    year: int
    citation: str
    judges: str
    headnotes: str
    full_text: str
    source_file: str

class JudgmentCreate(JudgmentBase):
    pass

class Judgment(JudgmentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class FeedbackBase(BaseModel):
    message_id: int
    rating: str
    comment: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
