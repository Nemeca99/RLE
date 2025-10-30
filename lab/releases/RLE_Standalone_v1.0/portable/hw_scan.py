import json
import platform
import socket
from datetime import datetime

import psutil

def safe_get_gpu_info():
    info = {"nvml_available": False, "gpus": []}
    try:
        import pynvml as nvml  # type: ignore
        nvml.nvmlInit()
        info["nvml_available"] = True
        count = nvml.nvmlDeviceGetCount()
        for i in range(count):
            h = nvml.nvmlDeviceGetHandleByIndex(i)
            name = nvml.nvmlDeviceGetName(h).decode("utf-8") if isinstance(nvml.nvmlDeviceGetName(h), bytes) else nvml.nvmlDeviceGetName(h)
            mem = nvml.nvmlDeviceGetMemoryInfo(h)
            temp = None
            try:
                temp = nvml.nvmlDeviceGetTemperature(h, nvml.NVML_TEMPERATURE_GPU)
            except Exception:
                temp = None
            info["gpus"].append({
                "index": i,
                "name": name,
                "memory_total": getattr(mem, "total", None),
                "memory_used": getattr(mem, "used", None),
                "temp_c": temp,
            })
        nvml.nvmlShutdown()
    except Exception:
        pass
    return info

def collect_system_snapshot():
    cpu_freq = psutil.cpu_freq() or None
    vm = psutil.virtual_memory()
    disks = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append({
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
            })
        except Exception:
            continue

    snapshot = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "cpu": {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "freq_current": getattr(cpu_freq, "current", None) if cpu_freq else None,
            "freq_max": getattr(cpu_freq, "max", None) if cpu_freq else None,
        },
        "memory": {
            "total": vm.total,
            "available": vm.available,
        },
        "disks": disks,
        "gpu": safe_get_gpu_info(),
    }
    return snapshot

if __name__ == "__main__":
    snap = collect_system_snapshot()
    with open("hardware_snapshot.json", "w", encoding="utf-8") as f:
        json.dump(snap, f, indent=2)
    print("Saved hardware_snapshot.json")


