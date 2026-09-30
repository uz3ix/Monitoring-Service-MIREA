from datetime import datetime
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from app.modules.auth.models import User, UserSession


def has_users(db: Session) -> bool:
    return db.scalar(select(User.id).limit(1)) is not None


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def create_user(db: Session, username: str, password_hash: str) -> User:
    user = User(username=username, password_hash=password_hash)
    db.add(user)
    db.flush()
    return user


def create_session(db: Session, token_hash: str, user_id: int, expires_at: datetime) -> UserSession:
    session = UserSession(token_hash=token_hash, user_id=user_id, expires_at=expires_at)
    db.add(session)
    db.flush()
    return session


def get_active_session(db: Session, token_hash: str, now: datetime) -> UserSession | None:
    statement = select(UserSession).where(
        UserSession.token_hash == token_hash,
        UserSession.expires_at > now,
    )
    return db.scalar(statement)


def delete_session(db: Session, session: UserSession) -> None:
    db.delete(session)
    db.flush()


def delete_expired_sessions(db: Session, now: datetime) -> None:
    db.execute(delete(UserSession).where(UserSession.expires_at <= now))
