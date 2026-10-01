from pathlib import Path
from pydantic import Field, SecretStr


ENV_FILE = Path(__file__).resolve().parent / ".env"

class Settings(BaseSettings):
    server_url: str