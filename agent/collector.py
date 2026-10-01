import platform
import subprocess
import os
import sys
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


def get_windows_service_status(name: str) -> str:
    try: 
        service = psutil.win_service_get(name)
        return service.status()
    except psutil.NoSuchProcess:
        return "not_found"
    except psutil.AccessDenied:
        return "access_denied"
    except OSError:
        return "unknown"
    
    
def get_linux_service_status(name: str) -> str:
    environment = os.environ.copy()
    if getattr(sys, "frozen", False):
        if "LD_LIBRARY_PATH_ORIG" in environment:
            environment["LD_LIBRARY_PATH"] = environment["LD_LIBRARY_PATH_ORIG"]
        else:
            environment.pop("LD_LIBRARY_PATH", None)
    try:
        result = subprocess.run(["systemctl", "show", "--property=LoadState,ActiveState,SubState", "--", name],
            capture_output=True, text=True, timeout=5, env=environment)
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    
    properties = {}

    for line in result.stdout.splitlines():
        key, separator, value = line.partition("=")
        if separator:
            properties[key] = value
            
    if properties.get("LoadState") == "not-found":
        return "not_found"

    if result.returncode != 0:
        return "unknown"

    active_state = properties.get("ActiveState")
    sub_state = properties.get("SubState")

    if not active_state or not sub_state:
        return "unknown"

    if active_state == "failed":
        return "failed"

    if active_state == "inactive":
        return "stopped"

    if active_state == "active" and sub_state == "running":
        return "running"

    return f"{active_state}/{sub_state}"

def collect_services(names: list[str]) -> dict[str, str]:
    services=dict()
    system = platform.system()
    
    for name in names:
        if system == "Windows":
            status = get_windows_service_status(name)
        elif system == "Linux":
            status = get_linux_service_status(name)
        else:
            status = "unknown"
            
        services[name] = status
        
    return services
    

def collect_metrics(services_names: list[str]) -> dict[str, object]:
    cpu = get_cpu_percent()
    memory = get_memory_usage()
    disks = get_disks_usage()
    services = collect_services(services_names)
    return {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "cpu_percent": cpu,
        "memory_used_bytes": memory["memory_used_bytes"],
        "memory_total_bytes": memory["memory_total_bytes"],
        "disks" : disks,
        "services": services
    }
    
    
