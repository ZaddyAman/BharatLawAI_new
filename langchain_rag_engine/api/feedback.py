from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import crud, schemas
from db.database import SessionLocal
from .auth import get_current_user

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/feedback", response_model=schemas.Feedback)
def create_feedback_for_message(
    feedback: schemas.FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    return crud.create_feedback(db=db, feedback=feedback, user_id=current_user.id)
