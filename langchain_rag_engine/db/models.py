from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True, default=None)
    avatar_url = Column(String, nullable=True, default=None)
    bio = Column(Text, nullable=True, default=None)
    phone_number = Column(String, nullable=True, default=None)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    oauth_provider = Column(String, nullable=True, default=None)  # 'google' or 'github'
    oauth_id = Column(String, nullable=True, default=None)  # OAuth provider's user ID
    last_login = Column(DateTime(timezone=True), nullable=True, default=None)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), default=None)

    conversations = relationship("Conversation", back_populates="owner")
    feedback = relationship("Feedback", back_populates="user")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    type = Column(String) # "user" or "assistant"
    content = Column(Text)
    source = Column(String, nullable=True) # e.g., "vector_db", "fallback_llm", "cancelled"
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")
    feedback = relationship("Feedback", back_populates="message")

class Judgment(Base):
    __tablename__ = "judgments"

    id = Column(Integer, primary_key=True, index=True)
    case_title = Column(String, index=True)
    judgment_date = Column(String)
    year = Column(Integer, index=True)
    citation = Column(String)
    judges = Column(String)
    headnotes = Column(Text)
    full_text = Column(Text)
    source_file = Column(String)

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(String) # "helpful" or "not_helpful"
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    message = relationship("Message", back_populates="feedback")
    user = relationship("User", back_populates="feedback")
