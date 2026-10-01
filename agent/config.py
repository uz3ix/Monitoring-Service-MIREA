from pathlib import Path
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
import sys


if getattr(sys, "frozen", False):
       BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    server_url: str 
    agent_token: SecretStr = Field(min_length=32, max_length=128)
    send_interval_seconds: int = Field(default=30, ge=10)
    request_timeout_seconds: int = Field(default=5, ge=1)
    service_names: list[str] = Field(default_factory=list, max_length=100)
    
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore")
    
settings = Settings()