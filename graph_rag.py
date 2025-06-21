import json
import os
from openai import OpenAI
from knowledge_graph import build_graph, find_similar_failures, get_failure_path
from embeddings import create_document_embeddings, search_similar_failures, extract_relevant_context

def init_llm():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        return OpenAI(api_key=api_key)
    except Exception:
        return None

def analyze_failure(run_id, query="build failure analysis"):
    G = build_graph()
    vectorizer, embeddings, doc_metadata = create_document_embeddings()
    
    graph_similar = find_similar_failures(G, run_id)[:3]
    vector_similar = search_similar_failures(query, vectorizer, embeddings, doc_metadata, 3)
    
    failure_path = get_failure_path(G, run_id)
    
    context = {
        "target_run": run_id,
        "graph_similar": graph_similar,
        "vector_similar": vector_similar,
        "failure_path": failure_path
    }
    
    return context

def generate_diagnosis(context, query):
    client = init_llm()
    if not client:
        return f"Mock diagnosis: Based on the error patterns and similar failures, this appears to be a {query} related issue. Common causes include dependency conflicts, build configuration errors, or environment setup problems."
    if not client:
        return "LLM not available - set OPENAI_API_KEY"
    
    prompt = f"""
Analyze this CI/CD failure:

Target Run: {context['target_run']}
Query: {query}

Similar failures from graph: {context['graph_similar']}
Similar failures from vector search: {context['vector_similar']}
Failure path: {context['failure_path']}

Provide:
1. Root cause analysis
2. Specific fix recommendations
3. Prevention strategies

Keep response concise and actionable.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a CI/CD failure analysis expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"LLM error: {str(e)}"

def graph_rag_pipeline(run_id, query="analyze ci failure"):
    context = analyze_failure(run_id, query)
    diagnosis = generate_diagnosis(context, query)
    
    result = {
        "run_id": run_id,
        "query": query,
        "context": context,
        "diagnosis": diagnosis,
        "recommendations": extract_recommendations(diagnosis)
    }
    
    save_analysis(result)
    return result

def extract_recommendations(diagnosis):
    recommendations = []
    lines = diagnosis.split('\n')
    
    for line in lines:
        line = line.strip()
        if any(keyword in line.lower() for keyword in ['fix:', 'solution:', 'recommend', 'should', 'try']):
            recommendations.append(line)
    
    return recommendations[:5]

def save_analysis(result):
    os.makedirs("data", exist_ok=True)
    filename = f"data/analysis_{result['run_id']}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)

def query_knowledge_graph(query, top_k=5):
    vectorizer, embeddings, doc_metadata = create_document_embeddings()
    results = search_similar_failures(query, vectorizer, embeddings, doc_metadata, top_k)
    
    G = build_graph()
    enhanced_results = []
    
    for result in results:
        run_id = result['metadata']['run_id']
        similar = find_similar_failures(G, run_id)
        path = get_failure_path(G, run_id)
        
        enhanced_results.append({
            **result,
            "graph_context": {
                "similar_runs": similar,
                "failure_path": path
            }
        })
    
    return enhanced_results
