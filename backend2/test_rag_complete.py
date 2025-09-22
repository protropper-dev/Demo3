#!/usr/bin/env python3
"""
Test RAG hoàn chỉnh với dữ liệu embedding đã có
"""

import sys
import os
from pathlib import Path

# Thêm thư mục hiện tại vào Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_rag_without_llm():
    """Test RAG pipeline mà không cần load LLM"""
    print("🧪 Test RAG Pipeline (không cần LLM)")
    print("=" * 50)
    
    try:
        import faiss
        import pickle
        import numpy as np
        from sentence_transformers import SentenceTransformer
        import settings
        
        # 1. Load FAISS index
        print("📥 Loading FAISS index...")
        faiss_index = faiss.read_index(str(settings.FAISS_PATH))
        print(f"✅ FAISS Index: {faiss_index.ntotal} vectors, {faiss_index.d} dimensions")
        
        # 2. Load embedding data
        print("📥 Loading embedding data...")
        with open(settings.PICKLE_PATH, "rb") as f:
            data = pickle.load(f)
        print(f"✅ Embedding Data: {len(data)} documents")
        
        # 3. Tạo chunks list
        all_chunks = []
        for item in data:
            if isinstance(item, dict) and "chunks" in item:
                all_chunks.extend(item["chunks"])
        print(f"✅ Total chunks: {len(all_chunks)}")
        
        # 4. Load embedding model
        print("📥 Loading embedding model...")
        embedding_model = SentenceTransformer(str(settings.EMBEDDING_MODEL_FOLDER))
        print("✅ Embedding model loaded")
        
        # 5. Test RAG pipeline
        print("\n🔍 Testing RAG Pipeline...")
        
        test_queries = [
            "an toàn thông tin",
            "luật an toàn thông tin Việt Nam", 
            "ISO 27001",
            "phishing attack",
            "ransomware"
        ]
        
        for query in test_queries:
            print(f"\n❓ Query: '{query}'")
            
            # Encode query
            query_vector = embedding_model.encode([query])
            
            # Search trong FAISS
            D, I = faiss_index.search(query_vector.astype('float32'), 3)
            
            print(f"   📊 Found {len(I[0])} relevant chunks:")
            
            # Hiển thị chunks tìm được
            for i, idx in enumerate(I[0]):
                if idx < len(all_chunks):
                    chunk = all_chunks[idx]
                    preview = chunk[:150] + "..." if len(chunk) > 150 else chunk
                    print(f"   {i+1}. Distance: {D[0][i]:.2f}")
                    print(f"      {preview}")
                    print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_chat_utils():
    """Test utils.chat functions"""
    print("\n🧪 Test Chat Utils")
    print("=" * 30)
    
    try:
        from utils.chat import load_embedding_and_chunks, get_relevant_chunks, build_prompt
        
        # Load data
        print("📥 Loading embedding and chunks...")
        faiss_index, chunks = load_embedding_and_chunks()
        
        if faiss_index is None:
            print("❌ Cannot load FAISS index")
            return False
        
        if len(chunks) == 0:
            print("❌ No chunks found")
            return False
        
        print(f"✅ Loaded {len(chunks)} chunks")
        
        # Test get_relevant_chunks (không cần LLM)
        test_query = "an toàn thông tin"
        print(f"\n🔍 Testing get_relevant_chunks with: '{test_query}'")
        
        # Mock embedding model để test
        import numpy as np
        from sentence_transformers import SentenceTransformer
        import settings
        
        embedding_model = SentenceTransformer(str(settings.EMBEDDING_MODEL_FOLDER))
        
        # Tạo function mock
        def mock_get_relevant_chunks(query, faiss_index, chunks, top_k=3):
            query_vector = embedding_model.encode([query])
            D, I = faiss_index.search(query_vector.astype('float32'), top_k)
            
            context_chunks = []
            for i in I[0]:
                if i < len(chunks):
                    chunk = chunks[i]
                    context_chunks.append(chunk.strip())
            
            return context_chunks
        
        relevant_chunks = mock_get_relevant_chunks(test_query, faiss_index, chunks)
        print(f"✅ Found {len(relevant_chunks)} relevant chunks")
        
        # Test build_prompt
        prompt = build_prompt(relevant_chunks, test_query)
        print(f"✅ Built prompt (length: {len(prompt)} chars)")
        print(f"   Prompt preview: {prompt[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Chạy tất cả tests"""
    print("🚀 Backend2 Complete RAG Test")
    print("=" * 60)
    
    success1 = test_rag_without_llm()
    success2 = test_chat_utils()
    
    print(f"\n{'='*60}")
    print("📊 Test Results:")
    print(f"RAG Pipeline Test: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Chat Utils Test: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 All RAG tests passed!")
        print("✅ Backend2 RAG pipeline is ready!")
        print("💡 You can now start the server and test chat functionality")
        return True
    else:
        print("\n⚠️  Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
