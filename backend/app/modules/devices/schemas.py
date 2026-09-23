from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class DeviceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    model_config = ConfigDict(str_strip_whitespace=True)


class DeviceResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    last_seen_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
