import json
import time
from ingestion import ingest_ci_failure
from knowledge_graph import build_graph, save_graph
from embeddings import create_document_embeddings
from graph_rag import graph_rag_pipeline, query_knowledge_graph

def test_sample_data():
    sample_failures = [
        {
            "run_id": 12345,
            "repo": "test/repo1",
            "status": "completed",
            "conclusion": "failure",
            "workflow": "CI",
            "commit": "abc123",
            "error_patterns": [
                {"keyword": "npm err", "line": "npm ERR! code ELIFECYCLE", "context": "Build failed"},
                {"keyword": "failed", "line": "Tests failed with 3 errors", "context": "Test execution"}
            ],
            "raw_logs": "npm install\nnpm ERR! code ELIFECYCLE\nTests failed"
        },
        {
            "run_id": 12346,
            "repo": "test/repo1",
            "status": "completed",
            "conclusion": "failure",
            "workflow": "CI",
            "commit": "def456",
            "error_patterns": [
                {"keyword": "error", "line": "TypeError: Cannot read property", "context": "Runtime error"},
                {"keyword": "failed", "line": "Build process failed", "context": "Build stage"}
            ],
            "raw_logs": "Building...\nTypeError: Cannot read property\nBuild process failed"
        }
    ]
    
    import os
    os.makedirs("data", exist_ok=True)
    
    with open("data/failures.json", "w") as f:
        for failure in sample_failures:
            f.write(json.dumps(failure) + "\n")

def test_pipeline():
    print("1. Creating sample data...")
    test_sample_data()
    
    print("2. Building knowledge graph...")
    G = build_graph()
    nodes, edges = save_graph(G)
    print(f"Graph: {nodes} nodes, {edges} edges")
    
    print("3. Creating embeddings...")
    vectorizer, embeddings, metadata = create_document_embeddings()
    print(f"Embeddings: {embeddings.shape if embeddings is not None else 'None'}")
    
    print("4. Testing Graph-RAG analysis...")
    result = graph_rag_pipeline(12345, "npm build error")
    print(f"Analysis result: {result['diagnosis'][:100]}...")
    
    print("5. Testing knowledge graph query...")
    query_results = query_knowledge_graph("build failure", 2)
    print(f"Query results: {len(query_results)} matches")
    
    print("Pipeline test completed successfully!")
    return True

if __name__ == "__main__":
    test_pipeline()
