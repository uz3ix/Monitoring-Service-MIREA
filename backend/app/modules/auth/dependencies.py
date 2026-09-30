from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.modules.auth.models import User, UserSession
from app.modules.devices.models import Device
from app.modules.auth.service import (
    get_active_session as get_active_session_service,
    get_user_by_id as get_user_by_id_service,
)
from app.modules.devices.service import (
    get_device_by_token as get_device_by_token_service,
)

bearer = HTTPBearer(auto_error=False, scheme_name="UserSession")
agent_header = APIKeyHeader(name="X-Agent-Token", auto_error=False, scheme_name="AgentToken")


def current_session(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> UserSession:
    if credentials:
        session = get_active_session_service(db, credentials.credentials)
        if session:
            return session
    raise HTTPException(401, "Authentication required", headers={"WWW-Authenticate": "Bearer"})


def current_user(
    session: UserSession = Depends(current_session), db: Session = Depends(get_db)
) -> User:
    user = get_user_by_id_service(db, session.user_id)
    if not user:
        raise HTTPException(401, "Authentication required", headers={"WWW-Authenticate": "Bearer"})
    return user


def current_agent(
    token: str | None = Depends(agent_header), db: Session = Depends(get_db)
) -> Device:
    if token and 32 <= len(token) <= 128:
        device = get_device_by_token_service(db, token)
        if device:
            return device
    raise HTTPException(401, "Invalid agent token")
