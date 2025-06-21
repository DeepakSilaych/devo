from fastapi import FastAPI
from collectors import ci_cd_collector, runtime_collector, monitoring_collector

app = FastAPI()

app.include_router(ci_cd_collector.router)
app.include_router(runtime_collector.router)
app.include_router(monitoring_collector.router)
