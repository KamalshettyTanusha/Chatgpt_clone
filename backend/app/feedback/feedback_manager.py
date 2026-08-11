from sqlalchemy.orm import Session

from app.database.models import Feedback



def save_feedback(
    db: Session,
    message_id: int,
    user_id: int,
    feedback_type: str,
    comment: str = None
):
    """
    Saves user feedback for a response.
    """

    feedback = Feedback(
        message_id=message_id,
        user_id=user_id,
        feedback_type=feedback_type,
        comment=comment
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return feedback



def get_message_feedback(
    db: Session,
    message_id: int
):
    """
    Fetch feedback for a message.
    """

    feedback = (
        db.query(Feedback)
        .filter(
            Feedback.message_id == message_id
        )
        .all()
    )

    return feedback