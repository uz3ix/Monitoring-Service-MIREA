from datetime import timedelta
from typing import Annotated, Self
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator
from app.core.config import settings
from app.core.time import utcnow


ByteCount = Annotated[int, Field(strict=True, ge=0, le=9223372036854775807)]
TotalBytes = Annotated[int, Field(strict=True, gt=0, le=9223372036854775807)]


class DiskMetrics(BaseModel):
    name: str = Field(min_length=1, max_length=512)
    disk_used_bytes: ByteCount
    disk_total_bytes: TotalBytes
    
    model_config = ConfigDict(extra="forbid")
    @model_validator(mode="after")
    def validate_disk(self) -> Self:
        if not self.name.strip():
            raise ValueError("Disk name cannot be blank")
        if self.disk_used_bytes > self.disk_total_bytes:
            raise ValueError("disk_used_bytes cannot exceed disk_total_bytes")
        return self
    
    
class MetricsCreate(BaseModel): 
    collected_at: AwareDatetime
    cpu_percent: float | None = Field(default=None, ge=0, le=100, allow_inf_nan=False)
    memory_used_bytes: ByteCount | None = None
    memory_total_bytes: TotalBytes | None = None
    disks: list[DiskMetrics] | None = Field(default=None, max_length=100)
    services: dict[str, str] | None = None
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_measurement(self) -> Self:
        now = utcnow()
        if (not now - timedelta(days=settings.retention_days) <= self.collected_at <= now + timedelta(minutes=5)):
            raise ValueError("collected_at is outside the allowed retention/future window")
        if (self.memory_used_bytes is not None and self.memory_total_bytes is not None and self.memory_used_bytes > self.memory_total_bytes):
            raise ValueError("memory_used_bytes cannot exceed memory_total_bytes")
        if self.services is not None:
            if len(self.services) > 100:
                raise ValueError("At most 100 services are allowed")
            if any(not name.strip() or len(name) > 128 or not state.strip() or len(state) > 64 for name, state in self.services.items()):
                raise ValueError("Service names/states must be nonempty and bounded")
        if all(
            getattr(self, field) is None
            for field in (
                "cpu_percent",
                "memory_used_bytes",
                "memory_total_bytes",
                "disks",
                "services"
            )
        ):
            raise ValueError("At least one measurement is required")
        return self


class MetricsResponse(BaseModel):
    id: int
    device_id: int
    collected_at: AwareDatetime
    received_at: AwareDatetime
    cpu_percent: float | None
    memory_used_bytes: int | None
    memory_total_bytes: int | None
    disks: list[DiskMetrics] | None = None
    services: dict[str, str] | None
    model_config = ConfigDict(from_attributes=True)


class HistoryPoint(BaseModel):
    bucket_start: AwareDatetime
    samples: int
    cpu_percent: float | None
    cpu_max_percent: float | None
    memory_used_bytes: float | None
    memory_total_bytes: float | None
    disks: list[DiskMetrics] | None = None


class MetricsHistory(BaseModel):
    device_id: int
    start: AwareDatetime
    end: AwareDatetime
    step_seconds: int
    points: list[HistoryPoint]
