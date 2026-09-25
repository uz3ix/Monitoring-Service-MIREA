from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing import Annotated


class DeviceCreate(BaseModel):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
    ]
    agent_token: str = Field(
        min_length=32,
        max_length=128,
        pattern=r"^[A-Za-z0-9_-]+$"
    )


class DeviceResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    last_seen_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
