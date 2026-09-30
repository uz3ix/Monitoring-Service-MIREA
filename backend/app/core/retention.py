import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.core.time import retention_cutoff, utcnow
from app.db.session import SessionLocal
from app.modules.auth.repository import (
    delete_expired_sessions as delete_expired_sessions_record,
)
from app.modules.metrics.repository import (
    delete_expired_metrics as delete_expired_metrics_record,
)

logger = logging.getLogger(__name__)


def cleanup(db: Session) -> int:
    try:
        deleted = delete_expired_metrics_record(db, retention_cutoff())
        delete_expired_sessions_record(db, utcnow())
        db.commit()
        return deleted
    except SQLAlchemyError:
        db.rollback()
        raise


def cleanup_once() -> None:
    try:
        with SessionLocal() as db:
            cleanup(db)
    except Exception as error:
        # Do not log SQL parameters or credentials.
        logger.warning("Cleanup failed (%s); retry on next interval", type(error).__name__)
