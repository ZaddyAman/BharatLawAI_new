from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_oauth_user(db: Session, user_data: dict):
    """Create user from OAuth provider data"""
    # Create a dummy password for OAuth users (they won't use it)
    dummy_password = get_password_hash("oauth_user_" + str(user_data.get('oauth_id', 'unknown')))

    db_user = models.User(
        email=user_data['email'],
        hashed_password=dummy_password,
        full_name=user_data.get('full_name'),
        avatar_url=user_data.get('avatar_url'),
        oauth_provider=user_data.get('oauth_provider'),
        oauth_id=user_data.get('oauth_id'),
        email_verified=True  # OAuth providers verify emails
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def update_user(db: Session, user_id: int, user_update):
    """Update user with either a Pydantic model or dictionary"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        # Handle both Pydantic models and dictionaries
        if hasattr(user_update, 'dict'):  # Pydantic model
            update_data = user_update.dict(exclude_unset=True)
        else:  # Plain dictionary
            update_data = user_update

        for field, value in update_data.items():
            if hasattr(db_user, field):  # Only update valid fields
                setattr(db_user, field, value)

        db.commit()
        db.refresh(db_user)
    return db_user

def get_user_stats(db: Session, user_id: int):
    conversation_count = db.query(models.Conversation).filter(models.Conversation.owner_id == user_id).count()
    message_count = db.query(models.Message).join(models.Conversation).filter(models.Conversation.owner_id == user_id).count()
    feedback_count = db.query(models.Feedback).filter(models.Feedback.user_id == user_id).count()

    return {
        "conversation_count": conversation_count,
        "message_count": message_count,
        "feedback_count": feedback_count
    }

def create_conversation(db: Session, user_id: int, title: str):
    db_conversation = models.Conversation(owner_id=user_id, title=title)
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def get_conversations(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Conversation).filter(models.Conversation.owner_id == user_id).order_by(models.Conversation.created_at.desc()).offset(skip).limit(limit).all()

def get_conversation(db: Session, conversation_id: int):
    return db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()

def create_message(db: Session, conversation_id: int, message_type: str, content: str, source: str = None):
    db_message = models.Message(conversation_id=conversation_id, type=message_type, content=content, source=source)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages_for_conversation(db: Session, conversation_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Message).filter(models.Message.conversation_id == conversation_id).offset(skip).limit(limit).all()

def delete_conversation(db: Session, conversation_id: int):
    # First, delete all messages in the conversation
    db.query(models.Message).filter(models.Message.conversation_id == conversation_id).delete(synchronize_session=False)

    # Then, delete the conversation itself
    db_conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if db_conversation:
        db.delete(db_conversation)
        db.commit()
        return True
    return False

def create_judgment(db: Session, judgment: schemas.JudgmentCreate):
    db_judgment = models.Judgment(**judgment.dict())
    db.add(db_judgment)
    db.commit()
    db.refresh(db_judgment)
    return db_judgment

def get_judgments_optimized(db: Session, skip: int = 0, limit: int = 10, search_query: str = None, year: int = None, sort_by: str = None):
    """Optimized judgment queries with proper indexing and performance improvements"""

    print(f"[CRUD] get_judgments_optimized called with: search_query={search_query}, year={year}, sort_by={sort_by}, skip={skip}, limit={limit}")

    # Query full model objects for proper serialization
    query = db.query(models.Judgment)

    # Apply filters
    if search_query:
        # Use case-insensitive search for better user experience
        search_term = f"%{search_query}%"
        query = query.filter(models.Judgment.case_title.ilike(search_term))
        print(f"[CRUD] Applied search filter: '{search_query}'")

    if year:
        query = query.filter(models.Judgment.year == year)
        print(f"[CRUD] Applied year filter: {year}")

    # Get total count efficiently before applying pagination
    count_query = db.query(models.Judgment.id)
    if search_query:
        count_query = count_query.filter(models.Judgment.case_title.ilike(f"%{search_query}%"))
    if year:
        count_query = count_query.filter(models.Judgment.year == year)
    total_count = count_query.count()

    # Apply sorting with database indexes
    if sort_by == "date_asc":
        # For date sorting, first sort by year, then by a parsed date
        # Since judgment_date is stored as strings like "14 March 1950", we need special handling
        query = query.order_by(models.Judgment.year.asc(), models.Judgment.judgment_date.asc())
    elif sort_by == "date_desc":
        # Sort by year descending, then by date descending within each year
        query = query.order_by(models.Judgment.year.desc(), models.Judgment.judgment_date.desc())
    else: # Default sort by title
        query = query.order_by(models.Judgment.case_title.asc())

    # Apply pagination
    judgments = query.offset(skip).limit(limit).all()

    print(f"[CRUD] Final results: total_count={total_count}, returned_count={len(judgments)}, sort_by={sort_by}")

    return judgments, total_count

# Connection pooling and optimization
from sqlalchemy.pool import QueuePool

# Optimized database engine configuration
def create_optimized_engine(database_url: str):
    """Create optimized database engine with connection pooling"""
    return create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=10,          # Number of connections to keep open
        max_overflow=20,       # Max additional connections
        pool_timeout=30,       # Timeout for getting connection
        pool_recycle=3600,     # Recycle connections after 1 hour
        echo=False             # Disable SQL logging in production
    )

# Keep the old function for backward compatibility
def get_judgments(db: Session, skip: int = 0, limit: int = 10, search_query: str = None, year: int = None, sort_by: str = None):
    """Legacy function - use get_judgments_optimized instead"""
    return get_judgments_optimized(db, skip, limit, search_query, year, sort_by)

def get_judgment(db: Session, judgment_id: int):
    return db.query(models.Judgment).filter(models.Judgment.id == judgment_id).first()

def create_feedback(db: Session, feedback: schemas.FeedbackCreate, user_id: int):
    db_feedback = models.Feedback(**feedback.dict(), user_id=user_id)
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def delete_user(db: Session, user_id: int):
    """Delete user and all associated data"""
    # First, delete all conversations and their messages (cascade delete)
    conversations = db.query(models.Conversation).filter(models.Conversation.owner_id == user_id).all()
    for conv in conversations:
        # Delete messages first
        db.query(models.Message).filter(models.Message.conversation_id == conv.id).delete(synchronize_session=False)
        # Delete conversation
        db.delete(conv)

    # Delete feedback
    db.query(models.Feedback).filter(models.Feedback.user_id == user_id).delete(synchronize_session=False)

    # Finally, delete the user
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False