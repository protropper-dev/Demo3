# app/services/vector_store.py
# Service quản lý vector store sử dụng FAISS

import os
import logging
import json
import pickle
from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from langchain.schema import Document

logger = logging.getLogger(__name__)

class VectorStore:
    """Service quản lý vector store sử dụng FAISS"""
    
    def __init__(self, persist_directory: str, collection_name: str = "documents"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.faiss_index = None
        self.documents_data = []
        
        # Đường dẫn files
        self.faiss_index_path = os.path.join(persist_directory, f"{collection_name}_faiss.index")
        self.documents_data_path = os.path.join(persist_directory, f"{collection_name}_data.pkl")
        
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(persist_directory, exist_ok=True)
        
    def initialize_index(self, dimension: int = 1024):
        """Khởi tạo FAISS index"""
        try:
            if os.path.exists(self.faiss_index_path):
                # Load index hiện có
                self.faiss_index = faiss.read_index(self.faiss_index_path)
                logger.info(f"Đã load FAISS index từ {self.faiss_index_path}")
            else:
                # Tạo index mới
                self.faiss_index = faiss.IndexFlatL2(dimension)
                logger.info(f"Đã tạo FAISS index mới với dimension {dimension}")
                
            # Load documents data
            if os.path.exists(self.documents_data_path):
                with open(self.documents_data_path, 'rb') as f:
                    self.documents_data = pickle.load(f)
                logger.info(f"Đã load {len(self.documents_data)} documents data")
            else:
                self.documents_data = []
                
        except Exception as e:
            logger.error(f"Lỗi khi khởi tạo FAISS index: {e}")
            raise
    
    def get_or_create_collection(self, dimension: int = 1024):
        """Lấy hoặc tạo collection (tương thích với interface cũ)"""
        try:
            self.initialize_index(dimension)
            logger.info(f"Collection '{self.collection_name}' đã sẵn sàng")
        except Exception as e:
            logger.error(f"Lỗi khi tạo/lấy collection: {e}")
            raise
    
    def add_documents(self, documents: List[Document], embeddings: List[np.ndarray]):
        """Thêm documents và embeddings vào FAISS index"""
        if self.faiss_index is None:
            # Tự động detect dimension từ embedding đầu tiên
            if embeddings:
                dimension = embeddings[0].shape[0]
                self.get_or_create_collection(dimension)
            else:
                self.get_or_create_collection()
        
        try:
            # Chuẩn bị embeddings cho FAISS
            embeddings_matrix = np.vstack([emb.astype(np.float32) for emb in embeddings])
            
            # Thêm embeddings vào FAISS index
            start_idx = self.faiss_index.ntotal
            self.faiss_index.add(embeddings_matrix)
            
            # Lưu documents data
            for i, doc in enumerate(documents):
                doc_data = {
                    'id': f"{doc.metadata.get('filename', 'unknown')}_{doc.metadata.get('chunk_id', start_idx + i)}",
                    'content': doc.page_content,
                    'metadata': doc.metadata.copy(),
                    'index_position': start_idx + i,
                    'created_at': datetime.now().isoformat()
                }
                doc_data['metadata']['text_length'] = len(doc.page_content)
                self.documents_data.append(doc_data)
            
            # Lưu xuống file
            self._save_to_disk()
            
            logger.info(f"Đã thêm {len(documents)} documents vào FAISS vector store")
            
        except Exception as e:
            logger.error(f"Lỗi khi thêm documents: {e}")
            raise
    
    def _save_to_disk(self):
        """Lưu FAISS index và documents data xuống đĩa"""
        try:
            # Lưu FAISS index
            faiss.write_index(self.faiss_index, self.faiss_index_path)
            
            # Lưu documents data
            with open(self.documents_data_path, 'wb') as f:
                pickle.dump(self.documents_data, f)
                
            logger.debug("Đã lưu FAISS index và documents data xuống đĩa")
            
        except Exception as e:
            logger.error(f"Lỗi khi lưu xuống đĩa: {e}")
            raise
    
    def search_similar(self, query_embedding: np.ndarray, 
                      top_k: int = 5, 
                      filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """Tìm kiếm documents tương đồng bằng FAISS"""
        if self.faiss_index is None:
            self.get_or_create_collection()
        
        try:
            # Chuẩn bị query embedding
            query_vector = query_embedding.astype(np.float32).reshape(1, -1)
            
            # Tìm kiếm trong FAISS
            distances, indices = self.faiss_index.search(query_vector, top_k)
            
            # Chuyển đổi kết quả
            similar_docs = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx >= 0 and idx < len(self.documents_data):
                    doc_data = self.documents_data[idx]
                    
                    # Áp dụng filter nếu có
                    if filter_metadata:
                        match = True
                        for key, value in filter_metadata.items():
                            if doc_data['metadata'].get(key) != value:
                                match = False
                                break
                        if not match:
                            continue
                    
                    # Tính similarity từ L2 distance
                    # Với FAISS IndexFlatL2, similarity = 1 / (1 + distance)
                    similarity = 1.0 / (1.0 + float(distance))
                    
                    doc_info = {
                        'content': doc_data['content'],
                        'metadata': doc_data['metadata'],
                        'distance': float(distance),
                        'similarity': similarity,
                        'index_position': doc_data['index_position']
                    }
                    similar_docs.append(doc_info)
            
            logger.info(f"Tìm thấy {len(similar_docs)} documents tương đồng")
            return similar_docs
            
        except Exception as e:
            logger.error(f"Lỗi khi tìm kiếm: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Lấy thống kê về collection"""
        if self.faiss_index is None:
            self.get_or_create_collection()
        
        try:
            # Đếm tổng số documents
            total_documents = len(self.documents_data)
            total_vectors = self.faiss_index.ntotal if self.faiss_index else 0
            
            # Phân tích categories
            categories = {}
            file_types = {}
            
            for doc_data in self.documents_data:
                metadata = doc_data['metadata']
                
                # Category
                category = metadata.get('category', 'unknown')
                categories[category] = categories.get(category, 0) + 1
                
                # File type
                filename = metadata.get('filename', 'unknown')
                if '.' in filename:
                    ext = filename.split('.')[-1].lower()
                    file_types[ext] = file_types.get(ext, 0) + 1
            
            # Thống kê kích thước
            avg_text_length = 0
            if self.documents_data:
                total_length = sum(doc['metadata'].get('text_length', 0) for doc in self.documents_data)
                avg_text_length = total_length / len(self.documents_data)
            
            return {
                'total_documents': total_documents,
                'total_vectors': total_vectors,
                'categories': categories,
                'file_types': file_types,
                'avg_text_length': round(avg_text_length, 2),
                'collection_name': self.collection_name,
                'faiss_index_path': self.faiss_index_path,
                'documents_data_path': self.documents_data_path
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy thống kê: {e}")
            return {'error': str(e)}
    
    def delete_collection(self):
        """Xóa collection (xóa các file FAISS và data)"""
        try:
            # Xóa FAISS index file
            if os.path.exists(self.faiss_index_path):
                os.remove(self.faiss_index_path)
                logger.info(f"Đã xóa FAISS index: {self.faiss_index_path}")
            
            # Xóa documents data file
            if os.path.exists(self.documents_data_path):
                os.remove(self.documents_data_path)
                logger.info(f"Đã xóa documents data: {self.documents_data_path}")
            
            # Reset in-memory data
            self.faiss_index = None
            self.documents_data = []
            
            logger.info(f"Đã xóa collection '{self.collection_name}'")
            
        except Exception as e:
            logger.error(f"Lỗi khi xóa collection: {e}")
            raise
    
    def reset_collection(self):
        """Reset collection (xóa và tạo lại)"""
        try:
            self.delete_collection()
            self.get_or_create_collection()
            logger.info("Đã reset collection thành công")
            
        except Exception as e:
            logger.error(f"Lỗi khi reset collection: {e}")
            raise
    
    def get_faiss_index(self):
        """Lấy FAISS index (để sử dụng trực tiếp)"""
        if self.faiss_index is None:
            self.get_or_create_collection()
        return self.faiss_index
    
    def get_all_chunks(self) -> List[str]:
        """Lấy tất cả chunks text (để tương thích với RAG_train.ipynb)"""
        return [doc_data['content'] for doc_data in self.documents_data]
    
    def load_from_existing_files(self, faiss_path: str, pickle_path: str):
        """Load từ các file FAISS và pickle có sẵn"""
        try:
            if os.path.exists(faiss_path) and os.path.exists(pickle_path):
                # Load FAISS index
                self.faiss_index = faiss.read_index(faiss_path)
                
                # Load pickle data
                with open(pickle_path, 'rb') as f:
                    pickle_data = pickle.load(f)
                
                # Chuyển đổi format nếu cần
                self.documents_data = []
                if isinstance(pickle_data, list):
                    # Format mới: list of documents data
                    if pickle_data and 'content' in pickle_data[0]:
                        self.documents_data = pickle_data
                    else:
                        # Format cũ: list of embedding data, cần chuyển đổi
                        for i, item in enumerate(pickle_data):
                            if 'chunks' in item:
                                for j, chunk in enumerate(item['chunks']):
                                    doc_data = {
                                        'id': f"{item.get('pdf_name', 'unknown')}_{i}_{j}",
                                        'content': chunk,
                                        'metadata': {
                                            'filename': item.get('pdf_name', 'unknown'),
                                            'chunk_id': j,
                                            'source': item.get('doc_path', 'unknown')
                                        },
                                        'index_position': len(self.documents_data),
                                        'created_at': item.get('created_at', datetime.now().isoformat())
                                    }
                                    self.documents_data.append(doc_data)
                
                logger.info(f"Đã load {len(self.documents_data)} documents từ {pickle_path}")
                logger.info(f"Đã load FAISS index với {self.faiss_index.ntotal} vectors từ {faiss_path}")
                
            else:
                logger.warning(f"Không tìm thấy files: {faiss_path} hoặc {pickle_path}")
                
        except Exception as e:
            logger.error(f"Lỗi khi load từ existing files: {e}")
            raise
