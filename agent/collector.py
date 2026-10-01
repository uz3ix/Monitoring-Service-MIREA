import psutil
from datetime import datetime, timezone

def get_cpu_percent() -> float:
    return psutil.cpu_percent(interval=1)


def get_memory_usage() -> dict[str, int]:
    memory = psutil.virtual_memory()
    return {"memory_used_bytes": memory.total - memory.available,
            "memory_total_bytes": memory.total
            }
    

def get_disk_usage(path: str) -> dict[str, int]:
    disk = psutil.disk_usage(path)
    return {
        "disk_used_bytes": disk.used,
        "disk_total_bytes": disk.total
    }
    
    
def collect_metrics(path: str) -> dict[str, float | int | str]:
    cpu = get_cpu_percent()
    memory = get_memory_usage()
    disk = get_disk_usage(path)
    return {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "cpu_percent": cpu,
        "memory_used_bytes": memory["memory_used_bytes"],
        "memory_total_bytes": memory["memory_total_bytes"],
        "disk_used_bytes": disk["disk_used_bytes"],
        "disk_total_bytes": disk["disk_total_bytes"]
    }
    
    
def get_disks_usage() -> list[dict[str, str | int]]:
    disks = []

    for partition in psutil.disk_partitions(all=False):
        try:
            usage = get_disk_usage(partition.mountpoint)
        except OSError:
            continue

        disks.append({
            "name": partition.mountpoint,
            **usage
        })

    return disks