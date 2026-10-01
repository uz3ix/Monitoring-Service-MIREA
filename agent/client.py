import httpx
from config import settings


def send_metrics(metrics: dict) -> None:
    base_url = settings.server_url.rstrip("/") + "/metrics"
    
    response = httpx.post(base_url, json=metrics, headers={"X-Agent-Token": settings.agent_token.get_secret_value()},
                          timeout=settings.request_timeout_seconds)
    response.raise_for_status()
    