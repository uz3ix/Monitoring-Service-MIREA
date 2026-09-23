from app.modules.health.schemas import HealthResponse


def get_health() -> HealthResponse:
    answer = HealthResponse(status="ok")
    return answer
