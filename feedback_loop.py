import json
import time
import schedule
from datetime import datetime
from ingestion import ingest_ci_failure
from knowledge_graph import build_graph, save_graph
from embeddings import create_document_embeddings
from graph_rag import graph_rag_pipeline

def collect_new_failures():
    print(f"[{datetime.now()}] Checking for new failures...")
    
    repos = ["owner/repo1", "owner/repo2"]
    
    for repo in repos:
        recent_runs = fetch_recent_runs(repo)
        
        for run in recent_runs:
            if run['conclusion'] == 'failure':
                if not failure_exists(run['id']):
                    print(f"New failure found: {run['id']}")
                    ingest_ci_failure(repo, run['id'], get_token())

def fetch_recent_runs(repo):
    return [
        {"id": 12347, "conclusion": "failure", "status": "completed"},
        {"id": 12348, "conclusion": "success", "status": "completed"}
    ]

def failure_exists(run_id):
    try:
        with open("data/failures.json", "r") as f:
            for line in f:
                failure = json.loads(line.strip())
                if failure['run_id'] == run_id:
                    return True
    except FileNotFoundError:
        pass
    return False

def get_token():
    import os
    return os.getenv("GITHUB_TOKEN", "fake-token")

def rebuild_knowledge_graph():
    print(f"[{datetime.now()}] Rebuilding knowledge graph...")
    G = build_graph()
    nodes, edges = save_graph(G)
    print(f"Graph rebuilt: {nodes} nodes, {edges} edges")

def update_embeddings():
    print(f"[{datetime.now()}] Updating embeddings...")
    vectorizer, embeddings, metadata = create_document_embeddings()
    if embeddings is not None:
        print(f"Embeddings updated: {embeddings.shape}")

def analyze_recent_patterns():
    print(f"[{datetime.now()}] Analyzing recent failure patterns...")
    
    recent_failures = []
    try:
        with open("data/failures.json", "r") as f:
            for line in f:
                failure = json.loads(line.strip())
                recent_failures.append(failure)
    except FileNotFoundError:
        return
    
    if len(recent_failures) < 2:
        return
    
    latest_failure = recent_failures[-1]
    analysis = graph_rag_pipeline(latest_failure['run_id'], "pattern analysis")
    
    print(f"Latest analysis: {analysis['diagnosis'][:100]}...")

def feedback_loop():
    collect_new_failures()
    rebuild_knowledge_graph()
    update_embeddings()
    analyze_recent_patterns()

def start_monitoring():
    schedule.every(30).minutes.do(feedback_loop)
    schedule.every(2).hours.do(rebuild_knowledge_graph)
    schedule.every(6).hours.do(analyze_recent_patterns)
    
    print("Starting Devo feedback loop monitoring...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    start_monitoring()
