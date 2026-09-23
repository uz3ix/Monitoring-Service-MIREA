from fastapi import APIRouter, HTTPException
from app.modules.health.service import get_health, check_database
from app.modules.health.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return get_health()


@router.get("/health/database", response_model=HealthResponse)
def health_database() -> HealthResponse:
    if not check_database():
        raise HTTPException(status_code=503, detail="Database unavailable")
    return HealthResponse(status="ok")
