from fastapi import APIRouter, Request

router = APIRouter(prefix="/runtime")

@router.post("/log")
async def receive_runtime_log(req: Request):
    data = await req.json()
    print("Runtime log received:", data)
    return {"status": "ok"}
