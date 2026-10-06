import subprocess
from types import SimpleNamespace

import psutil
from collector import (
    get_windows_service_status,
    get_linux_service_status,
)


def test_windows_service_running(monkeypatch):
    def service(name):
        assert name == "Spooler"
        return SimpleNamespace(status=lambda: "running")

    monkeypatch.setattr("collector.psutil.win_service_get", service, raising=False)
    assert get_windows_service_status("Spooler") == "running"


def test_windows_service_not_found(monkeypatch):
    def service(name):
        raise psutil.NoSuchProcess(0)

    monkeypatch.setattr("collector.psutil.win_service_get", service, raising=False)
    assert get_windows_service_status("missing") == "not_found"


def test_linux_service_running(monkeypatch):
    def run(command, **kwargs):
        assert command[-1] == "cron.service"
        return SimpleNamespace(
            returncode=0,
            stdout="LoadState=loaded\nActiveState=active\nSubState=running\n",
        )

    monkeypatch.setattr("collector.subprocess.run", run)
    assert get_linux_service_status("cron.service") == "running"


def test_linux_service_stopped(monkeypatch):
    def run(command, **kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout="LoadState=loaded\nActiveState=inactive\nSubState=dead\n",
        )

    monkeypatch.setattr("collector.subprocess.run", run)
    assert get_linux_service_status("cron.service") == "stopped"


def test_linux_service_timeout(monkeypatch):
    def run(command, **kwargs):
        raise subprocess.TimeoutExpired(command, 5)

    monkeypatch.setattr("collector.subprocess.run", run)
    assert get_linux_service_status("cron.service") == "unknown"
