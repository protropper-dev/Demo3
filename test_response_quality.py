#!/usr/bin/env python3
"""
Response Quality Testing Script cho Hệ thống Trợ lý Ảo An toàn Thông tin
Đánh giá chất lượng phản hồi qua các tiêu chí: coherence, relevance, helpfulness, clarity
"""

import asyncio
import aiohttp
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple
import logging
from dataclasses import dataclass

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('response_quality_test_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class QualityTestCase:
    """Test case cho response quality testing"""
    question: str
    context: str  # Ngữ cảnh của câu hỏi
    expected_response_type: str  # factual, procedural, comparative, explanatory
    expected_tone: str  # professional, educational, technical, friendly
    complexity_level: str  # basic, intermediate, advanced
    user_type: str  # beginner, expert, administrator, student

class ResponseQualityTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/api/v1/rag/query"
        self.session = None
        
        # Tạo bộ test cases cho quality testing
        self.test_cases = self._create_quality_test_cases()
    
    def _create_quality_test_cases(self) -> List[QualityTestCase]:
        """Tạo bộ test cases đa dạng cho quality testing"""
        return [
            # Test cases cho người mới bắt đầu
            QualityTestCase(
                question="Tôi mới làm việc với an toàn thông tin, bạn có thể giải thích đơn giản không?",
                context="Người dùng mới bắt đầu tìm hiểu về an toàn thông tin",
                expected_response_type="explanatory",
                expected_tone="educational",
                complexity_level="basic",
                user_type="beginner"
            ),
            QualityTestCase(
                question="Tại sao tôi cần quan tâm đến an toàn thông tin?",
                context="Câu hỏi từ người chưa hiểu tầm quan trọng của an toàn thông tin",
                expected_response_type="explanatory",
                expected_tone="educational",
                complexity_level="basic",
                user_type="beginner"
            ),
            
            # Test cases cho chuyên gia kỹ thuật
            QualityTestCase(
                question="So sánh hiệu quả giữa AES-256 và ChaCha20-Poly1305 trong việc mã hóa dữ liệu nhạy cảm",
                context="Chuyên gia bảo mật cần thông tin kỹ thuật chi tiết",
                expected_response_type="comparative",
                expected_tone="technical",
                complexity_level="advanced",
                user_type="expert"
            ),
            QualityTestCase(
                question="Cách triển khai Zero Trust Architecture trong môi trường hybrid cloud?",
                context="Kiến trúc sư bảo mật cần hướng dẫn triển khai",
                expected_response_type="procedural",
                expected_tone="technical",
                complexity_level="advanced",
                user_type="expert"
            ),
            
            # Test cases cho quản trị viên hệ thống
            QualityTestCase(
                question="Tôi cần thiết lập chính sách mật khẩu cho 500 nhân viên, bạn có gợi ý gì?",
                context="Quản trị viên cần hướng dẫn thực tế",
                expected_response_type="procedural",
                expected_tone="professional",
                complexity_level="intermediate",
                user_type="administrator"
            ),
            QualityTestCase(
                question="Các bước xử lý khi phát hiện ransomware trong hệ thống?",
                context="Sự cố khẩn cấp cần hướng dẫn rõ ràng",
                expected_response_type="procedural",
                expected_tone="professional",
                complexity_level="intermediate",
                user_type="administrator"
            ),
            
            # Test cases cho sinh viên/học viên
            QualityTestCase(
                question="Bạn có thể giải thích khái niệm CIA triad trong an toàn thông tin không?",
                context="Sinh viên học về nguyên tắc cơ bản",
                expected_response_type="explanatory",
                expected_tone="educational",
                complexity_level="basic",
                user_type="student"
            ),
            QualityTestCase(
                question="Ví dụ thực tế về vi phạm an toàn thông tin và hậu quả của nó?",
                context="Học viên cần ví dụ cụ thể để hiểu",
                expected_response_type="explanatory",
                expected_tone="educational",
                complexity_level="intermediate",
                user_type="student"
            ),
            
            # Test cases kiểm tra khả năng xử lý câu hỏi phức tạp
            QualityTestCase(
                question="Làm thế nào để đánh giá và cải thiện chương trình đào tạo nhận thức an toàn thông tin cho tổ chức?",
                context="Câu hỏi phức tạp đòi hỏi phân tích và đưa ra giải pháp",
                expected_response_type="procedural",
                expected_tone="professional",
                complexity_level="advanced",
                user_type="administrator"
            ),
            QualityTestCase(
                question="Phân tích ưu nhược điểm của việc sử dụng AI trong phát hiện và ngăn chặn mối đe dọa an toàn thông tin",
                context="Câu hỏi phân tích đòi hỏi tư duy phản biện",
                expected_response_type="comparative",
                expected_tone="technical",
                complexity_level="advanced",
                user_type="expert"
            ),
            
            # Test cases kiểm tra khả năng thích ứng với ngữ cảnh
            QualityTestCase(
                question="Tôi đang làm việc tại ngân hàng, các quy định an toàn thông tin nào tôi cần tuân thủ?",
                context="Ngữ cảnh cụ thể về lĩnh vực ngân hàng",
                expected_response_type="factual",
                expected_tone="professional",
                complexity_level="intermediate",
                user_type="administrator"
            ),
            QualityTestCase(
                question="Khác biệt giữa GDPR và Luật An toàn thông tin Việt Nam về bảo vệ dữ liệu cá nhân?",
                context="So sánh quy định quốc tế và trong nước",
                expected_response_type="comparative",
                expected_tone="professional",
                complexity_level="advanced",
                user_type="expert"
            )
        ]
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_single_quality_case(self, test_case: QualityTestCase) -> Dict[str, Any]:
        """Test một quality test case đơn lẻ"""
        payload = {
            "question": test_case.question,
            "top_k": 5,
            "include_sources": True,
            "use_enhancement": True
        }
        
        try:
            async with self.session.post(self.api_endpoint, json=payload) as response:
                if response.status != 200:
                    return {
                        "test_case": test_case.question,
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "quality_metrics": {}
                    }
                
                response_data = await response.json()
                answer = response_data.get("answer", "")
                sources = response_data.get("sources", [])
                
                # Đánh giá chất lượng phản hồi
                quality_metrics = self._evaluate_response_quality(test_case, answer, sources)
                
                return {
                    "test_case": test_case.question,
                    "context": test_case.context,
                    "success": True,
                    "answer": answer,
                    "sources": sources,
                    "quality_metrics": quality_metrics,
                    "response_data": response_data
                }
        
        except Exception as e:
            logger.error(f"Quality test case failed: {test_case.question} - {e}")
            return {
                "test_case": test_case.question,
                "success": False,
                "error": str(e),
                "quality_metrics": {}
            }
    
    def _evaluate_response_quality(self, test_case: QualityTestCase, answer: str, sources: List[Dict]) -> Dict[str, Any]:
        """Đánh giá chất lượng phản hồi"""
        
        # 1. Coherence - Tính mạch lạc và logic
        coherence_score = self._calculate_coherence(answer)
        
        # 2. Relevance - Tính liên quan đến câu hỏi
        relevance_score = self._calculate_relevance(test_case.question, answer)
        
        # 3. Helpfulness - Tính hữu ích cho người dùng
        helpfulness_score = self._calculate_helpfulness(test_case, answer)
        
        # 4. Clarity - Tính rõ ràng và dễ hiểu
        clarity_score = self._calculate_clarity(answer, test_case.complexity_level)
        
        # 5. Completeness - Tính đầy đủ
        completeness_score = self._calculate_completeness(test_case, answer)
        
        # 6. Tone Appropriateness - Tính phù hợp của giọng điệu
        tone_score = self._calculate_tone_appropriateness(answer, test_case.expected_tone)
        
        # 7. Source Quality - Chất lượng nguồn tham khảo
        source_quality_score = self._calculate_source_quality(sources)
        
        # 8. Structure - Cấu trúc và tổ chức thông tin
        structure_score = self._calculate_structure(answer)
        
        # Tính điểm tổng hợp
        overall_score = (
            coherence_score * 0.15 +
            relevance_score * 0.15 +
            helpfulness_score * 0.15 +
            clarity_score * 0.15 +
            completeness_score * 0.15 +
            tone_score * 0.10 +
            source_quality_score * 0.10 +
            structure_score * 0.05
        )
        
        return {
            "coherence": coherence_score,
            "relevance": relevance_score,
            "helpfulness": helpfulness_score,
            "clarity": clarity_score,
            "completeness": completeness_score,
            "tone_appropriateness": tone_score,
            "source_quality": source_quality_score,
            "structure": structure_score,
            "overall_score": overall_score,
            "answer_length": len(answer),
            "sources_count": len(sources),
            "complexity_level": test_case.complexity_level,
            "user_type": test_case.user_type,
            "expected_tone": test_case.expected_tone
        }
    
    def _calculate_coherence(self, answer: str) -> float:
        """Tính tính mạch lạc của câu trả lời"""
        if not answer:
            return 0.0
        
        # Kiểm tra cấu trúc câu và đoạn văn
        sentences = re.split(r'[.!?]+', answer)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 0.5
        
        # Kiểm tra từ nối logic
        logical_connectors = [
            "do đó", "vì vậy", "tuy nhiên", "ngoài ra", "đồng thời",
            "trước tiên", "tiếp theo", "cuối cùng", "tổng kết",
            "về mặt", "xét về", "cụ thể", "ví dụ", "như vậy"
        ]
        
        connector_count = sum(1 for connector in logical_connectors if connector in answer.lower())
        connector_score = min(connector_count / 3, 1.0)  # Tối đa 3 từ nối
        
        # Kiểm tra độ dài câu hợp lý
        avg_sentence_length = sum(len(s) for s in sentences) / len(sentences)
        length_score = 1.0 if 20 <= avg_sentence_length <= 100 else 0.7
        
        return (connector_score + length_score) / 2
    
    def _calculate_relevance(self, question: str, answer: str) -> float:
        """Tính tính liên quan đến câu hỏi"""
        if not answer or not question:
            return 0.0
        
        # Trích xuất từ khóa chính từ câu hỏi
        question_keywords = self._extract_keywords(question)
        answer_keywords = self._extract_keywords(answer)
        
        if not question_keywords:
            return 0.5
        
        # Tính độ trùng lặp từ khóa
        common_keywords = set(question_keywords) & set(answer_keywords)
        keyword_relevance = len(common_keywords) / len(question_keywords)
        
        # Kiểm tra xem câu trả lời có trả lời trực tiếp câu hỏi không
        question_type_indicators = {
            "what": ["là gì", "là", "định nghĩa", "khái niệm"],
            "how": ["như thế nào", "cách", "làm sao", "quy trình"],
            "why": ["tại sao", "lý do", "nguyên nhân"],
            "when": ["khi nào", "thời gian", "lúc nào"],
            "where": ["ở đâu", "nơi nào", "địa điểm"]
        }
        
        question_lower = question.lower()
        answer_lower = answer.lower()
        
        direct_answer_score = 0.0
        for q_type, indicators in question_type_indicators.items():
            if any(indicator in question_lower for indicator in indicators):
                # Kiểm tra xem câu trả lời có chứa từ khóa liên quan không
                if any(indicator in answer_lower for indicator in indicators):
                    direct_answer_score = 1.0
                    break
                else:
                    direct_answer_score = 0.7
        
        return (keyword_relevance + direct_answer_score) / 2
    
    def _calculate_helpfulness(self, test_case: QualityTestCase, answer: str) -> float:
        """Tính tính hữu ích cho người dùng"""
        if not answer:
            return 0.0
        
        helpfulness_score = 0.0
        
        # Kiểm tra có cung cấp thông tin thực tế không
        if len(answer) > 50:  # Độ dài tối thiểu
            helpfulness_score += 0.3
        
        # Kiểm tra có ví dụ cụ thể không
        example_indicators = ["ví dụ", "chẳng hạn", "cụ thể", "thực tế", "như"]
        if any(indicator in answer.lower() for indicator in example_indicators):
            helpfulness_score += 0.2
        
        # Kiểm tra có hướng dẫn thực hiện không (cho procedural questions)
        if test_case.expected_response_type == "procedural":
            action_indicators = ["bước", "thực hiện", "tiến hành", "triển khai", "cài đặt"]
            if any(indicator in answer.lower() for indicator in action_indicators):
                helpfulness_score += 0.3
            else:
                helpfulness_score += 0.1
        else:
            helpfulness_score += 0.2
        
        # Kiểm tra có nguồn tham khảo không
        if "nguồn" in answer.lower() or "tham khảo" in answer.lower():
            helpfulness_score += 0.1
        
        # Kiểm tra có cảnh báo hoặc lưu ý quan trọng không
        warning_indicators = ["lưu ý", "cảnh báo", "quan trọng", "chú ý", "cần thiết"]
        if any(indicator in answer.lower() for indicator in warning_indicators):
            helpfulness_score += 0.1
        
        return min(helpfulness_score, 1.0)
    
    def _calculate_clarity(self, answer: str, complexity_level: str) -> float:
        """Tính tính rõ ràng và dễ hiểu"""
        if not answer:
            return 0.0
        
        clarity_score = 0.0
        
        # Kiểm tra cấu trúc đoạn văn
        paragraphs = [p.strip() for p in answer.split('\n') if p.strip()]
        if len(paragraphs) > 1:
            clarity_score += 0.2
        
        # Kiểm tra độ dài câu phù hợp với độ phức tạp
        sentences = re.split(r'[.!?]+', answer)
        avg_sentence_length = sum(len(s.strip()) for s in sentences if s.strip()) / len(sentences)
        
        if complexity_level == "basic":
            if avg_sentence_length <= 50:
                clarity_score += 0.3
            else:
                clarity_score += 0.1
        elif complexity_level == "intermediate":
            if 30 <= avg_sentence_length <= 80:
                clarity_score += 0.3
            else:
                clarity_score += 0.1
        else:  # advanced
            if 40 <= avg_sentence_length <= 120:
                clarity_score += 0.3
            else:
                clarity_score += 0.1
        
        # Kiểm tra từ khó hiểu (technical jargon không cần thiết)
        complex_terms = ["paradigm", "infrastructure", "implementation", "architecture"]
        complex_count = sum(1 for term in complex_terms if term.lower() in answer.lower())
        if complexity_level == "basic" and complex_count > 2:
            clarity_score -= 0.1
        elif complexity_level == "advanced" and complex_count < 1:
            clarity_score -= 0.1
        
        # Kiểm tra có giải thích thuật ngữ không
        explanation_indicators = ["nghĩa là", "tức là", "có thể hiểu", "được định nghĩa"]
        if any(indicator in answer.lower() for indicator in explanation_indicators):
            clarity_score += 0.2
        
        return max(min(clarity_score, 1.0), 0.0)
    
    def _calculate_completeness(self, test_case: QualityTestCase, answer: str) -> float:
        """Tính tính đầy đủ của câu trả lời"""
        if not answer:
            return 0.0
        
        completeness_score = 0.0
        
        # Kiểm tra độ dài phù hợp với loại câu hỏi
        if test_case.expected_response_type == "factual":
            if len(answer) >= 100:
                completeness_score += 0.3
        elif test_case.expected_response_type == "procedural":
            if len(answer) >= 200:
                completeness_score += 0.3
        elif test_case.expected_response_type == "comparative":
            if len(answer) >= 250:
                completeness_score += 0.3
        elif test_case.expected_response_type == "explanatory":
            if len(answer) >= 150:
                completeness_score += 0.3
        
        # Kiểm tra có đề cập đến các khía cạnh khác nhau không
        aspect_indicators = ["đầu tiên", "thứ hai", "ngoài ra", "mặt khác", "đồng thời"]
        aspect_count = sum(1 for indicator in aspect_indicators if indicator in answer.lower())
        completeness_score += min(aspect_count * 0.1, 0.3)
        
        # Kiểm tra có kết luận hoặc tóm tắt không
        conclusion_indicators = ["tóm lại", "kết luận", "tổng kết", "như vậy", "cuối cùng"]
        if any(indicator in answer.lower() for indicator in conclusion_indicators):
            completeness_score += 0.2
        
        # Kiểm tra có đề cập đến nguồn tham khảo không
        if "theo" in answer.lower() or "nguồn" in answer.lower():
            completeness_score += 0.2
        
        return min(completeness_score, 1.0)
    
    def _calculate_tone_appropriateness(self, answer: str, expected_tone: str) -> float:
        """Tính tính phù hợp của giọng điệu"""
        if not answer:
            return 0.0
        
        tone_indicators = {
            "professional": ["theo quy định", "cần thiết", "bắt buộc", "tuân thủ", "thực hiện"],
            "educational": ["hãy cùng", "bạn có thể", "để hiểu", "giải thích", "ví dụ"],
            "technical": ["triển khai", "cấu hình", "thuật toán", "giao thức", "kiến trúc"],
            "friendly": ["bạn", "tôi", "chúng ta", "cùng nhau", "hãy"]
        }
        
        answer_lower = answer.lower()
        expected_indicators = tone_indicators.get(expected_tone, [])
        
        if not expected_indicators:
            return 0.5
        
        indicator_count = sum(1 for indicator in expected_indicators if indicator in answer_lower)
        return min(indicator_count / len(expected_indicators) * 2, 1.0)
    
    def _calculate_source_quality(self, sources: List[Dict]) -> float:
        """Tính chất lượng nguồn tham khảo"""
        if not sources:
            return 0.0
        
        quality_score = 0.0
        
        # Kiểm tra số lượng nguồn
        if len(sources) >= 2:
            quality_score += 0.3
        elif len(sources) >= 1:
            quality_score += 0.2
        
        # Kiểm tra chất lượng nguồn (dựa trên tên file và category)
        for source in sources:
            filename = source.get("filename", "").lower()
            category = source.get("category", "")
            similarity = source.get("similarity_score", 0)
            
            # Điểm cho nguồn có độ tương đồng cao
            if similarity > 0.7:
                quality_score += 0.2
            elif similarity > 0.5:
                quality_score += 0.1
            
            # Điểm cho nguồn uy tín (ISO, NIST, Luật, TCVN)
            if any(keyword in filename for keyword in ["iso", "nist", "luat", "tcvn", "nghị định"]):
                quality_score += 0.2
        
        return min(quality_score, 1.0)
    
    def _calculate_structure(self, answer: str) -> float:
        """Tính cấu trúc và tổ chức thông tin"""
        if not answer:
            return 0.0
        
        structure_score = 0.0
        
        # Kiểm tra có tiêu đề hoặc đánh số không
        if re.search(r'^\d+\.', answer, re.MULTILINE) or re.search(r'^[A-Z][a-z]+:', answer, re.MULTILINE):
            structure_score += 0.3
        
        # Kiểm tra có danh sách không
        if re.search(r'[-•*]\s', answer) or re.search(r'\d+\.\s', answer):
            structure_score += 0.2
        
        # Kiểm tra có đoạn văn riêng biệt không
        paragraphs = [p.strip() for p in answer.split('\n\n') if p.strip()]
        if len(paragraphs) > 1:
            structure_score += 0.3
        
        # Kiểm tra có từ nối giữa các ý không
        transition_words = ["đầu tiên", "tiếp theo", "ngoài ra", "tuy nhiên", "do đó"]
        if any(word in answer.lower() for word in transition_words):
            structure_score += 0.2
        
        return min(structure_score, 1.0)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Trích xuất từ khóa từ văn bản"""
        # Loại bỏ dấu câu và chuyển thành chữ thường
        clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Tách từ
        words = clean_text.split()
        
        # Loại bỏ từ dừng tiếng Việt
        stop_words = {
            "là", "của", "và", "với", "trong", "cho", "đến", "từ", "có", "được",
            "này", "đó", "các", "một", "như", "về", "sẽ", "đã", "đang", "bị"
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords[:10]  # Lấy 10 từ khóa quan trọng nhất
    
    async def run_all_quality_tests(self) -> List[Dict[str, Any]]:
        """Chạy tất cả quality test cases"""
        logger.info(f"🧪 Bắt đầu chạy {len(self.test_cases)} quality test cases...")
        
        all_results = []
        for i, test_case in enumerate(self.test_cases, 1):
            logger.info(f"Quality test case {i}/{len(self.test_cases)}: {test_case.question[:50]}...")
            result = await self.test_single_quality_case(test_case)
            all_results.append(result)
            
            # Nghỉ ngắn giữa các test
            await asyncio.sleep(0.5)
        
        return all_results
    
    def calculate_quality_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tính toán các metric chất lượng tổng thể"""
        successful_results = [r for r in results if r.get("success", False)]
        failed_results = [r for r in results if not r.get("success", False)]
        
        if not successful_results:
            return {"error": "Không có quality test case nào thành công"}
        
        # Tính toán metrics tổng thể
        all_scores = [r["quality_metrics"]["overall_score"] for r in successful_results]
        coherence_scores = [r["quality_metrics"]["coherence"] for r in successful_results]
        relevance_scores = [r["quality_metrics"]["relevance"] for r in successful_results]
        helpfulness_scores = [r["quality_metrics"]["helpfulness"] for r in successful_results]
        clarity_scores = [r["quality_metrics"]["clarity"] for r in successful_results]
        completeness_scores = [r["quality_metrics"]["completeness"] for r in successful_results]
        tone_scores = [r["quality_metrics"]["tone_appropriateness"] for r in successful_results]
        source_scores = [r["quality_metrics"]["source_quality"] for r in successful_results]
        structure_scores = [r["quality_metrics"]["structure"] for r in successful_results]
        
        # Phân tích theo độ phức tạp
        complexity_analysis = {}
        for complexity in ["basic", "intermediate", "advanced"]:
            complexity_results = [r for r in successful_results if r["quality_metrics"]["complexity_level"] == complexity]
            if complexity_results:
                scores = [r["quality_metrics"]["overall_score"] for r in complexity_results]
                complexity_analysis[complexity] = {
                    "count": len(complexity_results),
                    "avg_score": sum(scores) / len(scores),
                    "min_score": min(scores),
                    "max_score": max(scores)
                }
        
        # Phân tích theo loại người dùng
        user_type_analysis = {}
        for user_type in ["beginner", "expert", "administrator", "student"]:
            user_type_results = [r for r in successful_results if r["quality_metrics"]["user_type"] == user_type]
            if user_type_results:
                scores = [r["quality_metrics"]["overall_score"] for r in user_type_results]
                user_type_analysis[user_type] = {
                    "count": len(user_type_results),
                    "avg_score": sum(scores) / len(scores),
                    "min_score": min(scores),
                    "max_score": max(scores)
                }
        
        return {
            "total_tests": len(results),
            "successful_tests": len(successful_results),
            "failed_tests": len(failed_results),
            "success_rate": len(successful_results) / len(results) * 100,
            
            "overall_quality_scores": {
                "mean": sum(all_scores) / len(all_scores),
                "min": min(all_scores),
                "max": max(all_scores),
                "std_dev": self._calculate_std_dev(all_scores)
            },
            
            "component_scores": {
                "coherence": {
                    "mean": sum(coherence_scores) / len(coherence_scores),
                    "min": min(coherence_scores),
                    "max": max(coherence_scores)
                },
                "relevance": {
                    "mean": sum(relevance_scores) / len(relevance_scores),
                    "min": min(relevance_scores),
                    "max": max(relevance_scores)
                },
                "helpfulness": {
                    "mean": sum(helpfulness_scores) / len(helpfulness_scores),
                    "min": min(helpfulness_scores),
                    "max": max(helpfulness_scores)
                },
                "clarity": {
                    "mean": sum(clarity_scores) / len(clarity_scores),
                    "min": min(clarity_scores),
                    "max": max(clarity_scores)
                },
                "completeness": {
                    "mean": sum(completeness_scores) / len(completeness_scores),
                    "min": min(completeness_scores),
                    "max": max(completeness_scores)
                },
                "tone_appropriateness": {
                    "mean": sum(tone_scores) / len(tone_scores),
                    "min": min(tone_scores),
                    "max": max(tone_scores)
                },
                "source_quality": {
                    "mean": sum(source_scores) / len(source_scores),
                    "min": min(source_scores),
                    "max": max(source_scores)
                },
                "structure": {
                    "mean": sum(structure_scores) / len(structure_scores),
                    "min": min(structure_scores),
                    "max": max(structure_scores)
                }
            },
            
            "complexity_analysis": complexity_analysis,
            "user_type_analysis": user_type_analysis
        }
    
    @staticmethod
    def _calculate_std_dev(scores: List[float]) -> float:
        """Tính độ lệch chuẩn"""
        if len(scores) < 2:
            return 0.0
        
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / (len(scores) - 1)
        return variance ** 0.5
    
    def save_results(self, metrics: Dict[str, Any], detailed_results: List[Dict[str, Any]]):
        """Lưu kết quả test"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"response_quality_test_results_{timestamp}.json"
        
        output = {
            "test_type": "response_quality_testing",
            "timestamp": timestamp,
            "metrics": metrics,
            "detailed_results": detailed_results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 Kết quả test đã được lưu: {filename}")
        return filename
    
    def print_summary(self, metrics: Dict[str, Any]):
        """In tóm tắt kết quả"""
        print(f"\n{'='*60}")
        print(f"📝 KẾT QUẢ THỬ NGHIỆM CHẤT LƯỢNG PHẢN HỒI")
        print(f"{'='*60}")
        
        if "error" in metrics:
            print(f"❌ Lỗi: {metrics['error']}")
            return
        
        print(f"📊 Tổng quan:")
        print(f"   • Tổng test cases: {metrics['total_tests']}")
        print(f"   • Thành công: {metrics['successful_tests']}")
        print(f"   • Thất bại: {metrics['failed_tests']}")
        print(f"   • Tỷ lệ thành công: {metrics['success_rate']:.2f}%")
        
        print(f"\n📝 Điểm chất lượng tổng thể:")
        overall = metrics['overall_quality_scores']
        print(f"   • Điểm trung bình: {overall['mean']:.3f}/1.0")
        print(f"   • Điểm thấp nhất: {overall['min']:.3f}")
        print(f"   • Điểm cao nhất: {overall['max']:.3f}")
        print(f"   • Độ lệch chuẩn: {overall['std_dev']:.3f}")
        
        print(f"\n🎯 Phân tích thành phần:")
        components = metrics['component_scores']
        print(f"   • Mạch lạc: {components['coherence']['mean']:.3f}")
        print(f"   • Liên quan: {components['relevance']['mean']:.3f}")
        print(f"   • Hữu ích: {components['helpfulness']['mean']:.3f}")
        print(f"   • Rõ ràng: {components['clarity']['mean']:.3f}")
        print(f"   • Đầy đủ: {components['completeness']['mean']:.3f}")
        print(f"   • Giọng điệu: {components['tone_appropriateness']['mean']:.3f}")
        print(f"   • Chất lượng nguồn: {components['source_quality']['mean']:.3f}")
        print(f"   • Cấu trúc: {components['structure']['mean']:.3f}")
        
        print(f"\n📈 Phân tích theo độ phức tạp:")
        for complexity, analysis in metrics['complexity_analysis'].items():
            print(f"   • {complexity.title()}: {analysis['avg_score']:.3f} (n={analysis['count']})")
        
        print(f"\n👥 Phân tích theo loại người dùng:")
        for user_type, analysis in metrics['user_type_analysis'].items():
            print(f"   • {user_type.title()}: {analysis['avg_score']:.3f} (n={analysis['count']})")

async def main():
    """Chạy response quality testing"""
    async with ResponseQualityTester() as tester:
        print("📝 BẮT ĐẦU THỬ NGHIỆM CHẤT LƯỢNG PHẢN HỒI HỆ THỐNG TRỢ LÝ ẢO AN TOÀN THÔNG TIN")
        print("="*80)
        
        # Chạy tất cả quality test cases
        results = await tester.run_all_quality_tests()
        
        # Tính toán metrics
        metrics = tester.calculate_quality_metrics(results)
        
        # In kết quả
        tester.print_summary(metrics)
        
        # Lưu kết quả
        tester.save_results(metrics, results)
        
        print(f"\n✅ HOÀN THÀNH THỬ NGHIỆM CHẤT LƯỢNG PHẢN HỒI")
        print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
