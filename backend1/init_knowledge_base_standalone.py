#!/usr/bin/env python3
"""
Script khởi tạo Knowledge Base độc lập
Dựa trên /d:/Vian/Demo3/thamkhao/new_embeding.py
"""

import os
import sys
import logging
import torch
from datetime import datetime

# Thêm backend vào Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import services
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('knowledge_base_init_standalone.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Khởi tạo Knowledge Base như trong new_embeding.py"""
    
    print("🚀 Bắt đầu khởi tạo Knowledge Base...")
    print(f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Kiểm tra GPU
    print(f"\n🔍 Kiểm tra GPU:")
    print(f"Số lượng GPU: {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
        print(f"  Tổng VRAM: {torch.cuda.get_device_properties(i).total_memory / 1024 / 1024**2:.2f} GB")
    
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"\n🎯 Đang sử dụng: {device}")
    
    # Cấu hình đường dẫn (giống new_embeding.py)
    model_path = "D:/Vian/MODELS/multilingual_e5_large"
    input_folders = [
        "D:/Vian/Demo3/documents/Luat",
        "D:/Vian/Demo3/documents/TaiLieuTiengAnh", 
        "D:/Vian/Demo3/documents/TaiLieuTiengViet"
    ]
    output_dir = "D:/Vian/Demo3/backend/data"
    
    print(f"\n📁 Cấu hình đường dẫn:")
    print(f"Model: {model_path}")
    print(f"Output: {output_dir}")
    print(f"Input folders:")
    for folder in input_folders:
        exists = "✅" if os.path.exists(folder) else "❌"
        print(f"  {exists} {folder}")
    
    # Kiểm tra model path
    if not os.path.exists(model_path):
        print(f"❌ Model path không tồn tại: {model_path}")
        return False
    
    # Kiểm tra ít nhất một input folder tồn tại
    existing_folders = [f for f in input_folders if os.path.exists(f)]
    if not existing_folders:
        print("❌ Không tìm thấy thư mục documents nào!")
        return False
    
    print(f"\n📊 Sẽ xử lý {len(existing_folders)} thư mục:")
    for folder in existing_folders:
        print(f"  ✅ {folder}")
    
    try:
        # Khởi tạo EmbeddingService
        print(f"\n🔄 Khởi tạo EmbeddingService...")
        embedding_service = EmbeddingService(
            model_path=model_path,
            output_dir=output_dir
        )
        
        # Load model
        print("📥 Đang load model embedding...")
        embedding_service.load_model()
        print("✅ Model đã được load thành công!")
        
        # Xử lý tất cả documents
        print(f"\n🔄 Bắt đầu xử lý documents...")
        result = embedding_service.process_all_documents(
            input_folders=existing_folders,
            force_rebuild=False  # Có thể thay đổi thành True để force rebuild
        )
        
        # Hiển thị kết quả
        print(f"\n📊 KẾT QUẢ XỬ LÝ:")
        print(f"  📁 Tổng files: {result.get('total_files', 0)}")
        print(f"  ✅ Đã xử lý: {result.get('processed', 0)}")
        print(f"  ⏭️ Đã bỏ qua: {result.get('skipped', 0)}")
        print(f"  ❌ Lỗi: {result.get('errors', 0)}")
        
        if 'error' in result:
            print(f"❌ Lỗi: {result['error']}")
            return False
        
        # Hiển thị đường dẫn files kết quả
        print(f"\n📂 FILES KẾT QUẢ:")
        print(f"  🗃️ FAISS Index: {result.get('all_faiss_path', 'N/A')}")
        print(f"  📦 Pickle Data: {result.get('all_pickle_path', 'N/A')}")
        
        # Kiểm tra files đã tạo
        faiss_path = result.get('all_faiss_path')
        pickle_path = result.get('all_pickle_path')
        
        if faiss_path and os.path.exists(faiss_path):
            size_mb = os.path.getsize(faiss_path) / 1024 / 1024
            print(f"  ✅ FAISS Index: {size_mb:.2f} MB")
        
        if pickle_path and os.path.exists(pickle_path):
            size_mb = os.path.getsize(pickle_path) / 1024 / 1024
            print(f"  ✅ Pickle Data: {size_mb:.2f} MB")
        
        # Test VectorStore với dữ liệu đã tạo
        if faiss_path and pickle_path and os.path.exists(faiss_path) and os.path.exists(pickle_path):
            print(f"\n🧪 Test VectorStore...")
            vector_store = VectorStore(output_dir, "documents")
            vector_store.load_from_existing_files(faiss_path, pickle_path)
            
            stats = vector_store.get_collection_stats()
            print(f"  📊 Thống kê VectorStore:")
            print(f"    - Documents: {stats.get('total_documents', 0)}")
            print(f"    - Vectors: {stats.get('total_vectors', 0)}")
            print(f"    - Categories: {stats.get('categories', {})}")
            print(f"    - File types: {stats.get('file_types', {})}")
        
        print(f"\n🎉 HOÀN THÀNH!")
        print(f"⏰ Thời gian kết thúc: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📝 Log chi tiết: knowledge_base_init_standalone.log")
        
        return True
        
    except Exception as e:
        print(f"\n❌ LỖI NGHIÊM TRỌNG: {e}")
        logger.exception("Lỗi khi khởi tạo knowledge base")
        return False

def check_requirements():
    """Kiểm tra các requirements cần thiết"""
    print("🔍 Kiểm tra requirements...")
    
    required_packages = [
        'torch', 'sentence_transformers', 'transformers', 
        'underthesea', 'faiss', 'numpy', 'PIL', 'fitz'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Thiếu packages: {', '.join(missing_packages)}")
        print("Chạy: pip install -r requirements.txt")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 KNOWLEDGE BASE INITIALIZATION")
    print("=" * 60)
    
    # Kiểm tra requirements
    if not check_requirements():
        sys.exit(1)
    
    # Chạy khởi tạo
    success = main()
    
    if success:
        print("\n✅ Knowledge Base đã được khởi tạo thành công!")
        print("🚀 Bây giờ bạn có thể chạy server: python main.py")
        sys.exit(0)
    else:
        print("\n❌ Khởi tạo Knowledge Base thất bại!")
        print("📝 Kiểm tra log để biết chi tiết: knowledge_base_init_standalone.log")
        sys.exit(1)
