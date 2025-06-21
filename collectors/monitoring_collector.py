from fastapi import APIRouter
import json
import requests

router = APIRouter(prefix="/monitoring")

@router.get("/alerts")
def fetch_monitoring_alerts():
    return {
        "status": "success",
        "alerts": [
            {"type": "build_failure", "count": 5, "severity": "high"},
            {"type": "deployment_error", "count": 2, "severity": "medium"}
        ]
    }

@router.get("/metrics")
def fetch_system_metrics():
    return {
        "status": "success",
        "metrics": {
            "failure_rate": 0.15,
            "avg_build_time": 120,
            "success_rate": 0.85
        }
    }
