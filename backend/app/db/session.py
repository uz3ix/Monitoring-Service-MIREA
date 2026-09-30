from collections.abc import Iterator
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import settings

database_url = URL.create(
    drivername="postgresql+psycopg",
    username=settings.postgres_user,
    password=settings.postgres_password,
    host=settings.postgres_host,
    port=settings.postgres_port,
    database=settings.postgres_db,
)

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_timeout=5,
    hide_parameters=True,
    connect_args={
        "connect_timeout": 3,
        "options": "-c statement_timeout=10000",
    },
)


SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session
