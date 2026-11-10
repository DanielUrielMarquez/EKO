from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models import User


def get_user_by_email(db: Session, email: str) -> User | None:
    normalized_email = email.strip().lower()

    statement = select(User).where(User.email == normalized_email)

    return db.scalar(statement)


def create_user(db: Session, email: str, password: str) -> User | None:
    normalized_email = email.strip().lower()

    existing_user = get_user_by_email(db, normalized_email)

    if existing_user:
        return None

    user = User(
        email=normalized_email,
        hashed_password=hash_password(password),
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        return None

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:
    user = get_user_by_email(db, email)

    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    if not user.is_active:
        return None

    return user