#!/usr/bin/env python3
"""
Script kiểm tra models trước khi khởi động backend
"""

import sys
import os
from pathlib import Path

# Thêm thư mục hiện tại vào Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def check_model_paths():
    """Kiểm tra đường dẫn models"""
    print("🔍 Kiểm tra đường dẫn models...")
    
    try:
        import settings
        
        # Kiểm tra LLM model
        llm_path = settings.MODEL
        if llm_path.exists():
            print(f"✅ LLM Model: {llm_path}")
        else:
            print(f"❌ LLM Model không tồn tại: {llm_path}")
            return False
        
        # Kiểm tra Embedding model
        embedding_path = settings.EMBEDDING_MODEL_FOLDER
        if embedding_path.exists():
            print(f"✅ Embedding Model: {embedding_path}")
        else:
            print(f"❌ Embedding Model không tồn tại: {embedding_path}")
            return False
        
        # Kiểm tra FAISS index
        faiss_path = settings.FAISS_PATH
        if faiss_path.exists():
            print(f"✅ FAISS Index: {faiss_path}")
        else:
            print(f"⚠️  FAISS Index không tồn tại: {faiss_path}")
            print("   Backend sẽ hoạt động nhưng không có RAG")
        
        # Kiểm tra Pickle data
        pickle_path = settings.PICKLE_PATH
        if pickle_path.exists():
            print(f"✅ Embedding Data: {pickle_path}")
        else:
            print(f"⚠️  Embedding Data không tồn tại: {pickle_path}")
            print("   Backend sẽ hoạt động nhưng không có RAG")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra settings: {e}")
        return False

def test_model_loading():
    """Test load models"""
    print("\n🧪 Test loading models...")
    
    try:
        # Import consts để trigger model loading
        import consts
        
        # Kiểm tra kết quả
        if consts.llm_model is not None and consts.llm_tokenizer is not None:
            print("✅ LLM Model loaded successfully")
        else:
            print("❌ LLM Model failed to load")
            return False
        
        if consts.embedding_model is not None and consts.embedding_tokenizer is not None:
            print("✅ Embedding Model loaded successfully")
        else:
            print("❌ Embedding Model failed to load")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi load models: {e}")
        return False

def main():
    """Chạy kiểm tra"""
    print("🔧 Backend2 Model Checker")
    print("=" * 50)
    
    # Kiểm tra đường dẫn
    paths_ok = check_model_paths()
    
    if not paths_ok:
        print("\n❌ Kiểm tra đường dẫn thất bại!")
        print("Vui lòng kiểm tra lại cấu hình trong settings.py")
        return False
    
    # Test load models
    models_ok = test_model_loading()
    
    if models_ok:
        print("\n🎉 Tất cả models đã sẵn sàng!")
        print("Backend có thể được khởi động an toàn.")
        return True
    else:
        print("\n⚠️  Models chưa sẵn sàng!")
        print("Backend có thể khởi động nhưng một số chức năng sẽ không hoạt động.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
