from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: UUID, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(UTC) + (
        expires_delta if expires_delta is not None else timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> UUID | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        subject = payload.get("sub")
        return UUID(subject) if subject else None
    except (JWTError, ValueError, TypeError):
        return None
