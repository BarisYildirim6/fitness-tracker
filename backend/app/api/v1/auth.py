from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.session import get_db
from app.schemas.user import LoginRequest, Token, UserRegister, UserWithProfileRead
from app.services.users import authenticate_user, create_user, get_user_by_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserWithProfileRead, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Annotated[Session, Depends(get_db)]) -> UserWithProfileRead:
    if get_user_by_email(db, str(user_in.email)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

    try:
        return create_user(db, user_in)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered") from exc


@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> Token:
    user = authenticate_user(db, str(credentials.email), credentials.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    return Token(access_token=create_access_token(user.id))
