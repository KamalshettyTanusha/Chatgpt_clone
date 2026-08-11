from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.crud import (
    create_user,
    get_user_by_username
)

from app.auth.password_utils import (
    hash_password,
    verify_password
)

from app.auth.jwt_handler import create_access_token


def register_user(
    username: str,
    password: str,
    db: Session
):
    """
    Register a new user.
    """

    existing_user = get_user_by_username(db, username)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists."
        )

    hashed_password = hash_password(password)

    user = create_user(
        db=db,
        username=username,
        password=hashed_password
    )

    return {
        "message": "User registered successfully.",
        "user_id": user.id
    }


def login_user(
    username: str,
    password: str,
    db: Session
):
    """
    Authenticate a user and generate a JWT token.
    """

    user = get_user_by_username(db, username)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password."
        )

    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password."
        )

    access_token = create_access_token(
        {
            "username": user.username
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }