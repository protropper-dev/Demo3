# app/services/rag_service_fixed.py
# RAG Service đã được sửa để hoạt động với dữ liệu có sẵn

import os
import logging
import pickle
import faiss
import numpy as np
from typing import List, Dict, Any, Optional
from transformers import AutoTokenizer, AutoModel
import torch

logger = logging.getLogger(__name__)

class RAGServiceFixed:
    """RAG Service hoạt động với dữ liệu chunks có sẵn"""
    
    def __init__(self):
        self.is_initialized = False
        self.tokenizer = None
        self.model = None
        self.device = None
        self.faiss_index = None
        self.documents_data = None
        self.chunks_metadata = []
        
    async def initialize(self):
        """Khởi tạo service với dữ liệu có sẵn"""
        try:
            logger.info("Đang khởi tạo RAG service fixed...")
            
            # Load embedding model
            model_path = "models/multilingual_e5_large"
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModel.from_pretrained(model_path)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            
            # Load dữ liệu
            data_dir = "data"
            faiss_path = os.path.join(data_dir, "all_faiss.index")
            pickle_path = os.path.join(data_dir, "all_embeddings.pkl")
            
            # Load FAISS index
            self.faiss_index = faiss.read_index(faiss_path)
            
            # Load documents data
            with open(pickle_path, 'rb') as f:
                self.documents_data = pickle.load(f)
            
            # Tạo chunks metadata
            self.chunks_metadata = []
            for doc_idx, doc in enumerate(self.documents_data):
                pdf_name = doc.get('pdf_name', 'Unknown')
                chunks = doc.get('chunks', [])
                
                for chunk_idx, chunk in enumerate(chunks):
                    self.chunks_metadata.append({
                        'doc_idx': doc_idx,
                        'chunk_idx': chunk_idx,
                        'pdf_name': pdf_name,
                        'content': chunk
                    })
            
            self.is_initialized = True
            logger.info(f"RAG service fixed initialized: {len(self.chunks_metadata)} chunks")
            
        except Exception as e:
            logger.error(f"Lỗi khởi tạo RAG service fixed: {e}")
            raise
    
    def encode_text(self, text: str) -> np.ndarray:
        """Encode text thành embedding"""
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1)
            return embeddings.cpu().numpy()
    
    def search_chunks(self, question: str, top_k: int = 5) -> List[Dict]:
        """Tìm kiếm chunks liên quan"""
        if not self.is_initialized:
            return []
        
        # Encode question
        question_embedding = self.encode_text(question)
        
        # FAISS search
        scores, indices = self.faiss_index.search(question_embedding.astype('float32'), top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if 0 <= idx < len(self.chunks_metadata):
                chunk_meta = self.chunks_metadata[idx]
                results.append({
                    'score': float(score),
                    'pdf_name': chunk_meta['pdf_name'],
                    'content': chunk_meta['content'],
                    'doc_idx': chunk_meta['doc_idx'],
                    'chunk_idx': chunk_meta['chunk_idx']
                })
        
        return results
    
    def generate_answer(self, question: str, search_results: List[Dict]) -> str:
        """Tạo câu trả lời từ search results"""
        if not search_results:
            return "Xin lỗi, tôi không tìm thấy thông tin liên quan trong cơ sở dữ liệu."
        
        # Lấy top results
        top_results = search_results[:3]
        
        answer_parts = []
        answer_parts.append("**An toàn thông tin** theo các tài liệu pháp lý và tiêu chuẩn:")
        answer_parts.append("")
        
        for i, result in enumerate(top_results, 1):
            pdf_name = result['pdf_name']
            content = result['content']
            
            # Tìm câu quan trọng
            sentences = content.split('.')
            important_sentences = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 30:
                    if any(keyword in sentence.lower() for keyword in ["an toàn thông tin", "information security", "bảo mật"]):
                        important_sentences.append(sentence)
            
            if important_sentences:
                answer_parts.append(f"**{i}. Theo {pdf_name}:**")
                for sentence in important_sentences[:2]:
                    answer_parts.append(f"• {sentence}.")
            else:
                answer_parts.append(f"**{i}. Theo {pdf_name}:**")
                answer_parts.append(f"• {content[:300]}...")
            
            answer_parts.append("")
        
        answer_parts.append("---")
        answer_parts.append("**Tóm lại:** An toàn thông tin là lĩnh vực bảo vệ thông tin và hệ thống thông tin khỏi các mối đe dọa, đảm bảo tính bảo mật, toàn vẹn và sẵn sàng của dữ liệu.")
        
        return "\n".join(answer_parts)
    
    async def query(self, question: str, top_k: int = 5, filter_category: Optional[str] = None) -> Dict[str, Any]:
        """Xử lý query"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Search chunks
            search_results = self.search_chunks(question, top_k)
            
            # Generate answer
            answer = self.generate_answer(question, search_results)
            
            # Create sources
            sources = []
            for result in search_results:
                sources.append({
                    "filename": result['pdf_name'],
                    "content": result['content'][:300] + "..." if len(result['content']) > 300 else result['content'],
                    "similarity": result['score']
                })
            
            return {
                "question": question,
                "answer": answer,
                "sources": sources,
                "total_sources": len(sources)
            }
            
        except Exception as e:
            logger.error(f"Lỗi trong query: {e}")
            return {
                "question": question,
                "answer": "Xin lỗi, tôi không thể trả lời câu hỏi này lúc này.",
                "sources": [],
                "total_sources": 0,
                "error": str(e)
            }

# Global instance
_rag_service_fixed = None

async def get_rag_service_fixed():
    """Get RAG service fixed instance"""
    global _rag_service_fixed
    if _rag_service_fixed is None:
        _rag_service_fixed = RAGServiceFixed()
        await _rag_service_fixed.initialize()
    return _rag_service_fixed
