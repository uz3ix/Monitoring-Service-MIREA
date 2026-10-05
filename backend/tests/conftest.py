import os
from pathlib import Path


os.environ.update(
    {
        "POSTGRES_HOST": "127.0.0.1",
        "POSTGRES_PORT": os.getenv("TEST_POSTGRES_PORT", "55439"),
        "POSTGRES_USER": "monitoring_test",
        "POSTGRES_PASSWORD": "local-test-only",
        "POSTGRES_DB": "monitoring_test",
        "ADMIN_USERNAME": "admin",
        "ADMIN_PASSWORD": "testing-admin-password",
        "CLEANUP_ENABLED": "false",
        "CORS_ORIGINS": '["http://localhost:5173"]',
    }
)

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db.session import engine
from app.main import app
from app.modules.auth.router import attempts


@pytest.fixture(scope="session", autouse=True)
def migrated_database():
    if engine.url.database != "monitoring_test" or engine.url.host != "127.0.0.1":
        raise RuntimeError("Refusing to run destructive tests outside the isolated test database")
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    command.upgrade(config, "head")
    yield
    engine.dispose()


@pytest.fixture
def client():
    with engine.begin() as connection:
        connection.execute(
            text("TRUNCATE metrics, devices, user_sessions, users RESTART IDENTITY CASCADE")
        )
    attempts.clear()
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client


@pytest.fixture
def admin(client):
    response = client.post("/auth/login", json={
                                                "username": "admin", 
                                                "password": "testing-admin-password"
                                                })
    assert response.status_code == 200, response.text
    return {"Authorization": "Bearer " + response.json()["access_token"]}
