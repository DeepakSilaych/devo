import json
import requests
from datetime import datetime
import os

def fetch_github_run(repo, run_id, token):
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else {}

def fetch_github_logs(repo, run_id, token):
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/logs"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.content if response.status_code == 200 else b""

def extract_error_patterns(log_content):
    if isinstance(log_content, bytes):
        log_content = log_content.decode('utf-8', errors='ignore')
    
    error_keywords = ["error", "failed", "exception", "traceback", "fatal", "npm err", "build failed"]
    patterns = []
    
    for line in log_content.split('\n'):
        line_lower = line.lower()
        for keyword in error_keywords:
            if keyword in line_lower:
                patterns.append({
                    "keyword": keyword,
                    "line": line.strip(),
                    "context": line[:200]
                })
    
    return patterns

def ingest_ci_failure(repo, run_id, token):
    run_data = fetch_github_run(repo, run_id, token)
    logs = fetch_github_logs(repo, run_id, token)
    
    processed = {
        "run_id": run_id,
        "repo": repo,
        "status": run_data.get("status"),
        "conclusion": run_data.get("conclusion"),
        "workflow": run_data.get("name"),
        "commit": run_data.get("head_sha"),
        "timestamp": datetime.now().isoformat(),
        "error_patterns": extract_error_patterns(logs),
        "raw_logs": logs.decode('utf-8', errors='ignore')[:5000] if logs else ""
    }
    
    os.makedirs("data", exist_ok=True)
    with open("data/failures.json", "a") as f:
        f.write(json.dumps(processed) + "\n")
    
    return processed
