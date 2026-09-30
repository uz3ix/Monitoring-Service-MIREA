import math
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.core.time import retention_cutoff, utcnow
from app.modules.devices.models import Device
from app.modules.metrics.models import Metrics
from app.modules.devices.repository import (
    get_device_by_id as get_device_by_id_record,
    get_device_for_update as get_device_for_update_record,
    update_last_seen as update_last_seen_record
)
from app.modules.metrics.repository import (
    create_metrics as create_metrics_record,
    history_rows as history_rows_record,
    get_latest_metrics as get_latest_metrics_record
)
from app.modules.metrics.schemas import HistoryPoint, MetricsCreate, MetricsHistory


def get_latest_metrics(db: Session, device_id: int) -> Metrics | None:
    if get_device_by_id_record(db, device_id) is None:
        raise HTTPException(404, "Device not found")
    return get_latest_metrics_record(db, device_id, retention_cutoff())


def ingest_metrics(db: Session, device: Device, data: MetricsCreate) -> Metrics:
    received_at = utcnow()
    authenticated_hash = device.agent_token_hash
    try:
        locked = get_device_for_update_record(db, device.id)
        if locked is None or locked.agent_token_hash != authenticated_hash:
            db.rollback()
            raise HTTPException(401, "Invalid agent token")
        metric = create_metrics_record(db, device.id, data, received_at)
        update_last_seen_record(db, device.id, received_at)
        db.commit()
        return metric
    except SQLAlchemyError:
        db.rollback()
        raise


def get_history(db: Session, device_id: int, start: datetime | None, end: datetime | None, max_points: int) -> MetricsHistory:
    if get_device_by_id_record(db, device_id) is None:
        raise HTTPException(404, "Device not found")
    end = end or utcnow()
    start = start or end - timedelta(hours=24)
    if start >= end:
        raise HTTPException(422, "Start must be before end")
    if end > utcnow() + timedelta(minutes=5):
        raise HTTPException(422, "End is too far in the future")
    cutoff = retention_cutoff()
    if end <= cutoff:
        return MetricsHistory(device_id=device_id, start=start, end=end, step_seconds=1, points=[])
    start = max(start, cutoff)
    step = max(1, math.ceil((end - start).total_seconds() / max_points))
    rows = history_rows_record(db, device_id, start, end, step)
    points = [
        HistoryPoint(
            bucket_start=start + timedelta(seconds=int(row["bucket"]) * step),
            **{key: value for key, value in row.items() if key != "bucket"},
        )
        for row in rows
    ]
    return MetricsHistory(
        device_id=device_id, start=start, end=end, step_seconds=step, points=points
    )
