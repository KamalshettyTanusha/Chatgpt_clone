from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_current_user
)

from app.database.database import (
    get_db
)

from app.history.thread_manager import (
    create_thread,
    get_user_threads,
    get_thread
)

from app.history.history_manager import (
    get_chat_history
)


router = APIRouter(
    prefix="/history",
    tags=["History"]
)


@router.post("/new-chat")
def new_chat(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return create_thread(
        db=db,
        user_id=current_user.id
    )


@router.get("/chats")
def get_chats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return get_user_threads(
        db=db,
        user_id=current_user.id
    )


@router.get("/{chat_id}")
def get_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    chat = get_thread(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id
    )

    if chat is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Chat not found for the "
                "authenticated user."
            )
        )

    return get_chat_history(
        db=db,
        chat_id=chat_id
    )