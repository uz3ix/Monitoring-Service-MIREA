import json
import sys

import httpx
import pytest


def prepare_run(agent_modules, measurement, monkeypatch, args):
    monkeypatch.setattr(sys, "argv", ["monitoring-agent", *args])
    agent_modules.config.settings.service_names = ["cron.service"]

    def collect(names):
        assert names == ["cron.service"]
        return measurement

    def unexpected_sleep(seconds):
        pytest.fail("Одноразовый режим не должен ждать следующего цикла")

    monkeypatch.setattr(agent_modules.main, "collect_metrics", collect)
    monkeypatch.setattr(agent_modules.main.time, "sleep", unexpected_sleep)


def test_collect_only(agent_modules, measurement, monkeypatch, capsys):
    prepare_run(agent_modules, measurement, monkeypatch, ["--collect-only"])

    def send(data):
        pytest.fail("collect-only не должен отправлять данные")

    monkeypatch.setattr(agent_modules.client, "send_metrics", send)
    assert agent_modules.main.main() == 0
    assert json.loads(capsys.readouterr().out) == measurement


def test_once(agent_modules, measurement, monkeypatch, capsys):
    prepare_run(agent_modules, measurement, monkeypatch, ["--once"])
    sent = []
    monkeypatch.setattr(agent_modules.client, "send_metrics", lambda data: sent.append(data))

    assert agent_modules.main.main() == 0
    assert sent == [measurement]
    assert "Метрики отправлены" in capsys.readouterr().out


def test_loop_continues_after_network_error(agent_modules, measurement, monkeypatch, capsys):
    prepare_run(agent_modules, measurement, monkeypatch, [])
    collected = []
    sent = []
    pauses = []

    def collect(names):
        collected.append(len(collected) + 1)
        return {**measurement, "cpu_percent": len(collected)}

    def send(data):
        sent.append(data["cpu_percent"])
        if len(sent) == 1:
            raise httpx.ConnectError("Unavailable")

    def sleep(seconds):
        pauses.append(seconds)
        if len(pauses) == 2:
            raise KeyboardInterrupt()

    monkeypatch.setattr(agent_modules.main, "collect_metrics", collect)
    monkeypatch.setattr(agent_modules.client, "send_metrics", send)
    monkeypatch.setattr(agent_modules.main.time, "sleep", sleep)

    with pytest.raises(KeyboardInterrupt):
        agent_modules.main.main()

    assert collected == [1, 2]
    assert sent == [1, 2]
    assert pauses == [30, 30]
    assert "Метрики отправлены" in capsys.readouterr().out
