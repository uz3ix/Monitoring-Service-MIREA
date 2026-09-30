from pathlib import Path
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str
    admin_username: str = "admin"
    admin_password: SecretStr | None = None
    session_hours: int = Field(default=12, ge=1, le=168)
    retention_days: int = Field(default=7, ge=1, le=365)
    cleanup_interval_seconds: int = Field(default=60, ge=10)
    online_timeout_seconds: int = Field(default=180, ge=10)
    cors_origins: list[str] = []
    max_request_bytes: int = Field(default=65536, ge=1024)
    cleanup_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()  
