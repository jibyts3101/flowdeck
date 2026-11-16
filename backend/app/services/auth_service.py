from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


from app.core.security import hash_password,verify_password
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.services.user_service import DuplicateUserError



def register_user(db:Session, user_data:RegisterRequest)->User:
    """Register a user after securely hashing their password."""
    new_user=User(
    username=user_data.username,
    email=str(user_data.email),
    full_name=user_data.full_name,
    password_hash=hash_password(user_data.password),
    )
    
    db.add(new_user)
    
    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError as exc:
        db.rollback
        raise DuplicateUserError(
            "Username is already exist"
        ) from exc
        
    return new_user


def authenticate_user(
    db:Session,
    email:str,
    password:str
)->User|None:
    """Return the user if the email and password are valid"""
    user=db.query(User).filter(User.email==email).first()
    
    if user is None or user.password_hash is None:
        return None
    if not verify_password(password,user.password_hash):
        return None
    
    
    return user