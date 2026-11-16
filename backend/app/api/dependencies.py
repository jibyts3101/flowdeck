from typing import Annotated

import jwt
from fastapi import Depends,HTTPException,status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session


from app.core.config import settings
from app.core.security import ALGORITHM
from app.db.dependencies import get_db
from app.models.user import User

bearer_scheme=HTTPBearer(auto_error=False)


def get_current_user(
    credentials:Annotated[
        HTTPAuthorizationCredentials|None,
        Depends(bearer_scheme),
    ],
    db:Annotated[Session,Depends(get_db)]
)-> User:
    """Validate the JWT and return its assiocated user."""

    unauthorized=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    
    if credentials is None:
        raise unauthorized

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject.isdigit():
            raise unauthorized

        user = db.get(User, int(subject))
        if user is None:
            raise unauthorized

        return user

    except jwt.InvalidTokenError:
        raise unauthorized from None

