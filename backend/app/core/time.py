from datetime import datetime, timedelta, timezone
from app.core.config import settings


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def retention_cutoff() -> datetime:
    return utcnow() - timedelta(days=settings.retention_days)
