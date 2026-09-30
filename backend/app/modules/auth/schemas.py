from pydantic import BaseModel, ConfigDict, Field, SecretStr


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: SecretStr = Field(min_length=1, max_length=256)
    model_config = ConfigDict(extra="forbid")


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: int
    username: str
    model_config = ConfigDict(from_attributes=True)
