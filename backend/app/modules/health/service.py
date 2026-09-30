from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.modules.health.schemas import HealthResponse
from app.modules.health.repository import (
    check_database as check_database_record
)


def get_health() -> HealthResponse:
    answer = HealthResponse(status="ok")
    return answer


def check_database(db: Session) -> bool:
    try:
        return check_database_record(db)
    except SQLAlchemyError:
        return False
