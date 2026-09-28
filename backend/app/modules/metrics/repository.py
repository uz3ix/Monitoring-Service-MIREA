from app.modules.metrics.models import Metrics
from sqlalchemy.orm import Session
from sqlalchemy import select


def get_latest_metrics(db: Session, device_id: int) -> Metrics | None:
    statement = select(Metrics).where(Metrics.device_id == device_id).order_by(Metrics.collected_at.desc(), Metrics.id.desc()).limit(1)
    return db.scalar(statement)
    