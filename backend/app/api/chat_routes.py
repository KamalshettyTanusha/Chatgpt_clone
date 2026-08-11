from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.dependencies import get_current_user
from app.schemas.chat_schema import ChatRequest
from app.services.chat_service import process_chat


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/")
def chat(
    request: ChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return process_chat(
        user=current_user,
        chat_id=request.chat_id,
        message=request.message,
        db=db
    )