from sqlalchemy.orm import Session

from app.database.models import User
from app.auth.password import (
    hash_password,
    verify_password
)
from app.auth.jwt_handler import (
    create_access_token
)


def register_user(
    db: Session,
    username: str,
    email: str,
    password: str
):
    """
    Registers a new user.
    """

    # Check username

    existing_user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if existing_user:

        return {
            "success": False,
            "message": "Username already exists."
        }


    # Check email

    existing_email = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_email:

        return {
            "success": False,
            "message": "Email already exists."
        }


    # Create user

    user = User(

        username=username,

        email=email,

        password_hash=hash_password(password)

    )

    db.add(user)

    db.commit()

    db.refresh(user)


    return {

        "success": True,

        "message": "Registration successful."

    }



def login_user(
    db: Session,
    email: str,
    password: str
):
    """
    Authenticates a user.
    """

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


    if not user:

        return {

            "success": False,

            "message": "Invalid email or password."

        }


    if not verify_password(
        password,
        user.password_hash
    ):

        return {

            "success": False,

            "message": "Invalid email or password."

        }


    token = create_access_token(

        {
            "user_id": user.id
        }

    )


    return {

        "success": True,

        "access_token": token,

        "token_type": "bearer",

        "user": {

            "id": user.id,

            "username": user.username,

            "email": user.email

        }

    }