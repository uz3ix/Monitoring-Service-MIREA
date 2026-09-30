from collections import OrderedDict
from threading import Lock
from time import monotonic
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.modules.auth.dependencies import current_session, current_user
from app.modules.auth.models import User, UserSession
from app.modules.auth.schemas import LoginRequest, LoginResponse, UserResponse
from app.modules.auth.service import (
    login as login_service,
    logout as logout_service
)

router = APIRouter(prefix="/auth", tags=["Auth"])
attempts: OrderedDict[str, list[float]] = OrderedDict()
attempt_lock = Lock()


def check_login_rate(address: str) -> None:
    now = monotonic()
    with attempt_lock:
        recent = [t for t in attempts.get(address, []) if t > now - 60]
        if len(recent) >= 10:
            raise HTTPException(429, "Too many login attempts", headers={"Retry-After": "60"})
        attempts[address] = recent + [now]
        attempts.move_to_end(address)
        while len(attempts) > 10000:
            attempts.popitem(last=False)


@router.post("/login", response_model=LoginResponse)
def login_user(
    data: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)
):
    check_login_rate(request.client.host if request.client else "unknown")
    token = login_service(db, data.username, data.password.get_secret_value())
    if token is None:
        raise HTTPException(401, "Invalid username or password")
    response.headers["Cache-Control"] = "no-store"
    return LoginResponse(access_token=token, expires_in=settings.session_hours * 3600)


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(current_user)):
    return user


@router.post("/logout", status_code=204)
def logout(session: UserSession = Depends(current_session), db: Session = Depends(get_db)):
    logout_service(db, session)
    return Response(status_code=204)
