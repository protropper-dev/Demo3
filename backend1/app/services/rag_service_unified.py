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
            model_path = "models/multilingual_e5_large"
            logger.info(f"📥 Loading embedding model: {model_path}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModel.from_pretrained(model_path)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            
            logger.info(f"✅ Embedding model loaded on {self.device}")
            
            # 2. Initialize LLM Service
            if self.use_llm_generation:
                try:
                    llm_model_path = "models/vinallama-2.7b-chat"
                    logger.info(f"📥 Initializing LLM service: {llm_model_path}")
                    
                    self.llm_service = LLMService(llm_model_path)
                    self.llm_service.load_model()
                    
                    logger.info("✅ LLM service initialized successfully")
                except Exception as e:
                    logger.warning(f"⚠️ LLM service failed to load: {e}")
                    logger.warning("Will use template-based responses instead")
                    self.use_llm_generation = False
            
            # 3. Load dữ liệu
            data_dir = "data"
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
    
    # ==================== PIPELINE 2-STAGE: RAG → LLM ENHANCEMENT ====================
    
    def _generate_rag_response(self, question: str, search_results: List[Dict]) -> Dict[str, Any]:
        """Stage 1: Tạo response ban đầu từ RAG"""
        try:
            logger.info(f"📝 Stage 1: Generating RAG response for: {question[:50]}...")
            
            # Tạo response từ template hoặc basic LLM
            if self.use_llm_generation and self.llm_service:
                # Basic LLM generation với prompt đơn giản
                basic_response = self._generate_basic_llm_response(question, search_results)
            else:
                # Template-based response
                basic_response = self._generate_template_response(question, search_results)
            
            return {
                'raw_response': basic_response,
                'sources': search_results,
                'confidence': self._calculate_basic_confidence(search_results),
                'stage': 'rag_generation'
            }
            
        except Exception as e:
            logger.error(f"❌ RAG response generation error: {e}")
            # Fallback to template
            return {
                'raw_response': self._generate_template_response(question, search_results),
                'sources': search_results,
                'confidence': 0.5,
                'stage': 'rag_generation'
            }
    
    def _generate_basic_llm_response(self, question: str, search_results: List[Dict]) -> str:
        """Tạo response cơ bản từ LLM với prompt đơn giản"""
        try:
            # Simple prompt cho basic generation
            context_text = ""
            for i, result in enumerate(search_results[:3], 1):
                context_text += f"\n=== Nguồn {i}: {result['pdf_name']} ===\n{result['content'][:400]}\n"
            
            basic_prompt = f"""
            Dựa trên các tài liệu sau, hãy trả lời câu hỏi: {question}
            
            Tài liệu:
            {context_text}
            
            Trả lời ngắn gọn và chính xác:
            """
            
            # Cấu hình generation cho basic response
            basic_generation_config = {
                'temperature': 0.6,
                'max_new_tokens': 200,
                'top_p': 0.9,
                'top_k': 50,
                'repetition_penalty': 1.1
            }
            
            response = self.llm_service.generate_response(
                query=question,
                context_docs=search_results[:3],
                max_new_tokens=200,
                generation_config=basic_generation_config
            )
            return response
            
        except Exception as e:
            logger.warning(f"Basic LLM generation failed: {e}")
            return self._generate_template_response(question, search_results)
    
    def _generate_template_response(self, question: str, search_results: List[Dict]) -> str:
        """Tạo response từ template (fallback)"""
        if not search_results:
            return "Xin lỗi, tôi không tìm thấy thông tin liên quan đến câu hỏi của bạn."
        
        # Lấy top result
        top_result = search_results[0]
        content = top_result['content'][:500]  # Giới hạn độ dài
        
        # Tạo response cơ bản
        response = f"Dựa trên tài liệu {top_result['pdf_name']}, {content}"
        
        return response
    
    def _calculate_basic_confidence(self, search_results: List[Dict]) -> float:
        """Tính confidence cơ bản cho RAG response"""
        if not search_results:
            return 0.0
        
        # Average similarity score
        avg_similarity = sum(r['similarity'] for r in search_results[:3]) / min(len(search_results), 3)
        
        # Diversity bonus
        categories = set(r['category'] for r in search_results[:3])
        diversity_bonus = min(len(categories) * 0.1, 0.2)
        
        return min(avg_similarity + diversity_bonus, 1.0)
    
    def _enhance_response_with_llm(self, rag_response: Dict[str, Any], question: str) -> Dict[str, Any]:
        """Stage 2: Nâng cao chất lượng response bằng LLM"""
        try:
            logger.info(f"🚀 Stage 2: Enhancing response with LLM...")
            
            # 1. Chuẩn bị context cho enhancement
            enhancement_context = self._prepare_enhancement_context(rag_response, question)
            
            # 2. Tạo enhancement prompt
            enhancement_prompt = self._create_enhancement_prompt(rag_response, question)
            
            # 3. Gọi LLM để enhance response
            enhanced_response = self._call_llm_for_enhancement(enhancement_prompt)
            
            # 4. Validate enhanced response
            validated_response = self._validate_enhanced_response(enhanced_response, rag_response)
            
            # 5. Tính confidence mới
            enhanced_confidence = self._calculate_enhanced_confidence(rag_response, validated_response)
            
            return {
                'original_response': rag_response['raw_response'],
                'enhanced_response': validated_response,
                'sources': rag_response['sources'],
                'confidence': enhanced_confidence,
                'enhancement_applied': True,
                'stage': 'llm_enhancement'
            }
            
        except Exception as e:
            logger.warning(f"LLM enhancement failed: {e}")
            # Fallback to original response
            return {
                'original_response': rag_response['raw_response'],
                'enhanced_response': rag_response['raw_response'],
                'sources': rag_response['sources'],
                'confidence': rag_response['confidence'],
                'enhancement_applied': False,
                'stage': 'rag_generation'
            }
    
    def _prepare_enhancement_context(self, rag_response: Dict[str, Any], question: str) -> Dict[str, Any]:
        """Chuẩn bị context cho enhancement"""
        return {
            'original_response': rag_response['raw_response'],
            'question': question,
            'sources': rag_response['sources'],
            'original_confidence': rag_response['confidence'],
            'response_length': len(rag_response['raw_response']),
            'sources_count': len(rag_response['sources']),
            'question_type': self._classify_question_type(question)
        }
    
    def _classify_question_type(self, query: str) -> str:
        """Phân loại câu hỏi để tối ưu prompt"""
        query_lower = query.lower()
        
        # Keywords cho từng loại
        definition_keywords = ['là gì', 'what is', 'định nghĩa', 'khái niệm', 'nghĩa là']
        regulation_keywords = ['luật', 'quy định', 'regulation', 'law', 'điều', 'khoản']
        standard_keywords = ['iso', 'nist', 'tiêu chuẩn', 'standard', 'chuẩn']
        attack_keywords = ['tấn công', 'attack', 'hack', 'malware', 'virus', 'exploit']
        howto_keywords = ['làm thế nào', 'how to', 'cách', 'hướng dẫn', 'thực hiện']
        
        if any(keyword in query_lower for keyword in definition_keywords):
            return 'definition'
        elif any(keyword in query_lower for keyword in regulation_keywords):
            return 'regulation'
        elif any(keyword in query_lower for keyword in standard_keywords):
            return 'standard'
        elif any(keyword in query_lower for keyword in attack_keywords):
            return 'attack'
        elif any(keyword in query_lower for keyword in howto_keywords):
            return 'howto'
        else:
            return 'general'
    
    def _create_enhancement_prompt(self, rag_response: Dict[str, Any], question: str) -> str:
        """Tạo prompt cho LLM enhancement - tối ưu cho tiếng Việt"""
        original_response = rag_response['raw_response']
        sources = rag_response['sources']
        question_type = self._classify_question_type(question)
        
        # System prompt cho enhancement - tối ưu cho tiếng Việt
        system_prompt = f"""Bạn là chuyên gia an toàn thông tin và cải thiện chất lượng câu trả lời. Nhiệm vụ của bạn là:

**YÊU CẦU CHÍNH:**
1. **Sửa lỗi chính tả và ngữ pháp** - Đảm bảo tiếng Việt chuẩn, không có lỗi chính tả
2. **Cải thiện cấu trúc** - Sử dụng dấu câu đúng, xuống dòng hợp lý, câu hoàn chỉnh
3. **Làm rõ nội dung** - Giải thích rõ ràng, dễ hiểu, logic
4. **Bổ sung thông tin** - Thêm thông tin quan trọng từ sources nếu cần
5. **Tối ưu độ dài** - Tối đa 300 từ, súc tích nhưng đầy đủ

**QUY TẮC VIẾT:**
- Sử dụng thuật ngữ kỹ thuật chính xác (DDoS, tấn công, lưu lượng, máy chủ, ngăn chặn)
- Viết câu hoàn chỉnh, có chủ ngữ và vị ngữ
- Sử dụng dấu câu đúng: dấu chấm, phẩy, hai chấm
- Tránh lặp từ, lặp cụm từ
- Cấu trúc rõ ràng: định nghĩa → đặc điểm → ví dụ → giải pháp

**LOẠI CÂU HỎI:** {question_type}"""

        # Context từ sources - rút gọn để tránh quá dài
        sources_context = ""
        for i, source in enumerate(sources[:2], 1):  # Chỉ lấy 2 sources đầu
            sources_context += f"\n**Nguồn {i}:** {source['pdf_name']}\n{source['content'][:300]}...\n"
        
        # User prompt - đơn giản và rõ ràng
        user_prompt = f"""**Câu hỏi:** {question}

**Câu trả lời hiện tại cần cải thiện:**
{original_response}

**Nguồn tài liệu tham khảo:**
{sources_context}

**Hãy cải thiện câu trả lời với yêu cầu:**
- Sửa tất cả lỗi chính tả và ngữ pháp
- Viết lại với cấu trúc rõ ràng, dễ hiểu
- Sử dụng tiếng Việt chuẩn, tự nhiên
- Tối đa 300 từ, súc tích nhưng đầy đủ
- Giữ nguyên thông tin kỹ thuật chính xác

**Câu trả lời cải thiện:**"""
        
        return f"<|im_start|>system\n{system_prompt}\n<|im_end|>\n<|im_start|>user\n{user_prompt}\n<|im_end|>\n<|im_start|>assistant\n"
    
    def _call_llm_for_enhancement(self, enhancement_prompt: str) -> str:
        """Gọi LLM để enhance response"""
        try:
            # Cấu hình tối ưu cho enhancement - tập trung vào chất lượng
            generation_config = {
                'temperature': 0.4,  # Giảm để ổn định hơn, giảm lỗi chính tả
                'top_p': 0.75,  # Giảm để tập trung hơn
                'top_k': 30,  # Giảm để ổn định hơn
                'repetition_penalty': 1.25,  # Tăng để tránh lặp từ
                'no_repeat_ngram_size': 4,  # Tăng để tránh lặp cụm từ
                'max_new_tokens': 350,  # Giảm để tránh quá dài
                'do_sample': True,
                'early_stopping': True
            }
            
            # Gọi LLM với prompt enhancement
            enhanced_response = self.llm_service.generate_response(
                query=enhancement_prompt,
                context_docs=None,  # Không cần context docs vì đã có trong prompt
                max_new_tokens=generation_config['max_new_tokens'],
                generation_config=generation_config
            )
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"LLM enhancement call failed: {e}")
            raise
    
    def _validate_enhanced_response(self, enhanced_response: str, rag_response: Dict[str, Any]) -> str:
        """Validate enhanced response"""
        original_response = rag_response['raw_response']
        
        # 1. Length validation - tối ưu cho tiếng Việt
        if len(enhanced_response.strip()) < 30:
            logger.warning("Enhanced response too short, using original")
            return original_response
        
        if len(enhanced_response.strip()) > 600:
            logger.warning("Enhanced response too long, truncating")
            enhanced_response = enhanced_response[:600] + "..."
        
        # 2. Content validation
        if not self._contains_key_information(enhanced_response, original_response):
            logger.warning("Enhanced response missing key information, using original")
            return original_response
        
        # 3. Quality validation
        if self._has_quality_issues(enhanced_response):
            logger.warning("Enhanced response has quality issues, using original")
            return original_response
        
        return enhanced_response
    
    def _contains_key_information(self, enhanced: str, original: str) -> bool:
        """Kiểm tra enhanced response có chứa thông tin chính từ original"""
        # Extract key phrases from original
        original_keywords = self._extract_key_phrases(original)
        
        # Check if enhanced contains most key phrases
        enhanced_lower = enhanced.lower()
        matches = sum(1 for keyword in original_keywords if keyword.lower() in enhanced_lower)
        
        return matches >= len(original_keywords) * 0.7  # 70% match required
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text"""
        # Simple key phrase extraction
        words = text.split()
        # Filter out common words and get meaningful phrases
        key_phrases = []
        for word in words:
            if len(word) > 3 and word.lower() not in ['của', 'với', 'từ', 'cho', 'được', 'có', 'là', 'và', 'trong', 'theo']:
                key_phrases.append(word)
        return key_phrases[:10]  # Top 10 key phrases
    
    def _has_quality_issues(self, response: str) -> bool:
        """Kiểm tra quality issues"""
        # Check for error indicators
        error_indicators = ['không thể', 'thử lại', 'lỗi', 'error', 'sorry', 'cannot']
        if any(indicator in response.lower() for indicator in error_indicators):
            return True
        
        # Check for repetition
        words = response.split()
        if len(words) > 10:
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            # Check for excessive repetition
            max_repetition = max(word_counts.values())
            if max_repetition > len(words) * 0.3:  # 30% repetition threshold
                return True
        
        return False
    
    def _calculate_enhanced_confidence(self, rag_response: Dict[str, Any], enhanced_response: str) -> float:
        """Tính confidence cho enhanced response"""
        original_confidence = rag_response['confidence']
        
        # 1. Base confidence từ original
        base_confidence = original_confidence
        
        # 2. Enhancement quality bonus
        enhancement_bonus = self._calculate_enhancement_bonus(rag_response['raw_response'], enhanced_response)
        
        # 3. Response quality bonus
        quality_bonus = self._calculate_quality_bonus(enhanced_response)
        
        # 4. Source utilization bonus
        source_bonus = self._calculate_source_utilization_bonus(enhanced_response, rag_response['sources'])
        
        # Calculate final confidence
        final_confidence = base_confidence + enhancement_bonus + quality_bonus + source_bonus
        
        return min(max(final_confidence, 0.0), 1.0)
    
    def _calculate_enhancement_bonus(self, original: str, enhanced: str) -> float:
        """Tính bonus cho enhancement quality"""
        # Length improvement
        length_ratio = len(enhanced) / max(len(original), 1)
        if 1.2 <= length_ratio <= 2.0:  # Optimal length increase
            length_bonus = 0.1
        elif length_ratio > 2.0:  # Too long
            length_bonus = -0.05
        else:  # Too short
            length_bonus = -0.05
        
        # Structure improvement
        structure_bonus = 0.0
        if any(marker in enhanced for marker in ['**', '###', '-', '1.', '2.']):
            structure_bonus = 0.05
        
        # Language improvement
        language_bonus = 0.0
        if self._has_better_language(enhanced, original):
            language_bonus = 0.05
        
        return length_bonus + structure_bonus + language_bonus
    
    def _has_better_language(self, enhanced: str, original: str) -> bool:
        """Kiểm tra enhanced có ngôn ngữ tốt hơn không"""
        # Simple check for better language indicators
        better_indicators = ['dựa trên', 'theo', 'cụ thể', 'chi tiết', 'ví dụ']
        return any(indicator in enhanced.lower() for indicator in better_indicators)
    
    def _calculate_quality_bonus(self, response: str) -> float:
        """Tính bonus cho response quality"""
        quality_bonus = 0.0
        
        # Completeness
        if len(response) >= 200:
            quality_bonus += 0.05
        
        # Structure
        if any(marker in response for marker in ['**', '###', '-', '1.', '2.']):
            quality_bonus += 0.05
        
        # Professional language
        if self._has_professional_language(response):
            quality_bonus += 0.05
        
        return quality_bonus
    
    def _has_professional_language(self, response: str) -> bool:
        """Kiểm tra ngôn ngữ chuyên nghiệp"""
        professional_indicators = ['theo quy định', 'căn cứ', 'dựa trên', 'theo tiêu chuẩn']
        return any(indicator in response.lower() for indicator in professional_indicators)
    
    def _calculate_source_utilization_bonus(self, response: str, sources: List[Dict]) -> float:
        """Tính bonus cho việc sử dụng sources"""
        if not sources:
            return 0.0
        
        # Check if response mentions source information
        source_mentions = 0
        for source in sources[:3]:
            filename = source['pdf_name']
            if any(word in response.lower() for word in filename.lower().split()):
                source_mentions += 1
        
        return min(source_mentions * 0.05, 0.15)  # Max 0.15 bonus

    def _generate_llm_answer(self, question: str, search_results: List[Dict]) -> Dict[str, Any]:
        """Tạo câu trả lời sử dụng LLM với RAG context (Legacy method - kept for compatibility)"""
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
            confidence = self._calculate_confidence(search_results, max_sources=3)
            
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
            confidence = self._calculate_confidence(top_results, max_sources=len(top_results))
            
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
    
    def _calculate_confidence(self, search_results: List[Dict], max_sources: int = 3) -> float:
        """
        Tính confidence dựa trên chất lượng search results
        
        Logic đúng: Score thấp (tốt) → Confidence cao
        Score cao (kém) → Confidence thấp
        
        Args:
            search_results: Danh sách kết quả tìm kiếm
            max_sources: Số lượng sources tối đa để tính confidence
            
        Returns:
            float: Confidence score từ 0.0 đến 1.0
        """
        try:
            if not search_results:
                return 0.0
            
            # Lấy top results để tính confidence
            top_results = search_results[:max_sources]
            if not top_results:
                return 0.0
            
            # Tính điểm trung bình
            avg_score = sum(r['score'] for r in top_results) / len(top_results)
            
            # Chuyển đổi: score thấp = confidence cao
            # Giả sử score tốt nhất là 0, tệ nhất là 200
            # Công thức: confidence = max(0, 1 - (avg_score / 200))
            confidence = max(0.0, 1.0 - (avg_score / 200.0))
            
            # Đảm bảo confidence không vượt quá 1.0
            confidence = min(confidence, 1.0)
            
            logger.info(f"📊 Confidence calculation: avg_score={avg_score:.2f}, confidence={confidence:.3f}")
            
            return confidence
            
        except Exception as e:
            logger.error(f"❌ Lỗi tính confidence: {e}")
            return 0.0
    
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
                   similarity_threshold: Optional[float] = None,
                   use_enhancement: bool = True) -> Dict[str, Any]:
        """API chính để xử lý query với pipeline 2-stage: RAG → LLM Enhancement"""
        try:
            start_time = time.time()
            
            if not self.is_initialized:
                await self.initialize()
            
            # Validate input
            if not question or not question.strip():
                raise ValueError("Question không được để trống")
            
            question = question.strip()
            logger.info(f"🔍 Processing query with 2-stage pipeline: {question[:100]}...")
            
            # 1. Search relevant chunks
            search_results = self.search_relevant_chunks(
                question=question,
                top_k=top_k,
                filter_category=filter_category,
                similarity_threshold=similarity_threshold
            )
            
            if not search_results:
                return self._create_empty_response(question)
            
            # 2. Stage 1: Generate RAG response
            rag_response = self._generate_rag_response(question, search_results)
            
            # 3. Stage 2: LLM Enhancement (if enabled)
            if use_enhancement and self.llm_service:
                try:
                    final_response = self._enhance_response_with_llm(rag_response, question)
                except Exception as e:
                    logger.warning(f"Enhancement failed: {e}, using RAG response")
                    final_response = {
                        'original_response': rag_response['raw_response'],
                        'enhanced_response': rag_response['raw_response'],
                        'sources': rag_response['sources'],
                        'confidence': rag_response['confidence'],
                        'enhancement_applied': False,
                        'stage': 'rag_generation'
                    }
            else:
                final_response = {
                    'original_response': rag_response['raw_response'],
                    'enhanced_response': rag_response['raw_response'],
                    'sources': rag_response['sources'],
                    'confidence': rag_response['confidence'],
                    'enhancement_applied': False,
                    'stage': 'rag_generation'
                }
            
            # 4. Prepare sources information
            sources = []
            if include_sources and final_response['sources']:
                for result in final_response['sources']:
                    sources.append({
                        'filename': result['pdf_name'],
                        'display_name': self._clean_filename(result['pdf_name']),
                        'category': result['category'],
                        'content_preview': result['content'][:300] + "..." if len(result['content']) > 300 else result['content'],
                        'similarity_score': result['similarity'],
                        'content_length': result['content_length']
                    })
            
            # 5. Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)
            
            # 6. Prepare final response
            response = {
                'question': question,
                'answer': final_response['enhanced_response'],
                'sources': sources,
                'total_sources': len(sources),
                'confidence': final_response['confidence'],
                'method': 'rag_llm_enhancement' if final_response['enhancement_applied'] else 'rag_generation',
                'processing_time_ms': processing_time,
                'filter_category': filter_category or 'all',
                'timestamp': datetime.now().isoformat(),
                'service_version': '2.0.0',
                'enhancement_applied': final_response['enhancement_applied'],
                'original_response': final_response['original_response'] if final_response['enhancement_applied'] else None
            }
            
            logger.info(f"✅ Query processed successfully: {len(sources)} sources, {processing_time}ms, enhancement: {final_response['enhancement_applied']}")
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
    
    def _create_empty_response(self, question: str) -> Dict[str, Any]:
        """Tạo response khi không có kết quả tìm kiếm"""
        return {
            'question': question,
            'answer': "Xin lỗi, tôi không tìm thấy thông tin liên quan đến câu hỏi của bạn trong cơ sở dữ liệu.",
            'sources': [],
            'total_sources': 0,
            'confidence': 0.0,
            'method': 'no_results',
            'processing_time_ms': 0,
            'filter_category': 'all',
            'timestamp': datetime.now().isoformat(),
            'service_version': '2.0.0',
            'enhancement_applied': False
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
                'model_path': 'models/multilingual_e5_large',
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
