from fastapi import APIRouter, Depends, HTTPException
from app.modules.metrics.schemas import MetricsResponse
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.modules.metrics.models import Metrics
from app.modules.metrics.service import (
    get_latest_metrics as get_latest_metrics_service
)

router = APIRouter()


@router.get("/devices/{device_id}/metrics/latest", response_model=MetricsResponse, status_code=200, tags=["Metrics"])
def get_metrics_by_device_id(device_id: int, db: Session = Depends(get_db)) -> Metrics | None:
    result = get_latest_metrics_service(db, device_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Metrics not found")
    return result
