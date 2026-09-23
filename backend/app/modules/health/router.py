from fastapi import APIRouter
from app.modules.health.service import get_health
from app.modules.health.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return get_health()
