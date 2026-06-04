from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.user import UserProfile
from app.schemas.user import UserProfileCreate, UserProfileRead, UserProfileUpdate, UserWithProfileRead
from app.services.users import create_user_profile

router = APIRouter(tags=["users"])


@router.get("/me", response_model=UserWithProfileRead)
def read_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserWithProfileRead:
    return current_user


@router.post("/me/profile", response_model=UserProfileRead, status_code=status.HTTP_201_CREATED)
def create_my_profile(
    profile_in: UserProfileCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UserProfileRead:
    if current_user.profile is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Profile already exists")

    try:
        return create_user_profile(db, current_user, profile_in)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Profile already exists") from exc


@router.put("/me/profile", response_model=UserProfileRead)
def update_my_profile(
    profile_in: UserProfileUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UserProfileRead:
    profile = current_user.profile
    if profile is None:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    for field, value in profile_in.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile
