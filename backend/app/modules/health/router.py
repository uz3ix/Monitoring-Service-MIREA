from fastapi import APIRouter, HTTPException, Depends
from app.modules.health.service import get_health, check_database
from app.modules.health.schemas import HealthResponse
from sqlalchemy.orm import Session
from app.db.session import get_db


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return get_health()


@router.get("/health/database", response_model=HealthResponse, )
def health_database(db: Session = Depends(get_db)) -> HealthResponse:
    if not check_database(db):
        raise HTTPException(status_code=503, detail="Database unavailable")
    return HealthResponse(status="ok")
