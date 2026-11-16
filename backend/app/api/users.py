
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.user import UserRead, UserUpdate
from app.services.user_service import (
    get_all_users,
    get_user_by_id,
    update_user as update_user_service,
    delete_user as delete_user_service,
    DuplicateUserError,
)

router = APIRouter(prefix="/users", tags=["users"])


# Get all users
@router.get("/", response_model=list[UserRead])
def list_users(
    db: Annotated[Session, Depends(get_db)],
):
    return get_all_users(db)


# Get one user
@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    user = get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


# Update user details
@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    try:
        user = update_user_service(db, user_id, user_data)
    except DuplicateUserError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


# Delete user
@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    deleted = delete_user_service(db, user_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return Response(status_code=204)
