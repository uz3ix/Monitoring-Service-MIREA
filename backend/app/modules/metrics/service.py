from sqlalchemy.orm import Session
from app.modules.metrics.models import Metrics
from app.modules.metrics.repository import (
    get_latest_metrics as get_latest_metrics_record
)

def get_latest_metrics(db: Session, device_id: int) -> Metrics | None:
    return get_latest_metrics_record(db, device_id)
