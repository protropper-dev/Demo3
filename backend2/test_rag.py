#!/usr/bin/env python3
"""
Script test RAG với dữ liệu embedding đã có
"""

import sys
import os
from pathlib import Path

# Thêm thư mục hiện tại vào Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_embedding_data():
    """Test dữ liệu embedding"""
    print("🔍 Kiểm tra dữ liệu embedding...")
    
    try:
        import settings
        
        # Kiểm tra file FAISS
        faiss_path = settings.FAISS_PATH
        if faiss_path.exists():
            print(f"✅ FAISS Index: {faiss_path}")
            print(f"   Size: {faiss_path.stat().st_size / (1024*1024):.2f} MB")
        else:
            print(f"❌ FAISS Index không tồn tại: {faiss_path}")
            return False
        
        # Kiểm tra file Pickle
        pickle_path = settings.PICKLE_PATH
        if pickle_path.exists():
            print(f"✅ Embedding Data: {pickle_path}")
            print(f"   Size: {pickle_path.stat().st_size / (1024*1024):.2f} MB")
        else:
            print(f"❌ Embedding Data không tồn tại: {pickle_path}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra embedding data: {e}")
        return False

def test_faiss_loading():
    """Test load FAISS index"""
    print("\n🧪 Test load FAISS index...")
    
    try:
        import faiss
        import settings
        
        # Load FAISS index
        faiss_index = faiss.read_index(str(settings.FAISS_PATH))
        print(f"✅ FAISS Index loaded successfully")
        print(f"   Dimensions: {faiss_index.d}")
        print(f"   Total vectors: {faiss_index.ntotal}")
        
        return faiss_index
        
    except Exception as e:
        print(f"❌ Lỗi khi load FAISS index: {e}")
        return None

def test_embedding_data_loading():
    """Test load embedding data"""
    print("\n🧪 Test load embedding data...")
    
    try:
        import pickle
        import settings
        
        # Load embedding data
        with open(settings.PICKLE_PATH, "rb") as f:
            data = pickle.load(f)
        
        print(f"✅ Embedding data loaded successfully")
        print(f"   Data type: {type(data)}")
        
        if isinstance(data, list):
            print(f"   Number of documents: {len(data)}")
            
            # Hiển thị thông tin về document đầu tiên
            if len(data) > 0:
                first_doc = data[0]
                print(f"   First document type: {type(first_doc)}")
                
                if isinstance(first_doc, dict):
                    print(f"   First document keys: {list(first_doc.keys())}")
                    if "chunks" in first_doc:
                        print(f"   First document chunks: {len(first_doc['chunks'])}")
                elif isinstance(first_doc, list):
                    print(f"   First document chunks: {len(first_doc)}")
        
        return data
        
    except Exception as e:
        print(f"❌ Lỗi khi load embedding data: {e}")
        return None

def test_search_functionality():
    """Test chức năng tìm kiếm"""
    print("\n🧪 Test search functionality...")
    
    try:
        from utils.chat import load_embedding_and_chunks, get_relevant_chunks
        import consts
        
        # Load data
        faiss_index, chunks = load_embedding_and_chunks()
        
        if faiss_index is None or len(chunks) == 0:
            print("❌ Không thể load embedding data")
            return False
        
        print(f"✅ Loaded {len(chunks)} chunks")
        
        # Test search với câu hỏi mẫu
        test_queries = [
            "an toàn thông tin",
            "luật an toàn thông tin",
            "ISO 27001",
            "phishing",
            "ransomware"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Test query: '{query}'")
            try:
                relevant_chunks = get_relevant_chunks(query, faiss_index, chunks, top_k=3)
                print(f"   Found {len(relevant_chunks)} relevant chunks")
                
                if relevant_chunks:
                    # Hiển thị chunk đầu tiên (rút gọn)
                    first_chunk = relevant_chunks[0]
                    preview = first_chunk[:200] + "..." if len(first_chunk) > 200 else first_chunk
                    print(f"   First chunk preview: {preview}")
                
            except Exception as e:
                print(f"   ❌ Error searching for '{query}': {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi test search functionality: {e}")
        return False

def test_full_rag():
    """Test RAG hoàn chỉnh"""
    print("\n🧪 Test full RAG...")
    
    try:
        from utils.chat import get_response
        
        # Test với câu hỏi mẫu
        test_questions = [
            "Luật an toàn thông tin Việt Nam có những quy định gì?",
            "ISO 27001 là gì?",
            "Các loại tấn công mạng phổ biến?",
            "Phishing là gì?"
        ]
        
        for question in test_questions:
            print(f"\n❓ Question: {question}")
            try:
                response = get_response(question, max_tokens=100)
                print(f"✅ Response: {response}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi test full RAG: {e}")
        return False

def main():
    """Chạy tất cả tests"""
    print("🧪 Backend2 RAG Testing Suite")
    print("=" * 50)
    
    tests = [
        ("Embedding Data Check", test_embedding_data),
        ("FAISS Loading", test_faiss_loading),
        ("Embedding Data Loading", test_embedding_data_loading),
        ("Search Functionality", test_search_functionality),
        ("Full RAG Test", test_full_rag),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = test_func()
            results.append((test_name, result is not None and result is not False))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 RAG Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All RAG tests passed! Backend2 is ready for RAG.")
        return True
    else:
        print("⚠️  Some RAG tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
