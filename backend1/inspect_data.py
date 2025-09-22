#!/usr/bin/env python3
"""
Kiểm tra dữ liệu thực tế trong pickle file
"""

import os
import pickle
import json

def inspect_pickle_data():
    """Kiểm tra nội dung file pickle"""
    print("🔍 KIỂM TRA DỮ LIỆU PICKLE")
    print("=" * 40)
    
    try:
        data_dir = "D:/Vian/Demo3/backend1/data"
        pickle_path = os.path.join(data_dir, "all_embeddings.pkl")
        
        print(f"📁 File: {pickle_path}")
        print(f"📊 Size: {os.path.getsize(pickle_path) / 1024 / 1024:.2f} MB")
        
        with open(pickle_path, 'rb') as f:
            documents_data = pickle.load(f)
        
        print(f"📝 Total documents: {len(documents_data)}")
        
        # Kiểm tra structure của document đầu tiên
        if documents_data:
            print(f"\n🔍 Structure của document đầu tiên:")
            first_doc = documents_data[0]
            print(f"Type: {type(first_doc)}")
            
            if isinstance(first_doc, dict):
                print("Keys:", list(first_doc.keys()))
                for key, value in first_doc.items():
                    if isinstance(value, str):
                        print(f"  {key}: {value[:100]}..." if len(str(value)) > 100 else f"  {key}: {value}")
                    else:
                        print(f"  {key}: {type(value)} (length: {len(value) if hasattr(value, '__len__') else 'N/A'})")
            
            # Kiểm tra 5 documents đầu
            print(f"\n📚 Sample của 5 documents đầu:")
            for i, doc in enumerate(documents_data[:5]):
                if isinstance(doc, dict):
                    filename = doc.get('filename', 'N/A')
                    content_preview = str(doc.get('content', ''))[:50] + "..." if doc.get('content') else 'No content'
                    print(f"  {i+1}. {filename}: {content_preview}")
                else:
                    print(f"  {i+1}. Type: {type(doc)}")
        
        # Tìm documents có chứa từ khóa
        print(f"\n🔎 Tìm documents chứa 'an toàn' hoặc 'thông tin':")
        found_docs = []
        
        for i, doc in enumerate(documents_data):
            if isinstance(doc, dict):
                content = str(doc.get('content', '')).lower()
                filename = doc.get('filename', 'N/A')
                
                if 'an toàn' in content or 'thông tin' in content or 'bảo mật' in content:
                    found_docs.append({
                        'index': i,
                        'filename': filename,
                        'content_preview': content[:200]
                    })
        
        print(f"✅ Tìm thấy {len(found_docs)} documents có từ khóa liên quan")
        
        for doc in found_docs[:5]:  # Hiển thị top 5
            print(f"  - {doc['filename']}")
            print(f"    Content: {doc['content_preview']}...")
        
        return len(found_docs) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    success = inspect_pickle_data()
    
    if success:
        print(f"\n✅ Có dữ liệu liên quan đến an toàn thông tin!")
        print(f"💡 Vấn đề có thể là ở cách tìm kiếm trong script trước")
    else:
        print(f"\n❌ Không tìm thấy dữ liệu liên quan")
        print(f"💡 Có thể cần rebuild lại knowledge base")

if __name__ == "__main__":
    main()
