from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MetricsResponse(BaseModel):
    id: int
    device_id: int
    collected_at: datetime
    received_at: datetime
    cpu_percent: float | None
    memory_used_bytes: int | None
    memory_total_bytes: int | None
    disk_used_bytes: int | None
    disk_total_bytes: int | None
    services: dict[str, str] | None
    
    model_config = ConfigDict(from_attributes=True)