from __future__ import annotations

import hashlib
import os
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .errors import ApiError
from .models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return hashlib.sha256(f"tripcare::{password}".encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def create_access_token(user: User) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": user.email,
        "role": user.role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=8)).timestamp()),
    }
    return jwt.encode(
        payload,
        os.getenv("JWT_SECRET", "local-demo-secret"),
        algorithm=JWT_ALGORITHM,
    )


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(
            token,
            os.getenv("JWT_SECRET", "local-demo-secret"),
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.PyJWTError as exc:
        raise ApiError(401, "UNAUTHORIZED", "Invalid or expired token") from exc

    email = payload.get("sub")
    user = db.scalar(select(User).where(User.email == email, User.active.is_(True)))
    if user is None:
        raise ApiError(401, "UNAUTHORIZED", "User is not active or does not exist")
    return user


def require_roles(*roles: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise ApiError(403, "FORBIDDEN", "Role does not allow this operation")
        return user

    return dependency
