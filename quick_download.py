#!/usr/bin/env python3
"""
Script tải nhanh các mô hình AI
Sử dụng: python quick_download.py
"""

import os
import sys
from pathlib import Path

# Thêm backend1 vào Python path để import paths
backend_path = Path(__file__).parent / "backend1"
sys.path.insert(0, str(backend_path))

from app.core.paths import MODELS_DIR, EMBEDDING_MODEL, LLM_MODEL

def quick_download():
    """Tải nhanh cả 2 mô hình"""
    print("🚀 Bắt đầu tải nhanh các mô hình AI...")
    
    try:
        from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM
        from huggingface_hub import snapshot_download
        print("✅ Dependencies đã sẵn sàng")
    except ImportError as e:
        print(f"❌ Thiếu dependencies: {e}")
        print("Vui lòng chạy: pip install transformers torch huggingface_hub")
        return False
    
    # Sử dụng paths.py để lấy đường dẫn models
    models_dir = MODELS_DIR
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Models directory: {models_dir}")
    
    # Cấu hình mô hình - sử dụng paths.py
    models = [
        {
            "name": "multilingual_e5_large",
            "repo_id": "intfloat/multilingual-e5-large",
            "local_dir": EMBEDDING_MODEL
        },
        {
            "name": "vinallama-2.7b-chat", 
            "repo_id": "Viet-Mistral/Vinallama-2.7B-Chat",
            "local_dir": LLM_MODEL
        }
    ]
    
    results = {}
    
    for model in models:
        print(f"\n📦 Đang tải: {model['name']}")
        print(f"   Từ: {model['repo_id']}")
        print(f"   Đến: {model['local_dir']}")
        
        try:
            # Tải mô hình
            snapshot_download(
                repo_id=model["repo_id"],
                local_dir=str(model["local_dir"]),
                local_dir_use_symlinks=False,
                resume_download=True
            )
            
            # Kiểm tra kích thước
            total_size = sum(f.stat().st_size for f in model["local_dir"].rglob('*') if f.is_file())
            size_gb = total_size / (1024**3)
            
            print(f"✅ Thành công: {model['name']} ({size_gb:.2f} GB)")
            results[model["name"]] = True
            
        except Exception as e:
            print(f"❌ Thất bại: {model['name']} - {str(e)}")
            results[model["name"]] = False
    
    # Tổng kết
    print(f"\n📊 KẾT QUẢ:")
    for name, success in results.items():
        status = "✅ Thành công" if success else "❌ Thất bại"
        print(f"   - {name}: {status}")
    
    success_count = sum(results.values())
    total_count = len(results)
    
    if success_count == total_count:
        print(f"\n🎉 Hoàn thành! Đã tải thành công {success_count}/{total_count} mô hình")
        print(f"📁 Thư mục: {models_dir.absolute()}")
    else:
        print(f"\n⚠️ Hoàn thành một phần: {success_count}/{total_count} mô hình")
    
    return success_count == total_count

if __name__ == "__main__":
    quick_download()
