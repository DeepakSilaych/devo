from fastapi import APIRouter
import psutil
import time

router = APIRouter(prefix="/runtime")

@router.get("/system")
def get_system_metrics():
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent
        },
        "disk": {
            "total": psutil.disk_usage('/').total,
            "free": psutil.disk_usage('/').free,
            "percent": psutil.disk_usage('/').percent
        },
        "timestamp": time.time()
    }

@router.get("/processes")
def get_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return {"processes": processes[:10]}

@router.post("/collect")
def collect_runtime_data(data: dict):
    metrics = get_system_metrics()
    
    runtime_data = {
        "timestamp": metrics["timestamp"],
        "service": data.get("service", "unknown"),
        "metrics": metrics,
        "errors": data.get("errors", [])
    }
    
    return {"message": "Runtime data collected", "data": runtime_data}
