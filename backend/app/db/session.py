from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from app.core.config import settings
from sqlalchemy.orm import sessionmaker, Session
from collections.abc import Iterator


database_url = URL.create(
    drivername="postgresql+psycopg",
    username=settings.postgres_user,
    password=settings.postgres_password,
    host=settings.postgres_host,
    port=settings.postgres_port,
    database=settings.postgres_db
)

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    connect_args={
        "connect_timeout": 3
    }
)


SessionLocal = sessionmaker(bind=engine)


def get_db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session
