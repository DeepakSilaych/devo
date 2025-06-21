from fastapi import APIRouter, HTTPException
import requests

router = APIRouter(prefix="/ci")

def fetch_github_actions_logs(repo: str, run_id: int, token: str):
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/logs"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return {"status": "success", "log_zip": response.content.hex()[:1000] + "..."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

@router.get("/github")
def get_github_logs(repo: str, run_id: int, token: str):
    return fetch_github_actions_logs(repo, run_id, token)

@router.post("/analyze")
def analyze_failure(data: dict):
    from ingestion import ingest_ci_failure
    
    result = ingest_ci_failure(
        run_id=data.get("run_id"),
        repo=data.get("repo"),
        logs=data.get("logs", ""),
        status="failure"
    )
    return {"message": "Failure ingested", "result": result}
