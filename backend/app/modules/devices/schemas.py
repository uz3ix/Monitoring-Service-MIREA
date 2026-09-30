from datetime import datetime
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator
from app.core.config import settings
from app.core.time import utcnow
from app.modules.metrics.schemas import MetricsResponse

DeviceName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
AgentToken = Annotated[str, Field(min_length=32, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")]


class DeviceCreate(BaseModel):
    name: DeviceName
    agent_token: AgentToken
    model_config = ConfigDict(extra="forbid")


class DeviceResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    last_seen_at: datetime | None
    status: Literal["online", "offline"] = "offline"
    latest_metrics: MetricsResponse | None = None
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def set_status(self):
        self.status = (
            "online"
            if self.last_seen_at
            and (utcnow() - self.last_seen_at).total_seconds() <= settings.online_timeout_seconds
            else "offline"
        )
        return self


class DeviceRename(BaseModel):
    name: DeviceName
    model_config = ConfigDict(extra="forbid")


class AgentTokenUpdate(BaseModel):
    agent_token: AgentToken
    model_config = ConfigDict(extra="forbid")
