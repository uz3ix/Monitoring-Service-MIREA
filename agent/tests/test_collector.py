from datetime import datetime, timezone
from types import SimpleNamespace
from collector import (
    get_memory_usage,
    get_disks_usage,
    collect_metrics,
)


def test_memory_usage(monkeypatch):
    def virtual_memory():
        return SimpleNamespace(total=16000, available=6000)
    
    monkeypatch.setattr("collector.psutil.virtual_memory", virtual_memory)
    
    result = get_memory_usage()
    
    assert result["memory_total_bytes"] == 16000
    assert result["memory_used_bytes"] == 10000


def test_unavailable_disk(monkeypatch):
    def disks(all=False):
        return [
            SimpleNamespace(mountpoint="/unavailable"),
            SimpleNamespace(mountpoint="/data")
        ]
    
    def disk_usage(path):
        if path == "/unavailable":
            raise OSError("Disk unavailable")
    
        return SimpleNamespace(used=4000, total=10000)

    monkeypatch.setattr("collector.psutil.disk_partitions", disks)
    monkeypatch.setattr("collector.psutil.disk_usage", disk_usage)
    
    result = get_disks_usage()
    
    assert result == [
        {
            "name": "/data",
            "disk_used_bytes": 4000,
            "disk_total_bytes": 10000,
        }
    ]


def test_collect_metrics(monkeypatch):
    def cpu_percent(interval):
        assert interval == 1
        return 25.5

    def services(names):
        assert names == ["cron.service"]
        return {"cron.service": "running"}

    monkeypatch.setattr("collector.psutil.cpu_percent", cpu_percent)
    monkeypatch.setattr(
        "collector.psutil.virtual_memory",
        lambda: SimpleNamespace(total=16000, available=6000),
    )
    monkeypatch.setattr(
        "collector.psutil.disk_partitions",
        lambda all=False: [SimpleNamespace(mountpoint="/")],
    )
    monkeypatch.setattr(
        "collector.psutil.disk_usage", lambda path: SimpleNamespace(used=0, total=8000)
    )
    monkeypatch.setattr("collector.collect_services", services)

    before = datetime.now(timezone.utc)
    result = collect_metrics(["cron.service"])
    after = datetime.now(timezone.utc)
    collected_at = datetime.fromisoformat(result.pop("collected_at"))

    assert collected_at.utcoffset().total_seconds() == 0
    assert before <= collected_at <= after
    assert result == {
        "cpu_percent": 25.5,
        "memory_used_bytes": 10000,
        "memory_total_bytes": 16000,
        "disks": [{"name": "/", "disk_used_bytes": 0, "disk_total_bytes": 8000}],
        "services": {"cron.service": "running"},
    }
