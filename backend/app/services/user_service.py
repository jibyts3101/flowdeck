
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class DuplicateUserError(Exception):
    """Raised when a username or email is already in use."""


def get_all_users(db: Session) -> list[User]:
    statement = select(User)
    return list(db.scalars(statement).all())


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def create_user(db: Session, user_data: UserCreate) -> User:
    new_user = User(
        username=user_data.username,
        email=str(user_data.email),
        full_name=user_data.full_name,
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateUserError(
            "Username or email already exists"
        ) from exc

    return new_user


def update_user(
    db: Session,
    user_id: int,
    user_data: UserUpdate,
) -> User | None:
    user = db.get(User, user_id)

    if user is None:
        return None

    update_data=user_data.model_dump(exclude_unset=True)
    
    for field,value in update_data.items():
        if field in {"username","email"} and value is None:
            continue
        
        if field=="email" and value is not None:
            value=str(value)
            
        setattr(user,field,value)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateUserError(
            "Username or email already exists"
        ) from exc

    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = db.get(User, user_id)

    if user is None:
        return False

    db.delete(user)
    db.commit()

    return True
