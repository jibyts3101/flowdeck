from datetime import datetime, timedelta, timezone
from app.core.config import settings    

import jwt
from pwdlib import PasswordHash


password_hash=PasswordHash.recommended()

ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

def hash_password(password:str)->str:
    """covert a plain text password to secure password hash."""
    return password_hash.hash(password)

def verify_password(password:str,hashed_password:str)->bool:
    """check a password against its stored hash."""
    return password_hash.verify(password,hashed_password)



def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token."""
    now = datetime.now(timezone.utc)

    expires_at = now + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload = {
        "sub": subject,
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )
