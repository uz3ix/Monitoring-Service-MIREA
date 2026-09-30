import secrets
from datetime import timedelta
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import hash_agent_token, hash_password, verify_password
from app.core.time import utcnow
from app.modules.auth.models import User, UserSession
from app.modules.auth.repository import (
    has_users as has_users_record,
    create_user as create_user_record,
    get_user_by_id as get_user_by_id_record,
    get_user_by_username as get_user_by_username_record,
    create_session as create_session_record,
    get_active_session as get_active_session_record,
    delete_session as delete_session_record
)

# Equal work for a missing username and an incorrect password.
DUMMY_HASH = hash_password(secrets.token_hex(32))


def bootstrap_admin(db: Session) -> None:
    """Create the first admin; restarting never overwrites an existing password."""
    if settings.admin_password is None:
        return
    if has_users_record(db):
        return
    password = settings.admin_password.get_secret_value()
    if len(password) < 12 or len(password) > 256:
        raise ValueError("ADMIN_PASSWORD must contain 12 to 256 characters")
    try:
        create_user_record(db, settings.admin_username, hash_password(password))
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise


def login(db: Session, username: str, password: str) -> str | None:
    user = get_user_by_username_record(db, username)
    valid = verify_password(password, user.password_hash if user else DUMMY_HASH)
    if not user or not valid:
        return None
    token = secrets.token_urlsafe(32)
    expires_at = utcnow() + timedelta(hours=settings.session_hours)
    try:
        create_session_record(db, hash_agent_token(token), user.id, expires_at)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    return token


def get_active_session(db: Session, token: str) -> UserSession | None:
    if not token or len(token) > 256:
        return None
    return get_active_session_record(db, hash_agent_token(token), utcnow())


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return get_user_by_id_record(db, user_id)


def logout(db: Session, session: UserSession) -> None:
    try:
        delete_session_record(db, session)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
