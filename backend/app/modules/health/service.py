from app.modules.health.schemas import HealthResponse
from sqlalchemy import text
from app.db.session import engine
from sqlalchemy.exc import SQLAlchemyError


def get_health() -> HealthResponse:
    answer = HealthResponse(status="ok")
    return answer


def check_database() -> bool:
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1;")).scalar()

            return result == 1
    except SQLAlchemyError:
        return False
