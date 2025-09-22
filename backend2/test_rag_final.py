#!/usr/bin/env python3
"""
Test RAG cuối cùng - chỉ test dữ liệu và search functionality
"""

import sys
import os
from pathlib import Path

# Thêm thư mục hiện tại vào Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_data_availability():
    """Test dữ liệu có sẵn"""
    print("🔍 Kiểm tra dữ liệu RAG")
    print("=" * 40)
    
    try:
        import settings
        
        # Kiểm tra FAISS
        faiss_path = settings.FAISS_PATH
        if faiss_path.exists():
            size_mb = faiss_path.stat().st_size / (1024*1024)
            print(f"✅ FAISS Index: {faiss_path.name} ({size_mb:.1f} MB)")
        else:
            print(f"❌ FAISS Index không tồn tại: {faiss_path}")
            return False
        
        # Kiểm tra Pickle
        pickle_path = settings.PICKLE_PATH
        if pickle_path.exists():
            size_mb = pickle_path.stat().st_size / (1024*1024)
            print(f"✅ Embedding Data: {pickle_path.name} ({size_mb:.1f} MB)")
        else:
            print(f"❌ Embedding Data không tồn tại: {pickle_path}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_faiss_search():
    """Test FAISS search với random vectors"""
    print("\n🔍 Test FAISS Search")
    print("=" * 30)
    
    try:
        import faiss
        import pickle
        import numpy as np
        import settings
        
        # Load FAISS
        faiss_index = faiss.read_index(str(settings.FAISS_PATH))
        print(f"✅ FAISS loaded: {faiss_index.ntotal} vectors, {faiss_index.d} dimensions")
        
        # Load chunks
        with open(settings.PICKLE_PATH, "rb") as f:
            data = pickle.load(f)
        
        all_chunks = []
        for item in data:
            if isinstance(item, dict) and "chunks" in item:
                all_chunks.extend(item["chunks"])
        print(f"✅ Chunks loaded: {len(all_chunks)} chunks")
        
        # Test search với random vectors
        print("\n🔍 Testing search with random vectors...")
        
        for i in range(3):
            # Tạo random query vector
            query_vector = np.random.random((1, faiss_index.d)).astype('float32')
            
            # Search
            D, I = faiss_index.search(query_vector, 3)
            
            print(f"\nSearch {i+1}:")
            print(f"  Distances: {[f'{d:.2f}' for d in D[0]]}")
            
            # Hiển thị chunks
            for j, idx in enumerate(I[0]):
                if idx < len(all_chunks):
                    chunk = all_chunks[idx]
                    preview = chunk[:100] + "..." if len(chunk) > 100 else chunk
                    print(f"  Chunk {j+1}: {preview}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_data_structure():
    """Test cấu trúc dữ liệu"""
    print("\n🔍 Test Data Structure")
    print("=" * 30)
    
    try:
        import pickle
        import settings
        
        # Load data
        with open(settings.PICKLE_PATH, "rb") as f:
            data = pickle.load(f)
        
        print(f"✅ Data type: {type(data)}")
        print(f"✅ Number of items: {len(data)}")
        
        # Analyze first few items
        for i, item in enumerate(data[:3]):
            print(f"\nItem {i+1}:")
            print(f"  Type: {type(item)}")
            
            if isinstance(item, dict):
                print(f"  Keys: {list(item.keys())}")
                
                if "pdf_name" in item:
                    print(f"  PDF: {item['pdf_name']}")
                
                if "chunks" in item:
                    print(f"  Chunks: {len(item['chunks'])}")
                    
                    # Hiển thị chunk đầu tiên
                    if len(item['chunks']) > 0:
                        first_chunk = item['chunks'][0]
                        preview = first_chunk[:150] + "..." if len(first_chunk) > 150 else first_chunk
                        print(f"  First chunk: {preview}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Chạy tất cả tests"""
    print("🚀 Backend2 RAG Data Test")
    print("=" * 50)
    
    success1 = test_data_availability()
    success2 = test_faiss_search()
    success3 = test_data_structure()
    
    print(f"\n{'='*50}")
    print("📊 Test Results:")
    print(f"Data Availability: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"FAISS Search: {'✅ PASS' if success2 else '❌ FAIL'}")
    print(f"Data Structure: {'✅ PASS' if success3 else '❌ FAIL'}")
    
    if success1 and success2 and success3:
        print("\n🎉 All RAG data tests passed!")
        print("✅ Dữ liệu RAG đã sẵn sàng!")
        print("💡 Backend2 có thể sử dụng RAG với dữ liệu hiện tại")
        return True
    else:
        print("\n⚠️  Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
