from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserProfile
from app.schemas.user import UserProfileCreate, UserRegister


def get_user_by_email(db: Session, email: str) -> User | None:
    normalized_email = email.strip().lower()
    return db.scalar(select(User).where(User.email == normalized_email))


def create_user(db: Session, user_in: UserRegister) -> User:
    user = User(
        email=str(user_in.email).strip().lower(),
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    db.flush()

    if user_in.profile is not None:
        user.profile = UserProfile(**user_in.profile.model_dump())

    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user_profile(db: Session, user: User, profile_in: UserProfileCreate) -> UserProfile:
    profile = UserProfile(user_id=user.id, **profile_in.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile
