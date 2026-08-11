from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.auth_schema import (
    RegisterRequest,
    LoginRequest
)
from app.auth.auth_service import (
    register_user,
    login_user
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    """

    return register_user(
        db=db,
        username=request.username,
        email=request.email,
        password=request.password
    )



@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login user.
    """

    return login_user(
        db=db,
        email=request.email,
        password=request.password
    )