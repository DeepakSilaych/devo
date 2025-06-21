import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_failures():
    failures = []
    try:
        with open("data/failures.json", "r") as f:
            for line in f:
                failures.append(json.loads(line.strip()))
    except FileNotFoundError:
        pass
    return failures

def create_document_embeddings():
    failures = load_failures()
    if not failures:
        return None, None, {}
    
    documents = []
    doc_metadata = {}
    
    for failure in failures:
        doc_id = f"run_{failure['run_id']}"
        
        error_text = " ".join([p['line'] for p in failure['error_patterns']])
        doc_text = f"{failure['repo']} {failure['workflow']} {failure['status']} {error_text}"
        
        documents.append(doc_text)
        doc_metadata[doc_id] = failure
    
    vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    embeddings = vectorizer.fit_transform(documents)
    
    return vectorizer, embeddings, doc_metadata

def search_similar_failures(query, vectorizer, embeddings, doc_metadata, top_k=3):
    if not vectorizer or embeddings is None:
        return []
    
    query_vector = vectorizer.transform([query])
    similarities = cosine_similarity(query_vector, embeddings).flatten()
    
    top_indices = similarities.argsort()[-top_k:][::-1]
    
    results = []
    for idx in top_indices:
        doc_id = list(doc_metadata.keys())[idx]
        score = similarities[idx]
        results.append({
            "doc_id": doc_id,
            "similarity": float(score),
            "metadata": doc_metadata[doc_id]
        })
    
    return results

def extract_relevant_context(failure_data, query):
    relevant_lines = []
    
    for pattern in failure_data['error_patterns']:
        if any(word in pattern['line'].lower() for word in query.lower().split()):
            relevant_lines.append(pattern['line'])
    
    if failure_data['raw_logs']:
        log_lines = failure_data['raw_logs'].split('\n')
        for line in log_lines:
            if any(word in line.lower() for word in query.lower().split()):
                relevant_lines.append(line)
                if len(relevant_lines) >= 5:
                    break
    
    return relevant_lines
