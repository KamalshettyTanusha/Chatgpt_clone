from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.database import get_db
from app.feedback.feedback_manager import save_feedback
from app.feedback.retry_handler import retry_with_different_model
from app.schemas.feedback_schema import (
    FeedbackRequest,
    RetryRequest
)


router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"]
)


@router.post("/")
def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Save user feedback.
    """

    return save_feedback(
        db=db,
        message_id=request.message_id,
        user_id=current_user.id,
        feedback_type=request.feedback_type,
        comment=request.comment
    )



@router.post("/retry")
def retry_response(
    request: RetryRequest,
    current_user=Depends(get_current_user)
):
    """
    Retry using a fallback model.
    """

    return retry_with_different_model(
        query=request.query,
        memory=request.memory,
        previous_model=request.previous_model
    )