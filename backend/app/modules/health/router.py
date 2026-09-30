from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.modules.health.schemas import HealthResponse
from app.modules.health.service import (
    check_database as check_database_service,
    get_health as get_health_service
)

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check() -> HealthResponse:
    return get_health_service()


@router.get("/health/database", response_model=HealthResponse, tags=["Health"])
def health_database(db: Session = Depends(get_db)) -> HealthResponse:
    if not check_database_service(db):
        raise HTTPException(status_code=503, detail="Database unavailable")
    return HealthResponse(status="ok")
