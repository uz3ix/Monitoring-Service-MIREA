import importlib.util
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
from pydantic_settings.sources import DotEnvSettingsSource


AGENT_DIR = Path(__file__).resolve().parents[1]
SETTING_NAMES = {
    "SERVER_URL", "AGENT_TOKEN", "SEND_INTERVAL_SECONDS",
    "REQUEST_TIMEOUT_SECONDS", "SERVICE_NAMES",
}


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch):
    
    for name in list(os.environ):
        if name.upper() in SETTING_NAMES:
            monkeypatch.delenv(name)

    def unexpected_request(*args, **kwargs):
        pytest.fail("HTTP-запрос нужно подменить в тесте")

    monkeypatch.setattr(httpx, "post", unexpected_request)


def load_module(name, monkeypatch):
    spec = importlib.util.spec_from_file_location(name, AGENT_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def agent_modules(monkeypatch):
    
    with monkeypatch.context() as setup:
        setup.setenv("SERVER_URL", "http://monitoring.test:8000")
        setup.setenv("AGENT_TOKEN", "a" * 32)
        setup.setattr(DotEnvSettingsSource, "_read_env_files", lambda self: {})
        config = load_module("config", monkeypatch)

    client = load_module("client", monkeypatch)
    main = load_module("main", monkeypatch)
    return SimpleNamespace(config=config, client=client, main=main)


@pytest.fixture
def measurement():
    return {
        "collected_at": "2026-10-06T10:00:00+00:00",
        "cpu_percent": 25.5,
        "memory_used_bytes": 4000,
        "memory_total_bytes": 16000,
        "disks": [{"name": "/", "disk_used_bytes": 2000, "disk_total_bytes": 8000}],
        "services": {"cron.service": "running"},
    }
