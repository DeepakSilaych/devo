from fastapi import APIRouter
import requests
from fastapi import HTTPException

router = APIRouter(prefix="/ci")

@router.get("/github")
def fetch_github_actions_logs(repo: str, run_id: int, token: str):
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/logs"
    headers = {"Authorization": f"Bearer {token}"}

    res = requests.get(url, headers=headers)

    if res.status_code == 200:
        return {"status": "success", "log_zip": res.content.hex()[:1000] + "..."}
    else:
        raise HTTPException(status_code=res.status_code, detail=res.text)
