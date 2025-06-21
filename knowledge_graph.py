import json
import networkx as nx
import os

def load_failures():
    failures = []
    if os.path.exists("data/failures.json"):
        with open("data/failures.json", "r") as f:
            for line in f:
                failures.append(json.loads(line.strip()))
    return failures

def build_graph():
    G = nx.DiGraph()
    failures = load_failures()
    
    for failure in failures:
        repo_id = f"repo_{failure['repo'].replace('/', '_')}"
        workflow_id = f"workflow_{failure['workflow']}"
        run_id = f"run_{failure['run_id']}"
        
        G.add_node(repo_id, type="repository", name=failure['repo'])
        G.add_node(workflow_id, type="workflow", name=failure['workflow'])
        G.add_node(run_id, type="run", status=failure['status'], conclusion=failure['conclusion'])
        
        G.add_edge(repo_id, workflow_id, relation="contains")
        G.add_edge(workflow_id, run_id, relation="executed")
        
        for pattern in failure['error_patterns']:
            error_id = f"error_{pattern['keyword']}_{failure['run_id']}"
            G.add_node(error_id, type="error", keyword=pattern['keyword'], context=pattern['context'])
            G.add_edge(run_id, error_id, relation="produced")
    
    return G

def find_similar_failures(G, target_run_id):
    target_node = f"run_{target_run_id}"
    if target_node not in G:
        return []
    
    target_errors = [n for n in G.successors(target_node) if G.nodes[n]['type'] == 'error']
    target_keywords = {G.nodes[e]['keyword'] for e in target_errors}
    
    similar_runs = []
    for node in G.nodes():
        if G.nodes[node]['type'] == 'run' and node != target_node:
            run_errors = [n for n in G.successors(node) if G.nodes[n]['type'] == 'error']
            run_keywords = {G.nodes[e]['keyword'] for e in run_errors}
            
            overlap = len(target_keywords.intersection(run_keywords))
            if overlap > 0:
                similar_runs.append((node, overlap))
    
    return sorted(similar_runs, key=lambda x: x[1], reverse=True)

def get_failure_path(G, run_id):
    run_node = f"run_{run_id}"
    if run_node not in G:
        return []
    
    path = []
    for pred in G.predecessors(run_node):
        path.append(G.nodes[pred])
    
    path.append(G.nodes[run_node])
    
    for succ in G.successors(run_node):
        path.append(G.nodes[succ])
    
    return path

def save_graph(G):
    os.makedirs("data", exist_ok=True)
    nx.write_gexf(G, "data/knowledge_graph.gexf")
    
    graph_data = {
        "nodes": [{"id": n, **G.nodes[n]} for n in G.nodes()],
        "edges": [{"source": u, "target": v, **G.edges[u, v]} for u, v in G.edges()]
    }
    
    with open("data/knowledge_graph.json", "w") as f:
        json.dump(graph_data, f, indent=2)
    
    return len(G.nodes()), len(G.edges())
