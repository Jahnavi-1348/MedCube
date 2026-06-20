from sqlalchemy.orm import Session
from models import User, UserRole
from schemas import UserRegister
from service.auth import hash_password
import logging

logger = logging.getLogger(__name__)


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_all_users(db: Session) -> list[User]:
    return db.query(User).all()


def create_user(db: Session, user_data: UserRegister) -> User:
    hashed = hash_password(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed,
        role=user_data.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"Created user '{db_user.username}' with role '{db_user.role}'")
    return db_user


def deactivate_user(db: Session, username: str) -> User | None:
    user = get_user_by_username(db, username)
    if not user:
        return None
    user.is_active = False
    db.commit()
    db.refresh(user)
    logger.info(f"Deactivated user '{username}'")
    return user