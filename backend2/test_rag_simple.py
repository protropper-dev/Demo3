#!/usr/bin/env python3
"""
Test RAG đơn giản - chỉ test embedding và search, không load LLM
"""

import sys
import os
from pathlib import Path

# Thêm thư mục hiện tại vào Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_embedding_only():
    """Test chỉ embedding và search, không load LLM"""
    print("🧪 Test RAG Embedding (không load LLM)")
    print("=" * 50)
    
    try:
        import faiss
        import pickle
        import numpy as np
        import settings
        
        # Load FAISS index
        print("📥 Loading FAISS index...")
        faiss_index = faiss.read_index(str(settings.FAISS_PATH))
        print(f"✅ FAISS Index: {faiss_index.ntotal} vectors, {faiss_index.d} dimensions")
        
        # Load embedding data
        print("📥 Loading embedding data...")
        with open(settings.PICKLE_PATH, "rb") as f:
            data = pickle.load(f)
        print(f"✅ Embedding Data: {len(data)} documents")
        
        # Tạo chunks list
        all_chunks = []
        for item in data:
            if isinstance(item, dict) and "chunks" in item:
                all_chunks.extend(item["chunks"])
        print(f"✅ Total chunks: {len(all_chunks)}")
        
        # Test search với embedding model đơn giản
        print("\n🔍 Testing search functionality...")
        
        # Tạo query vector giả (random) để test FAISS
        query_vector = np.random.random((1, faiss_index.d)).astype('float32')
        
        # Search
        D, I = faiss_index.search(query_vector, 5)
        print(f"✅ Search successful:")
        print(f"   Distances: {D[0]}")
        print(f"   Indices: {I[0]}")
        
        # Hiển thị chunks tìm được
        for i, idx in enumerate(I[0]):
            if idx < len(all_chunks):
                chunk = all_chunks[idx]
                preview = chunk[:100] + "..." if len(chunk) > 100 else chunk
                print(f"   Chunk {i+1}: {preview}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_embedding_model():
    """Test embedding model riêng biệt"""
    print("\n🧪 Test Embedding Model")
    print("=" * 30)
    
    try:
        from sentence_transformers import SentenceTransformer
        import settings
        
        # Load embedding model
        embedding_model_path = str(settings.EMBEDDING_MODEL_FOLDER)
        print(f"📥 Loading embedding model from: {embedding_model_path}")
        
        embedding_model = SentenceTransformer(embedding_model_path)
        print("✅ Embedding model loaded successfully")
        
        # Test encoding
        test_queries = [
            "an toàn thông tin",
            "luật an toàn thông tin Việt Nam",
            "ISO 27001",
            "phishing attack"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Encoding: '{query}'")
            try:
                vector = embedding_model.encode([query])
                print(f"   Vector shape: {vector.shape}")
                print(f"   Vector sample: {vector[0][:5]}...")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading embedding model: {e}")
        return False

def main():
    """Chạy test"""
    success1 = test_embedding_only()
    success2 = test_embedding_model()
    
    print(f"\n{'='*50}")
    print("📊 Test Results:")
    print(f"Embedding Data Test: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Embedding Model Test: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 All embedding tests passed!")
        print("✅ Dữ liệu embedding đã sẵn sàng cho RAG")
        return True
    else:
        print("\n⚠️  Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
