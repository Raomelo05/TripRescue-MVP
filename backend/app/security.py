import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()
ALGORITHM = "HS256"
TOKEN_LIFETIME = timedelta(minutes=30)


def get_secret() -> str:
    secret = os.getenv("SECRET_KEY")
    if not secret:
        raise RuntimeError("SECRET_KEY environment variable is required")
    return secret


def create_access_token(user_id: UUID) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {"sub": str(user_id), "iat": now, "exp": now + TOKEN_LIFETIME},
        get_secret(),
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> UUID:
    payload = jwt.decode(token, get_secret(), algorithms=[ALGORITHM])
    return UUID(payload["sub"])
