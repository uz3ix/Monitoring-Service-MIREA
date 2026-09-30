from datetime import datetime
from typing import cast
from sqlalchemy import delete, func, select
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session
from app.modules.metrics.models import Metrics
from app.modules.metrics.schemas import MetricsCreate

NUMERIC_FIELDS = (
    "cpu_percent",
    "memory_used_bytes",
    "memory_total_bytes",
    "disk_used_bytes",
    "disk_total_bytes",
)


def get_latest_metrics(db: Session, device_id: int, cutoff: datetime) -> Metrics | None:
    return db.scalar(
        select(Metrics)
        .where(Metrics.device_id == device_id, Metrics.collected_at >= cutoff)
        .order_by(Metrics.collected_at.desc(), Metrics.id.desc())
        .limit(1)
    )


def create_metrics(db: Session, device_id: int, data: MetricsCreate, received_at: datetime) -> Metrics:
    metric = Metrics(device_id=device_id, received_at=received_at, **data.model_dump())
    db.add(metric)
    db.flush()
    return metric


def history_rows(db: Session, device_id: int, start: datetime, end: datetime, step: int):
    bucket = func.floor((func.extract("epoch", Metrics.collected_at) - start.timestamp()) / step).label("bucket")
    statement = (
        select(
            bucket,
            func.count().label("samples"),
            *(func.avg(getattr(Metrics, field)).label(field) for field in NUMERIC_FIELDS),
            func.max(Metrics.cpu_percent).label("cpu_max_percent"),
        )
        .where(
            Metrics.device_id == device_id,
            Metrics.collected_at >= start,
            Metrics.collected_at < end,
        ).group_by(bucket).order_by(bucket)
    )
    return db.execute(statement).mappings().all()


def get_latest_metrics_for_devices(db: Session, device_ids: list[int], cutoff: datetime) -> list[Metrics]:
    if not device_ids:
        return []
    statement = (
        select(Metrics)
        .where(Metrics.device_id.in_(device_ids), Metrics.collected_at >= cutoff)
        .distinct(Metrics.device_id)
        .order_by(Metrics.device_id, Metrics.collected_at.desc(), Metrics.id.desc())
    )
    return list(db.scalars(statement).all())


def delete_device_metrics(db: Session, device_id: int) -> None:
    db.execute(delete(Metrics).where(Metrics.device_id == device_id))


def delete_expired_metrics(db: Session, cutoff: datetime) -> int:
    result = db.execute(delete(Metrics).where(Metrics.collected_at < cutoff))
    return cast(CursorResult, result).rowcount
