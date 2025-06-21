from fastapi import APIRouter, Request

router = APIRouter(prefix="/monitoring")

@router.post("/alert")
async def receive_monitoring_alert(req: Request):
    data = await req.json()
    print("Monitoring alert received:", data)
    return {"status": "ok"}
