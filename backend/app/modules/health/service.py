from app.modules.health.schemas import HealthResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


def get_health() -> HealthResponse:
    answer = HealthResponse(status="ok")
    return answer


def check_database(db: Session) -> bool:
    try:
        result = db.execute(text("SELECT 1;")).scalar()

        return result == 1
    except SQLAlchemyError:
        return False
