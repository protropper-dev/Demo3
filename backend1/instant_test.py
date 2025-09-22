#!/usr/bin/env python3
import requests

try:
    # Test health
    health = requests.get("http://localhost:8000/health", timeout=3)
    print(f"Health: {health.status_code}")
    
    # Test stats  
    stats = requests.get("http://localhost:8000/api/v1/chatbot/stats", timeout=5)
    if stats.status_code == 200:
        data = stats.json()
        kb = data.get("knowledge_base", {})
        print(f"Documents: {kb.get('total_documents', 0)}")
        print(f"Vectors: {kb.get('total_vectors', 0)}")
    
    # Test query
    query = requests.post(
        "http://localhost:8000/api/v1/chatbot/query",
        json={"question": "An toàn thông tin là gì?"},
        timeout=10
    )
    if query.status_code == 200:
        data = query.json()
        print(f"Query success! Sources: {data.get('total_sources', 0)}")
        print(f"Answer: {data.get('answer', 'No answer')[:100]}...")
    else:
        print(f"Query failed: {query.status_code}")
        
except Exception as e:
    print(f"Error: {e}")
