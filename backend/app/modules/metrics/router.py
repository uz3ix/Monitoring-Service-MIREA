from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import AwareDatetime
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.modules.auth.dependencies import current_agent, current_user
from app.modules.devices.models import Device
from app.modules.metrics.schemas import MetricsCreate, MetricsHistory, MetricsResponse
from app.modules.metrics.service import (
    get_history as get_history_service,
    get_latest_metrics as get_latest_metrics_service,
    ingest_metrics as ingest_metrics_service
)

router = APIRouter(tags=["Metrics"])


@router.post("/metrics", response_model=MetricsResponse, status_code=201)
def receive_metrics(data: MetricsCreate, device: Device = Depends(current_agent), db: Session = Depends(get_db)):
    return ingest_metrics_service(db, device, data)


@router.get("/devices/{device_id}/metrics/latest", response_model=MetricsResponse, dependencies=[Depends(current_user)])
def latest_metrics(device_id: int, db: Session = Depends(get_db)):
    metric = get_latest_metrics_service(db, device_id)
    if metric is None:
        raise HTTPException(404, "Metrics not found")
    return metric


@router.get("/devices/{device_id}/metrics", response_model=MetricsHistory, dependencies=[Depends(current_user)])
def metrics_history(
    device_id: int,
    start: AwareDatetime | None = None,
    end: AwareDatetime | None = None,
    max_points: int = Query(default=500, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    return get_history_service(db, device_id, start, end, max_points)
