from typing import Annotated

from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.security import create_access_token
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest,LoginRequest,TokenResponse
from app.schemas.user import UserRead
from app.services.auth_service import register_user,authenticate_user
from app.services.user_service import DuplicateUserError



router=APIRouter(prefix="/auth",tags=["authentication"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register(user_data:RegisterRequest, db:Annotated[Session,Depends(get_db)])-> User:
    try:
        return register_user(db,user_data)
    except DuplicateUserError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=str(exc),)from exc
    
    
    
@router.post("/login",response_model=TokenResponse)
def login(
    credentials:LoginRequest,
    db:Annotated[Session,Depends(get_db)],
)-> TokenResponse:
    user=authenticate_user(
        db,
        email=str(credentials.email),
        password=credentials.password,
    )
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token=create_access_token(subject=str(user.id))
    
    return TokenResponse(access_token=access_token)



@router.get("/me",response_model=UserRead)
def read_current_user(
    current_user:Annotated[User,Depends(get_current_user)],
)-> User:
    """return the profile of the authenticated user."""
    return current_user