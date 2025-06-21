from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from collectors.ci_cd_collector import router as ci_router
from collectors.monitoring_collector import router as monitoring_router
from collectors.runtime_collector import router as runtime_router
from ingestion import ingest_ci_failure
from knowledge_graph import build_graph, save_graph
from graph_rag import graph_rag_pipeline, query_knowledge_graph
import os

app = FastAPI(title="Devo CI/CD Failure Analysis")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

app.include_router(ci_router)
app.include_router(monitoring_router)
app.include_router(runtime_router)

class IngestRequest(BaseModel):
    repo: str
    run_id: int
    token: str

class AnalyzeRequest(BaseModel):
    run_id: int
    query: str = "analyze ci failure"

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

@app.get("/")
def root():
    return FileResponse("frontend/index.html")

@app.get("/app")
def serve_app():
    return FileResponse("frontend/index.html")

@app.get("/api")
def api_root():
    return {"message": "Devo CI/CD Analysis API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "collectors": ["ci", "monitoring", "runtime"]}

@app.post("/ingest")
def ingest_failure(request: IngestRequest):
    try:
        result = ingest_ci_failure(request.repo, request.run_id, request.token)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/build-graph")
def build_knowledge_graph():
    try:
        G = build_graph()
        nodes, edges = save_graph(G)
        return {"status": "success", "nodes": nodes, "edges": edges}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
def analyze_failure(request: AnalyzeRequest):
    try:
        result = graph_rag_pipeline(request.run_id, request.query)
        return {"status": "success", "analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
def query_graph(request: QueryRequest):
    try:
        results = query_knowledge_graph(request.query, request.top_k)
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
def get_stats():
    try:
        G = build_graph()
        return {
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "node_types": {node_type: len([n for n in G.nodes() if G.nodes[n].get('type') == node_type]) 
                          for node_type in ['repository', 'workflow', 'run', 'error']}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
