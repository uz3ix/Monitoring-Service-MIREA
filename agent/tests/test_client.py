from copy import deepcopy

import httpx
import pytest


def test_send_metrics_request(agent_modules, measurement, monkeypatch):
    settings = agent_modules.config.settings
    settings.server_url = "http://monitoring.test:8000" + "/"
    settings.request_timeout_seconds = 7
    original = deepcopy(measurement)
    calls = []

    def post(url, **kwargs):
        calls.append(url)
        assert url == "http://monitoring.test:8000/metrics"
        assert kwargs["json"] == original
        assert kwargs["headers"] == {"X-Agent-Token": "a" * 32}
        assert kwargs["timeout"] == 7
        return httpx.Response(201, request=httpx.Request("POST", url))

    monkeypatch.setattr("httpx.post", post)
    assert agent_modules.client.send_metrics(measurement) is None
    assert len(calls) == 1
    assert measurement == original


def test_server_rejects_metrics(agent_modules, measurement, monkeypatch):
    def post(url, **kwargs):
        return httpx.Response(401, request=httpx.Request("POST", url))

    monkeypatch.setattr("httpx.post", post)
    with pytest.raises(httpx.HTTPStatusError) as error:
        agent_modules.client.send_metrics(measurement)
    assert error.value.response.status_code == 401
