# app/services/llm_service.py
# Service xử lý LLM sử dụng vinallama-2.7b-chat model

import os
import logging
import torch
from typing import List, Dict, Any, Optional
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    BitsAndBytesConfig,
    pipeline
)
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """Service xử lý LLM sử dụng vinallama-2.7b-chat"""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Sử dụng device: {self.device}")
        
    def load_model(self):
        """Load model LLM"""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model path không tồn tại: {self.model_path}")
            
            logger.info(f"Đang load model từ {self.model_path}")
            
            # Cấu hình quantization để tiết kiệm memory
            quantization_config = None
            if self.device == "cuda" and settings.USE_QUANTIZATION:
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )
            
            # Thêm pad token nếu chưa có
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model với quantization config
            if quantization_config is not None:
                logger.info("Loading model with 4-bit quantization...")
                # Sử dụng quantization - KHÔNG dùng device_map="auto" để tránh lỗi .to()
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    quantization_config=quantization_config,
                    trust_remote_code=True,
                    torch_dtype=torch.float16
                )
                
                # Move model to CUDA manually nếu available
                if self.device == "cuda":
                    # Quantized model đã ở đúng device, không cần .to()
                    pass
                
                logger.info("✅ Quantized model loaded successfully")
                
            else:
                logger.info("Loading model without quantization...")
                # Không sử dụng quantization
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    device_map="auto" if self.device == "cuda" else None,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    trust_remote_code=True
                )
                
                # Chỉ move model khi không dùng quantization
                if self.device == "cuda" and not hasattr(self.model, 'hf_device_map'):
                    self.model = self.model.to(self.device)
            
            logger.info("Model đã được load thành công")
            
        except Exception as e:
            logger.error(f"Lỗi khi load model: {e}")
            raise
    
    def generate_response(self, 
                         query: str, 
                         context_docs: List[Dict] = None,
                         max_new_tokens: int = 256,
                         generation_config: Dict = None) -> str:
        """Tạo câu trả lời từ query và context"""
        if self.model is None or self.tokenizer is None:
            self.load_model()
        
        try:
            # Tạo prompt từ query và context
            prompt = self._create_prompt(query, context_docs)
            
            # Tokenize input - safe cho quantized models
            inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=2048)
            
            # Move inputs to correct device
            device = None
            if hasattr(self.model, 'device'):
                device = self.model.device
            elif hasattr(self.model, 'hf_device_map'):
                # Model with device_map, get first device
                device = next(iter(self.model.hf_device_map.values()))
            elif torch.cuda.is_available():
                device = 'cuda'
            else:
                device = 'cpu'
            
            if device:
                inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Cấu hình generation cho responses chính xác và ổn định
            if generation_config is None:
                # Default generation config - tối ưu cho tiếng Việt
                gen_config = self.model.generation_config
                gen_config.max_new_tokens = max_new_tokens
                gen_config.do_sample = True  # Enable sampling
                gen_config.temperature = 0.5  # Giảm để ổn định hơn, giảm lỗi chính tả
                gen_config.top_p = 0.8  # Giảm để tập trung hơn
                gen_config.top_k = 40  # Giảm để ổn định hơn
                gen_config.repetition_penalty = 1.2  # Tăng để tránh lặp từ
                gen_config.no_repeat_ngram_size = 3  # Tăng để tránh lặp cụm từ
                gen_config.num_return_sequences = 1
                gen_config.num_beams = 1  # Greedy decoding
                gen_config.early_stopping = True  # Bật early stopping
            else:
                # Use custom generation config với defaults tối ưu
                gen_config = self.model.generation_config
                gen_config.max_new_tokens = generation_config.get('max_new_tokens', max_new_tokens)
                gen_config.do_sample = generation_config.get('do_sample', True)
                gen_config.temperature = generation_config.get('temperature', 0.5)  # Default tối ưu
                gen_config.top_p = generation_config.get('top_p', 0.8)  # Default tối ưu
                gen_config.top_k = generation_config.get('top_k', 40)  # Default tối ưu
                gen_config.repetition_penalty = generation_config.get('repetition_penalty', 1.2)  # Default tối ưu
                gen_config.no_repeat_ngram_size = generation_config.get('no_repeat_ngram_size', 3)  # Default tối ưu
                gen_config.num_return_sequences = generation_config.get('num_return_sequences', 1)
                gen_config.num_beams = generation_config.get('num_beams', 1)
                gen_config.early_stopping = generation_config.get('early_stopping', True)  # Default tối ưu
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids=inputs['input_ids'],
                    attention_mask=inputs['attention_mask'],
                    generation_config=gen_config,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            answer = generated_text[len(prompt):].strip()
            
            # Làm sạch response
            answer = self._clean_response(answer)
            
            logger.info(f"Đã tạo response cho query: {query[:50]}...")
            return answer
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo response: {e}")
            return "Xin lỗi, tôi không thể tạo câu trả lời lúc này. Vui lòng thử lại sau."
    
    def _create_prompt(self, query: str, context_docs: List[Dict] = None) -> str:
        """Tạo prompt từ query và context documents theo định dạng ChatML"""
        
        # Enhanced system prompt cho responses tự nhiên
        system_prompt = """Bạn là chuyên gia an toàn thông tin với kiến thức sâu rộng. Nhiệm vụ của bạn là:

1. Đọc và hiểu các tài liệu được cung cấp
2. Tổng hợp thông tin từ nhiều nguồn một cách thông minh
3. Trả lời câu hỏi bằng ngôn ngữ tự nhiên, dễ hiểu
4. Cung cấp thông tin toàn diện và có cấu trúc logic
5. Sử dụng tiếng Việt chuyên nghiệp

Hãy tạo câu trả lời chi tiết, có cấu trúc và dễ hiểu. Không chỉ trích dẫn mà hãy giải thích và tổng hợp thông tin."""

        # Context từ RAG với metadata
        context_text = ""
        if context_docs:
            context_parts = []
            for i, doc in enumerate(context_docs[:3], 1):
                filename = doc.get('metadata', {}).get('filename', f'Tài liệu {i}')
                content = doc['content'][:800]  # Tăng độ dài để có nhiều context hơn
                
                context_parts.append(f"=== Nguồn {i}: {filename} ===\n{content.strip()}")
            
            context_text = "\n\n".join(context_parts)
        
        # Tạo prompt với instructions rõ ràng
        prompt = f"""<|im_start|>system
{system_prompt}
<|im_end|>
<|im_start|>user
Dưới đây là các tài liệu chuyên môn về an toàn thông tin:

{context_text}

Dựa trên các tài liệu trên, hãy trả lời câu hỏi sau một cách chi tiết và dễ hiểu:

Câu hỏi: {query}

Yêu cầu:
- Trả lời bằng tiếng Việt tự nhiên
- Tổng hợp thông tin từ các nguồn
- Cung cấp định nghĩa rõ ràng
- Giải thích cách hoạt động (nếu có)
- Đưa ra các loại/phân loại (nếu có)
- Nêu tác hại và biện pháp phòng chống (nếu có)
- Cấu trúc logic và dễ đọc
<|im_end|>
<|im_start|>assistant
"""
        
        return prompt.strip()
    
    def _clean_response(self, response: str) -> str:
        """Làm sạch response"""
        # Loại bỏ các token đặc biệt ChatML
        response = response.replace("<|endoftext|>", "")
        response = response.replace("<|im_start|>", "")
        response = response.replace("<|im_end|>", "")
        response = response.replace("<|assistant|>", "")
        response = response.replace("<|user|>", "")
        response = response.replace("<|system|>", "")
        
        # Loại bỏ dòng trống thừa và chuẩn hóa
        lines = response.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def get_relevant_chunks_from_faiss(self, query: str, faiss_index, chunks: List[str], 
                                     top_k: int = 3, max_tokens_per_chunk: int = 512) -> List[str]:
        """Lấy các chunks liên quan từ FAISS index (tương thích với RAG_train.ipynb)"""
        try:
            from sentence_transformers import SentenceTransformer
            
            # Load embedding model nếu cần
            if not hasattr(self, 'embedding_model'):
                # Giả sử embedding model path được config
                from app.core.config import settings
                self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL_PATH)
            
            # Tạo query vector
            query_vector = self.embedding_model.encode([query])
            
            # Tìm kiếm trong FAISS
            import numpy as np
            import faiss as faiss_lib
            D, I = faiss_index.search(np.array(query_vector).astype("float32"), top_k)
            
            # Lấy chunks tương ứng
            context_chunks = []
            for i in I[0]:
                if i < len(chunks):
                    chunk = chunks[i]
                    # Giới hạn độ dài chunk
                    tokens = self.tokenizer.tokenize(chunk)
                    if len(tokens) > max_tokens_per_chunk:
                        tokens = tokens[:max_tokens_per_chunk]
                        chunk = self.tokenizer.convert_tokens_to_string(tokens)
                    context_chunks.append(chunk.strip())
            
            return context_chunks
            
        except Exception as e:
            logger.error(f"Lỗi lấy relevant chunks: {e}")
            return []
    
    def rag_answer(self, query: str, faiss_index=None, chunks: List[str] = None, 
                   top_k: int = 3) -> str:
        """Tạo RAG answer như trong RAG_train.ipynb"""
        try:
            if faiss_index is not None and chunks is not None:
                # Sử dụng FAISS để lấy context
                context_chunks = self.get_relevant_chunks_from_faiss(query, faiss_index, chunks, top_k)
                
                # Chuyển đổi sang format phù hợp
                context_docs = []
                for chunk in context_chunks:
                    context_docs.append({
                        'content': chunk,
                        'metadata': {'source': 'faiss_search'}
                    })
                
                return self.generate_response(query, context_docs)
            else:
                # Fallback về generate_response thông thường
                return self.generate_response(query, [])
                
        except Exception as e:
            logger.error(f"Lỗi trong rag_answer: {e}")
            return "Xin lỗi, tôi không thể trả lời câu hỏi này lúc này."
    
    def chat_with_history(self, 
                         query: str, 
                         chat_history: List[Dict] = None,
                         context_docs: List[Dict] = None) -> Dict[str, Any]:
        """Chat với lịch sử hội thoại"""
        if self.model is None or self.tokenizer is None:
            self.load_model()
        
        try:
            # Tạo prompt với lịch sử
            prompt = self._create_chat_prompt(query, chat_history, context_docs)
            
            # Tokenize input
            from app.utils.model_utils import safe_tokenize_to_device
            encoding = safe_tokenize_to_device(self.tokenizer, prompt, self.model)
            
            # Cấu hình generation
            generation_config = self.model.generation_config
            generation_config.max_new_tokens = 512
            generation_config.num_beams = 3  # Beam search với 3 beams
            generation_config.early_stopping = True  # OK vì num_beams > 1
            generation_config.do_sample = False
            generation_config.num_return_sequences = 1
            generation_config.repetition_penalty = 1.2
            generation_config.no_repeat_ngram_size = 3
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids=inputs['input_ids'],
                    attention_mask=inputs['attention_mask'],
                    generation_config=gen_config,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            answer = generated_text[len(prompt):].strip()
            answer = self._clean_response(answer)
            
            return {
                "response": answer,
                "query": query,
                "context_used": len(context_docs) if context_docs else 0
            }
            
        except Exception as e:
            logger.error(f"Lỗi trong chat: {e}")
            return {
                "response": "Xin lỗi, tôi không thể trả lời lúc này.",
                "query": query,
                "context_used": 0,
                "error": str(e)
            }
    
    def _create_chat_prompt(self, 
                           query: str, 
                           chat_history: List[Dict] = None,
                           context_docs: List[Dict] = None) -> str:
        """Tạo prompt cho chat với lịch sử theo định dạng ChatML"""
        
        system_prompt = """Bạn là một trợ lý AI an toàn thông tin. Chỉ trả lời người dùng dựa trên thông tin được cung cấp dưới đây. Nếu không biết, hãy trả lời: "Tôi không có thông tin về câu hỏi này." Không được bịa."""
        
        # Context từ RAG
        context_text = ""
        if context_docs:
            context_chunks = []
            for doc in context_docs[:2]:  # Chỉ lấy 2 docs để tiết kiệm tokens
                chunk_content = doc['content'][:300]  # Giới hạn độ dài
                context_chunks.append(chunk_content.strip())
            context_text = "\n---\n".join(context_chunks)
        
        # Xây dựng prompt với lịch sử hội thoại
        messages = []
        
        # System message
        system_content = system_prompt
        if context_text:
            system_content += f"\n\nThông tin tham khảo:\n{context_text}"
        
        messages.append(f"<|im_start|>system\n{system_content}\n<|im_end|>")
        
        # Chat history
        if chat_history:
            for msg in chat_history[-3:]:  # Chỉ lấy 3 tin nhắn gần nhất
                role = msg.get("role", "user")
                content = msg.get("content", "")
                messages.append(f"<|im_start|>{role}\n{content}\n<|im_end|>")
        
        # Current query
        messages.append(f"<|im_start|>user\n{query}\n<|im_end|>")
        messages.append("<|im_start|>assistant")
        
        return "\n".join(messages)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Lấy thông tin về model"""
        if self.model is None:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "model_path": self.model_path,
            "device": self.device,
            "model_type": "vinallama-2.7b-chat",
            "max_length": self.tokenizer.model_max_length if self.tokenizer else "unknown"
        }
