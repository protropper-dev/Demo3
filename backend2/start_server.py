#!/usr/bin/env python3
"""
Script để khởi động server backend2
"""

import uvicorn
import sys
import os
from pathlib import Path

# Thêm thư mục hiện tại vào Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

import settings

def check_models():
    """Kiểm tra models trước khi khởi động"""
    print("🔍 Kiểm tra models...")
    
    try:
        import consts
        
        llm_ok = consts.llm_model is not None and consts.llm_tokenizer is not None
        embedding_ok = consts.embedding_model is not None and consts.embedding_tokenizer is not None
        
        if llm_ok and embedding_ok:
            print("✅ Tất cả models đã được load thành công!")
            return True
        else:
            print("⚠️  Một số models chưa được load:")
            print(f"   LLM Model: {'✅' if llm_ok else '❌'}")
            print(f"   Embedding Model: {'✅' if embedding_ok else '❌'}")
            print("   Server vẫn sẽ khởi động nhưng một số chức năng có thể không hoạt động.")
            return False
            
    except Exception as e:
        print(f"⚠️  Lỗi khi kiểm tra models: {e}")
        print("   Server vẫn sẽ khởi động.")
        return False

def main():
    """
    Khởi động server FastAPI
    """
    print("🚀 Đang khởi động Chatbot Security API...")
    print(f"📁 Working directory: {current_dir}")
    
    # Kiểm tra models
    check_models()
    
    print(f"🌐 Server sẽ chạy tại: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"📚 API docs sẽ có tại: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print("💡 Nhấn Ctrl+C để dừng server")
    
    try:
        uvicorn.run(
            "main:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server đã được dừng")
    except Exception as e:
        print(f"❌ Lỗi khởi động server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
