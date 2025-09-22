# app/utils/rag_utils.py
# Utility functions cho RAG (tích hợp từ backend2)

import os
import faiss
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class RAGUtils:
    """Utility functions cho RAG operations"""
    
    @staticmethod
    def load_embedding_and_chunks():
        """
        Load FAISS index và chunks từ file đã lưu
        """
        try:
            # Load FAISS index
            if os.path.exists(settings.FAISS_PATH):
                faiss_index = faiss.read_index(settings.FAISS_PATH)
                logger.info(f"✅ FAISS Index loaded: {faiss_index.ntotal} vectors")
            else:
                logger.warning(f"File FAISS không tồn tại: {settings.FAISS_PATH}")
                return None, []
            
            # Load chunks
            if os.path.exists(settings.PICKLE_PATH):
                with open(settings.PICKLE_PATH, "rb") as f:
                    data = pickle.load(f)
                all_chunks = []
                for item in data:
                    if isinstance(item, dict) and "chunks" in item:
                        all_chunks.extend(item["chunks"])
                
                logger.info(f"✅ Chunks loaded: {len(all_chunks)} chunks")
                return faiss_index, all_chunks
            else:
                logger.warning(f"File pickle không tồn tại: {settings.PICKLE_PATH}")
                return faiss_index, []
                
        except Exception as e:
            logger.error(f"❌ Lỗi khi load embedding và chunks: {e}")
            return None, []
    
    @staticmethod
    def get_relevant_chunks(query_vector, faiss_index, chunks, top_k=3, max_tokens_per_chunk=5120):
        """
        Tìm các đoạn văn bản liên quan nhất với query vector
        """
        try:
            D, I = faiss_index.search(query_vector.astype("float32"), top_k)

            context_chunks = []
            for i in I[0]:
                if i < len(chunks):
                    chunk = chunks[i]
                    # Có thể thêm logic tokenize nếu cần
                    context_chunks.append(chunk.strip())

            return context_chunks
        except Exception as e:
            logger.error(f"❌ Lỗi khi tìm chunks liên quan: {e}")
            return []
    
    @staticmethod
    def build_prompt(context_chunks: List[str], question: str) -> str:
        """
        Tạo prompt cho mô hình với context và câu hỏi
        """
        context = "\n---\n".join(context_chunks)
        return f"""<|im_start|>system
Bạn là một trợ lý AI chuyên về an toàn thông tin tại Việt Nam. Chỉ trả lời người dùng dựa trên thông tin được cung cấp dưới đây về luật pháp, quy định và tiêu chuẩn an toàn thông tin Việt Nam. Nếu không có thông tin phù hợp, hãy trả lời: "Tôi không có thông tin về câu hỏi này trong cơ sở dữ liệu hiện tại." Không được bịa đặt thông tin.
<|im_end|>
<|im_start|>user
Thông tin tham khảo:
{context}

Câu hỏi: {question}
<|im_end|>
<|im_start|>assistant
"""
    
    @staticmethod
    def check_embedding_data_availability() -> Dict[str, Any]:
        """
        Kiểm tra tính khả dụng của dữ liệu embedding
        """
        result = {
            "faiss_available": False,
            "pickle_available": False,
            "faiss_size": 0,
            "pickle_size": 0,
            "total_chunks": 0,
            "total_documents": 0
        }
        
        try:
            # Kiểm tra FAISS
            if os.path.exists(settings.FAISS_PATH):
                result["faiss_available"] = True
                result["faiss_size"] = os.path.getsize(settings.FAISS_PATH) / (1024*1024)  # MB
            
            # Kiểm tra Pickle
            if os.path.exists(settings.PICKLE_PATH):
                result["pickle_available"] = True
                result["pickle_size"] = os.path.getsize(settings.PICKLE_PATH) / (1024*1024)  # MB
                
                # Load để đếm chunks và documents
                try:
                    with open(settings.PICKLE_PATH, "rb") as f:
                        data = pickle.load(f)
                    
                    result["total_documents"] = len(data)
                    
                    total_chunks = 0
                    for item in data:
                        if isinstance(item, dict) and "chunks" in item:
                            total_chunks += len(item["chunks"])
                    
                    result["total_chunks"] = total_chunks
                    
                except Exception as e:
                    logger.warning(f"Không thể load pickle data để đếm: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra embedding data: {e}")
            result["error"] = str(e)
            return result
    
    @staticmethod
    def test_faiss_search(query_vector: Optional[np.ndarray] = None, top_k: int = 5) -> Dict[str, Any]:
        """
        Test FAISS search với vector
        """
        try:
            faiss_index, chunks = RAGUtils.load_embedding_and_chunks()
            
            if faiss_index is None:
                return {"error": "FAISS index không có sẵn"}
            
            if query_vector is None:
                # Tạo random vector để test
                query_vector = np.random.random((1, faiss_index.d)).astype('float32')
            
            # Search
            D, I = faiss_index.search(query_vector, top_k)
            
            # Lấy chunks
            found_chunks = []
            for i, idx in enumerate(I[0]):
                if idx < len(chunks):
                    chunk = chunks[idx]
                    found_chunks.append({
                        "index": idx,
                        "distance": float(D[0][i]),
                        "preview": chunk[:100] + "..." if len(chunk) > 100 else chunk
                    })
            
            return {
                "success": True,
                "query_shape": query_vector.shape,
                "faiss_dimensions": faiss_index.d,
                "total_vectors": faiss_index.ntotal,
                "found_chunks": found_chunks
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi test FAISS search: {e}")
            return {"error": str(e)}

class FileUtils:
    """Utility functions cho file operations"""
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """
        Lấy thông tin file
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            return {
                "filename": os.path.basename(file_path),
                "size": stat.st_size,
                "size_mb": stat.st_size / (1024*1024),
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "extension": Path(file_path).suffix.lower()
            }
        except Exception as e:
            logger.error(f"Lỗi khi lấy thông tin file: {e}")
            return None
    
    @staticmethod
    def list_uploaded_files() -> List[Dict[str, Any]]:
        """
        Liệt kê các file đã upload
        """
        try:
            upload_dir = Path(settings.UPLOAD_DIR)
            if not upload_dir.exists():
                return []
            
            files = []
            for file_path in upload_dir.iterdir():
                if file_path.is_file():
                    file_info = FileUtils.get_file_info(str(file_path))
                    if file_info:
                        files.append(file_info)
            
            return files
            
        except Exception as e:
            logger.error(f"Lỗi khi liệt kê file: {e}")
            return []
    
    @staticmethod
    def is_allowed_file(filename: str) -> bool:
        """
        Kiểm tra file có được phép upload không
        """
        allowed_extensions = {".pdf", ".doc", ".docx", ".txt"}
        file_extension = Path(filename).suffix.lower()
        return file_extension in allowed_extensions
