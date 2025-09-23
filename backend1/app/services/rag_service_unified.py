#!/usr/bin/env python3
"""
RAG Service Unified - API thống nhất cho query/response
Hợp nhất tất cả các chức năng RAG thành một service mạnh mẽ
"""

import os
import logging
import pickle
import faiss
import numpy as np
from typing import List, Dict, Any, Optional, Union
from transformers import AutoTokenizer, AutoModel
import torch
import time
from datetime import datetime
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

class RAGServiceUnified:
    """RAG Service thống nhất - xử lý tất cả query/response"""
    
    def __init__(self):
        self.is_initialized = False
        self.tokenizer = None
        self.model = None
        self.device = None
        self.faiss_index = None
        self.documents_data = None
        self.chunks_metadata = []
        self.total_chunks = 0
        self.total_documents = 0
        self.initialization_time = None
        
        # LLM Service cho text generation
        self.llm_service = None
        
        # Cấu hình mặc định
        self.default_top_k = 5
        self.default_similarity_threshold = 0.3
        self.max_answer_length = 2000
        self.max_context_length = 1500
        self.use_llm_generation = True  # Tạm thời disable để test template - set True để enable LLM
        
    async def initialize(self):
        """Khởi tạo service với dữ liệu có sẵn"""
        try:
            start_time = time.time()
            logger.info("🚀 Đang khởi tạo RAG Service Unified...")
            
            # 1. Load embedding model
            model_path = "D:/Vian/MODELS/multilingual_e5_large"
            logger.info(f"📥 Loading embedding model: {model_path}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModel.from_pretrained(model_path)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            
            logger.info(f"✅ Embedding model loaded on {self.device}")
            
            # 2. Initialize LLM Service
            if self.use_llm_generation:
                try:
                    llm_model_path = "D:/Vian/MODELS/vinallama-2.7b-chat"
                    logger.info(f"📥 Initializing LLM service: {llm_model_path}")
                    
                    self.llm_service = LLMService(llm_model_path)
                    self.llm_service.load_model()
                    
                    logger.info("✅ LLM service initialized successfully")
                except Exception as e:
                    logger.warning(f"⚠️ LLM service failed to load: {e}")
                    logger.warning("Will use template-based responses instead")
                    self.use_llm_generation = False
            
            # 3. Load dữ liệu
            data_dir = "D:/Vian/Demo3/backend1/data"
            faiss_path = os.path.join(data_dir, "all_faiss.index")
            pickle_path = os.path.join(data_dir, "all_embeddings.pkl")
            
            logger.info(f"📥 Loading FAISS index: {faiss_path}")
            self.faiss_index = faiss.read_index(faiss_path)
            
            logger.info(f"📥 Loading documents data: {pickle_path}")
            with open(pickle_path, 'rb') as f:
                self.documents_data = pickle.load(f)
            
            # 3. Tạo chunks metadata với category mapping
            logger.info("🔄 Processing chunks metadata...")
            self.chunks_metadata = []
            
            for doc_idx, doc in enumerate(self.documents_data):
                pdf_name = doc.get('pdf_name', 'Unknown')
                chunks = doc.get('chunks', [])
                
                # Xác định category dựa trên pdf_name
                category = self._determine_category(pdf_name)
                
                for chunk_idx, chunk in enumerate(chunks):
                    self.chunks_metadata.append({
                        'doc_idx': doc_idx,
                        'chunk_idx': chunk_idx,
                        'pdf_name': pdf_name,
                        'content': chunk,
                        'category': category,
                        'content_length': len(chunk)
                    })
            
            self.total_chunks = len(self.chunks_metadata)
            self.total_documents = len(self.documents_data)
            
            end_time = time.time()
            self.initialization_time = end_time - start_time
            
            self.is_initialized = True
            
            logger.info(f"✅ RAG Service Unified initialized successfully!")
            logger.info(f"📊 Stats: {self.total_documents} documents, {self.total_chunks} chunks")
            logger.info(f"⏱️ Initialization time: {self.initialization_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Lỗi khởi tạo RAG Service Unified: {e}")
            raise
    
    def _extract_main_topic(self, question_lower: str) -> str:
        """Trích xuất chủ đề chính từ câu hỏi"""
        # Mapping keywords to topics
        topic_keywords = {
            'tường lửa': ['tường lửa', 'firewall', 'waf', 'ids', 'ips'],
            'ddos': ['ddos', 'dos', 'denial of service', 'từ chối dịch vụ'],
            'malware': ['malware', 'virus', 'trojan', 'ransomware', 'mã độc'],
            'phishing': ['phishing', 'lừa đảo', 'giả mạo'],
            'mật khẩu': ['mật khẩu', 'password', 'authentication'],
            'mã hóa': ['mã hóa', 'encryption', 'cryptography'],
            'iso 27001': ['iso 27001', 'iso27001'],
            'nist': ['nist', 'cybersecurity framework'],
            'an toàn thông tin': ['an toàn thông tin', 'information security', 'bảo mật']
        }
        
        # Tìm topic phù hợp nhất
        for topic, keywords in topic_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                return topic
        
        return 'general'
    
    def _generate_dynamic_title(self, main_topic: str, answer_style: str) -> str:
        """Tạo tiêu đề động dựa trên topic"""
        if answer_style == 'definition':
            if main_topic == 'tường lửa':
                return "Định nghĩa Tường lửa (Firewall)"
            elif main_topic == 'ddos':
                return "Tấn công DDoS là gì"
            elif main_topic == 'malware':
                return "Định nghĩa Malware và Mã độc"
            elif main_topic == 'phishing':
                return "Tấn công Phishing là gì"
            elif main_topic == 'mật khẩu':
                return "Định nghĩa về Mật khẩu và Xác thực"
            elif main_topic == 'mã hóa':
                return "Mã hóa (Encryption) là gì"
            elif main_topic == 'iso 27001':
                return "Tiêu chuẩn ISO 27001"
            elif main_topic == 'nist':
                return "NIST Cybersecurity Framework"
            else:
                return "Định nghĩa An toàn thông tin"
        elif answer_style == 'regulation':
            return f"Quy định pháp lý về {main_topic.title()}"
        elif answer_style == 'standard':
            return f"Tiêu chuẩn về {main_topic.title()}"
        elif answer_style == 'attack':
            return f"Thông tin về {main_topic.title()}"
        else:
            return f"Thông tin về {main_topic.title()}"
    
    def _generate_dynamic_conclusion(self, main_topic: str, answer_style: str) -> str:
        """Tạo kết luận động dựa trên topic"""
        conclusions = {
            'tường lửa': "Tường lửa là hệ thống bảo mật mạng quan trọng, giúp kiểm soát và lọc lưu lượng mạng, bảo vệ hệ thống khỏi các truy cập trái phép.",
            'ddos': "Tấn công DDoS là một trong những mối đe dọa nghiêm trọng nhất đối với hệ thống mạng, có thể gây gián đoạn dịch vụ và thiệt hại kinh tế lớn.",
            'malware': "Malware là mối đe dọa thường xuyên trong không gian mạng, cần có biện pháp phòng chống đa lớp để bảo vệ hệ thống.",
            'phishing': "Phishing là hình thức tấn công kỹ thuật xã hội nguy hiểm, cần nâng cao nhận thức người dùng để phòng chống hiệu quả.",
            'mật khẩu': "Mật khẩu mạnh và xác thực đa yếu tố là nền tảng của bảo mật hệ thống thông tin.",
            'mã hóa': "Mã hóa là công nghệ cốt lõi để bảo vệ tính bảo mật và toàn vẹn của dữ liệu.",
            'iso 27001': "ISO 27001 là tiêu chuẩn quốc tế quan trọng cho hệ thống quản lý an toàn thông tin.",
            'nist': "NIST Framework cung cấp hướng dẫn toàn diện để quản lý rủi ro cybersecurity.",
            'an toàn thông tin': "An toàn thông tin là lĩnh vực bảo vệ thông tin và hệ thống thông tin khỏi các mối đe dọa, đảm bảo tính bảo mật (Confidentiality), toàn vẹn (Integrity) và sẵn sàng (Availability) của dữ liệu."
        }
        
        return conclusions.get(main_topic, "Đây là một khía cạnh quan trọng của an toàn thông tin cần được hiểu rõ và triển khai đúng cách.")
    
    def _generate_llm_answer(self, question: str, search_results: List[Dict]) -> Dict[str, Any]:
        """Tạo câu trả lời sử dụng LLM với RAG context"""
        try:
            logger.info(f"🤖 Attempting LLM generation for: {question[:50]}...")
            
            # Kiểm tra LLM service
            if not self.llm_service:
                logger.warning("❌ LLM service not available, using template")
                return self._generate_template_answer(question, search_results)
            
            # Chuẩn bị context từ search results
            context_docs = []
            for result in search_results[:3]:  # Top 3 results
                context_docs.append({
                    'content': result['content'][:800],  # Giới hạn length để tránh token limit
                    'metadata': {
                        'filename': result['pdf_name'],
                        'category': result['category'],
                        'similarity': result['similarity']
                    }
                })
            
            logger.info(f"📖 Prepared {len(context_docs)} context docs for LLM")
            
            # Sử dụng LLM service để generate response
            llm_response = self.llm_service.generate_response(
                query=question,
                context_docs=context_docs,
                max_new_tokens=256  # Giảm để tránh timeout
            )
            
            # Kiểm tra response quality
            if not llm_response or len(llm_response.strip()) < 20:
                logger.warning("❌ LLM response too short, using template fallback")
                return self._generate_template_answer(question, search_results)
            
            if "không thể" in llm_response or "thử lại" in llm_response:
                logger.warning("❌ LLM returned error message, using template fallback")
                return self._generate_template_answer(question, search_results)
            
            # Tính confidence dựa trên search results quality
            avg_score = sum(r['score'] for r in search_results[:3]) / min(3, len(search_results))
            confidence = min(avg_score / 200.0, 1.0)
            
            logger.info(f"✅ LLM generation successful: {len(llm_response)} chars")
            
            return {
                'answer': llm_response,
                'confidence': confidence,
                'method': 'llm_generation',
                'sources_used': len(search_results[:3])
            }
            
        except Exception as e:
            logger.error(f"❌ Lỗi LLM generation: {e}")
            logger.info("🔄 Falling back to template generation")
            # Fallback to template
            return self._generate_template_answer(question, search_results)
    
    def _generate_template_answer(self, question: str, search_results: List[Dict]) -> Dict[str, Any]:
        """Tạo câu trả lời bằng template (fallback)"""
        try:
            # 1. Phân tích câu hỏi để xác định chủ đề và style
            question_lower = question.lower()
            
            # Xác định chủ đề chính từ câu hỏi
            main_topic = self._extract_main_topic(question_lower)
            
            # Xác định style dựa trên câu hỏi
            is_definition = any(word in question_lower for word in ['là gì', 'what is', 'định nghĩa', 'khái niệm'])
            is_regulation = any(word in question_lower for word in ['luật', 'quy định', 'regulation', 'law'])
            is_standard = any(word in question_lower for word in ['iso', 'nist', 'tiêu chuẩn', 'standard'])
            is_attack = any(word in question_lower for word in ['tấn công', 'attack', 'hack', 'malware', 'virus'])
            
            # 2. Lấy top results dựa trên loại câu hỏi
            if is_definition:
                top_results = search_results[:3]
                answer_style = 'definition'
            elif is_regulation:
                top_results = search_results[:4]
                answer_style = 'regulation'
            elif is_standard:
                top_results = search_results[:3]
                answer_style = 'standard'
            elif is_attack:
                top_results = search_results[:3]
                answer_style = 'attack'
            else:
                top_results = search_results[:3]
                answer_style = 'general'
            
            # 3. Tạo tiêu đề động dựa trên topic và style
            answer_parts = []
            title = self._generate_dynamic_title(main_topic, answer_style)
            answer_parts.append(f"**{title}:**")
            answer_parts.append("")
            
            # 4. Thêm nội dung từ từng source
            for i, result in enumerate(top_results, 1):
                pdf_name = result['pdf_name']
                content = result['content']
                category = result['category']
                
                # Làm sạch tên file để hiển thị đẹp hơn
                display_name = self._clean_filename(pdf_name)
                
                # Tìm câu quan trọng nhất
                important_sentences = self._extract_important_sentences(content, question_lower)
                
                if important_sentences:
                    answer_parts.append(f"**{i}. Theo {display_name}:**")
                    for sentence in important_sentences[:2]:  # Tối đa 2 câu
                        cleaned_sentence = self._clean_sentence(sentence.strip())
                        if cleaned_sentence and len(cleaned_sentence) > 20:
                            answer_parts.append(f"• {cleaned_sentence}")
                    answer_parts.append("")
                else:
                    # Nếu không tìm thấy câu cụ thể, tạo summary từ content
                    summary = self._create_content_summary(content, question_lower)
                    if summary:
                        answer_parts.append(f"**{i}. Theo {display_name}:**")
                        answer_parts.append(f"• {summary}")
                        answer_parts.append("")
            
            # 5. Thêm tổng kết động dựa trên topic
            answer_parts.append("---")
            conclusion = self._generate_dynamic_conclusion(main_topic, answer_style)
            answer_parts.append(f"**Tóm lại:** {conclusion}")
            
            answer_text = "\n".join(answer_parts)
            
            # 6. Tính confidence dựa trên quality của results
            avg_score = sum(r['score'] for r in top_results) / len(top_results)
            confidence = min(avg_score / 200.0, 1.0)  # Normalize to 0-1
            
            return {
                'answer': answer_text,
                'confidence': confidence,
                'method': answer_style + '_template',
                'sources_used': len(top_results)
            }
            
        except Exception as e:
            logger.error(f"❌ Lỗi template generation: {e}")
            return {
                'answer': "Xin lỗi, có lỗi khi tạo câu trả lời. Vui lòng thử lại.",
                'confidence': 0.0,
                'method': 'error'
            }
    
    def _determine_category(self, pdf_name: str) -> str:
        """Xác định category dựa trên tên file"""
        pdf_lower = pdf_name.lower()
        
        if any(keyword in pdf_lower for keyword in ['luat', 'nghi_dinh', 'quyet_dinh', 'thong_tu', 'tcvn']):
            return 'luat'
        elif any(keyword in pdf_lower for keyword in ['nist', 'iso', 'cybersecurity', 'framework']):
            return 'english'
        else:
            return 'vietnamese'
    
    def encode_text(self, text: str) -> np.ndarray:
        """Encode text thành embedding vector"""
        try:
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)
                return embeddings.cpu().numpy()
                
        except Exception as e:
            logger.error(f"❌ Lỗi encode text: {e}")
            raise
    
    def search_relevant_chunks(self, 
                             question: str, 
                             top_k: int = None,
                             filter_category: Optional[str] = None,
                             similarity_threshold: float = None) -> List[Dict]:
        """Tìm kiếm chunks liên quan với filtering nâng cao"""
        try:
            if not self.is_initialized:
                raise RuntimeError("Service chưa được khởi tạo")
            
            if top_k is None:
                top_k = self.default_top_k
            if similarity_threshold is None:
                similarity_threshold = self.default_similarity_threshold
            
            # 1. Encode question
            question_embedding = self.encode_text(question)
            
            # 2. FAISS search với top_k cao hơn để có nhiều lựa chọn
            search_k = min(top_k * 3, 50)  # Tìm nhiều hơn để filter
            scores, indices = self.faiss_index.search(question_embedding.astype('float32'), search_k)
            
            # 3. Tạo kết quả và filter
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if 0 <= idx < len(self.chunks_metadata):
                    chunk_meta = self.chunks_metadata[idx]
                    
                    # Filter theo category nếu có
                    if filter_category and filter_category != 'all':
                        if chunk_meta['category'] != filter_category:
                            continue
                    
                    # Filter theo similarity threshold
                    if score < similarity_threshold:
                        continue
                    
                    results.append({
                        'score': float(score),
                        'similarity': float(score),
                        'pdf_name': chunk_meta['pdf_name'],
                        'content': chunk_meta['content'],
                        'category': chunk_meta['category'],
                        'content_length': chunk_meta['content_length'],
                        'doc_idx': chunk_meta['doc_idx'],
                        'chunk_idx': chunk_meta['chunk_idx']
                    })
            
            # 4. Sắp xếp theo score và lấy top_k
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"❌ Lỗi search chunks: {e}")
            return []
    
    def generate_comprehensive_answer(self, 
                                    question: str, 
                                    search_results: List[Dict],
                                    include_sources: bool = True) -> Dict[str, Any]:
        """Tạo câu trả lời toàn diện từ search results sử dụng LLM"""
        try:
            if not search_results:
                return {
                    'answer': "Xin lỗi, tôi không tìm thấy thông tin liên quan trong cơ sở dữ liệu.",
                    'confidence': 0.0,
                    'method': 'no_results'
                }
            
            # Sử dụng LLM nếu có sẵn
            if self.use_llm_generation and self.llm_service:
                return self._generate_llm_answer(question, search_results)
            else:
                return self._generate_template_answer(question, search_results)
            
        except Exception as e:
            logger.error(f"❌ Lỗi generate answer: {e}")
            return {
                'answer': "Xin lỗi, có lỗi khi tạo câu trả lời. Vui lòng thử lại.",
                'confidence': 0.0,
                'method': 'error'
            }
    
    def _clean_filename(self, filename: str) -> str:
        """Làm sạch tên file để hiển thị đẹp"""
        # Loại bỏ extension
        name = filename.replace('.pdf', '').replace('.PDF', '')
        
        # Thay thế underscore bằng space
        name = name.replace('_', ' ')
        
        # Viết hoa chữ cái đầu
        name = name.title()
        
        return name
    
    def _extract_important_sentences(self, content: str, question_lower: str) -> List[str]:
        """Trích xuất câu quan trọng từ content dựa trên câu hỏi"""
        
        # Tách content thành sentences tốt hơn
        import re
        
        # Tách theo dấu câu và xuống dòng
        sentences = re.split(r'[.!?]\s*|\n+', content)
        important_sentences = []
        
        # Xác định keywords dựa trên câu hỏi
        topic_keywords = self._get_topic_keywords(question_lower)
        
        # Scoring và ranking sentences
        sentence_scores = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20 or len(sentence) > 500:  # Bỏ qua câu quá ngắn/dài
                continue
                
            sentence_lower = sentence.lower()
            score = 0
            
            # Tính điểm dựa trên keywords
            for keyword in topic_keywords:
                if keyword in sentence_lower:
                    score += len(keyword.split())  # Keyword dài hơn = điểm cao hơn
            
            # Bonus cho câu có định nghĩa
            if any(def_word in sentence_lower for def_word in ['là', 'được định nghĩa', 'có nghĩa', 'refers to']):
                score += 2
            
            # Penalty cho câu có URL hoặc reference
            if any(ref in sentence_lower for ref in ['http', 'www', 'truy cập', 'tham khảo']):
                score -= 1
            
            if score > 0:
                sentence_scores.append((sentence, score))
        
        # Sắp xếp theo điểm và lấy top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Lấy tối đa 3 câu tốt nhất
        for sentence, score in sentence_scores[:3]:
            important_sentences.append(sentence)
        
        return important_sentences
    
    def _get_topic_keywords(self, question_lower: str) -> List[str]:
        """Lấy keywords liên quan đến topic trong câu hỏi"""
        topic_keywords_map = {
            'ddos': ['ddos', 'dos', 'denial of service', 'từ chối dịch vụ', 'tấn công phân tán'],
            'tường lửa': ['tường lửa', 'firewall', 'waf', 'ids', 'ips', 'kiểm soát truy cập'],
            'malware': ['malware', 'virus', 'trojan', 'ransomware', 'mã độc', 'phần mềm độc hại'],
            'phishing': ['phishing', 'lừa đảo', 'giả mạo', 'social engineering'],
            'mật khẩu': ['mật khẩu', 'password', 'authentication', 'xác thực'],
            'mã hóa': ['mã hóa', 'encryption', 'cryptography', 'mật mã'],
            'an toàn thông tin': ['an toàn thông tin', 'information security', 'bảo mật', 'cybersecurity']
        }
        
        # Tìm keywords phù hợp với câu hỏi
        relevant_keywords = []
        for topic, keywords in topic_keywords_map.items():
            if any(keyword in question_lower for keyword in keywords):
                relevant_keywords.extend(keywords)
        
        # Thêm keywords chung
        relevant_keywords.extend(['định nghĩa', 'khái niệm', 'bảo vệ', 'security', 'rủi ro', 'mối đe dọa'])
        
        return list(set(relevant_keywords))  # Remove duplicates
    
    def _clean_sentence(self, sentence: str) -> str:
        """Làm sạch câu văn"""
        import re
        
        # Loại bỏ URLs
        sentence = re.sub(r'https?://[^\s]+', '', sentence)
        sentence = re.sub(r'www\.[^\s]+', '', sentence)
        
        # Loại bỏ references không hoàn chỉnh
        sentence = re.sub(r'truy cập vào tháng \d+.*', '', sentence)
        sentence = re.sub(r'tham khảo.*', '', sentence)
        
        # Loại bỏ ký tự đặc biệt thừa
        sentence = re.sub(r'[%#*]+', '', sentence)
        sentence = re.sub(r'\s+', ' ', sentence)  # Normalize whitespace
        
        # Loại bỏ dấu câu thừa ở cuối
        sentence = sentence.strip(' .,;:')
        
        return sentence
    
    def _create_content_summary(self, content: str, question_lower: str) -> str:
        """Tạo summary từ content khi không tìm được câu quan trọng"""
        
        # Tìm đoạn văn có chứa keywords liên quan
        topic_keywords = self._get_topic_keywords(question_lower)
        
        # Tách content thành paragraphs
        paragraphs = content.split('\n')
        best_paragraph = ""
        best_score = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if len(paragraph) < 50:  # Bỏ qua đoạn quá ngắn
                continue
                
            paragraph_lower = paragraph.lower()
            score = 0
            
            # Tính điểm cho paragraph
            for keyword in topic_keywords:
                score += paragraph_lower.count(keyword)
            
            if score > best_score:
                best_score = score
                best_paragraph = paragraph
        
        if best_paragraph:
            # Clean và truncate
            summary = self._clean_sentence(best_paragraph)
            if len(summary) > 200:
                summary = summary[:200] + "..."
            return summary
        
        # Fallback: lấy đoạn đầu
        first_part = content[:200].strip()
        return self._clean_sentence(first_part) + "..."
    
    async def query(self, 
                   question: str,
                   top_k: Optional[int] = None,
                   filter_category: Optional[str] = None,
                   include_sources: bool = True,
                   similarity_threshold: Optional[float] = None) -> Dict[str, Any]:
        """API chính để xử lý query và trả về response"""
        try:
            start_time = time.time()
            
            if not self.is_initialized:
                await self.initialize()
            
            # Validate input
            if not question or not question.strip():
                raise ValueError("Question không được để trống")
            
            question = question.strip()
            logger.info(f"🔍 Processing query: {question[:100]}...")
            
            # 1. Search relevant chunks
            search_results = self.search_relevant_chunks(
                question=question,
                top_k=top_k,
                filter_category=filter_category,
                similarity_threshold=similarity_threshold
            )
            
            # 2. Generate comprehensive answer
            answer_data = self.generate_comprehensive_answer(
                question=question,
                search_results=search_results,
                include_sources=include_sources
            )
            
            # 3. Prepare sources information
            sources = []
            if include_sources and search_results:
                for result in search_results:
                    sources.append({
                        'filename': result['pdf_name'],
                        'display_name': self._clean_filename(result['pdf_name']),
                        'category': result['category'],
                        'content_preview': result['content'][:300] + "..." if len(result['content']) > 300 else result['content'],
                        'similarity_score': result['similarity'],
                        'content_length': result['content_length']
                    })
            
            # 4. Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)
            
            # 5. Prepare final response
            response = {
                'question': question,
                'answer': answer_data['answer'],
                'sources': sources,
                'total_sources': len(sources),
                'confidence': answer_data.get('confidence', 0.0),
                'method': answer_data.get('method', 'unified'),
                'processing_time_ms': processing_time,
                'filter_category': filter_category or 'all',
                'timestamp': datetime.now().isoformat(),
                'service_version': '1.0.0'
            }
            
            logger.info(f"✅ Query processed successfully: {len(sources)} sources, {processing_time}ms")
            return response
            
        except Exception as e:
            logger.error(f"❌ Lỗi trong query unified: {e}")
            return {
                'question': question,
                'answer': f"Xin lỗi, có lỗi khi xử lý câu hỏi: {str(e)}",
                'sources': [],
                'total_sources': 0,
                'confidence': 0.0,
                'method': 'error',
                'processing_time_ms': 0,
                'error': str(e)
            }
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """Lấy thống kê service"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Thống kê theo category
            category_stats = {}
            for chunk in self.chunks_metadata:
                cat = chunk['category']
                if cat not in category_stats:
                    category_stats[cat] = {'chunks': 0, 'total_length': 0}
                category_stats[cat]['chunks'] += 1
                category_stats[cat]['total_length'] += chunk['content_length']
            
            return {
                'service_name': 'RAG Service Unified',
                'version': '1.0.0',
                'status': 'ready' if self.is_initialized else 'not_initialized',
                'initialization_time': self.initialization_time,
                'total_documents': self.total_documents,
                'total_chunks': self.total_chunks,
                'categories': category_stats,
                'device': str(self.device),
                'model_path': 'D:/Vian/MODELS/multilingual_e5_large',
                'default_settings': {
                    'top_k': self.default_top_k,
                    'similarity_threshold': self.default_similarity_threshold,
                    'max_answer_length': self.max_answer_length
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Lỗi get stats: {e}")
            return {'error': str(e)}

# Global instance
_rag_service_unified = None

async def get_rag_service_unified():
    """Get RAG Service Unified instance"""
    global _rag_service_unified
    if _rag_service_unified is None:
        _rag_service_unified = RAGServiceUnified()
        await _rag_service_unified.initialize()
    return _rag_service_unified
