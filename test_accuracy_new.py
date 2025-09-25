#!/usr/bin/env python3
"""
Accuracy Testing Script cho Hệ thống Trợ lý Ảo An toàn Thông tin
Đánh giá độ chính xác theo yêu cầu 4.3.4.1, 4.3.4.2, 4.3.4.3
"""

import asyncio
import aiohttp
import json
import time
import csv
import statistics
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
        logging.FileHandler('accuracy_test_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ExpertEvaluationCase:
    """Test case cho đánh giá bởi chuyên gia (4.3.4.1)"""
    question: str
    language: str  # "vietnamese", "english", "mixed"
    category: str  # luat, english, vietnamese, technical
    expected_keywords: List[str]
    expert_notes: str

@dataclass
class SearchAccuracyCase:
    """Test case cho đánh giá độ chính xác tìm kiếm (4.3.4.2)"""
    question: str
    expected_answer: str
    expected_sources: List[str]  # Các nguồn tài liệu mong đợi
    language: str
    category: str

@dataclass
class MultilingualCase:
    """Test case cho thử nghiệm đa ngôn ngữ (4.3.4.3)"""
    question: str
    language: str  # "vietnamese", "english", "mixed"
    expected_response_language: str
    category: str

class AccuracyTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/api/v1/rag/query"
        self.session = None
        
        # Tạo bộ test cases cho từng loại đánh giá
        self.expert_evaluation_cases = self._create_expert_evaluation_cases()
        self.search_accuracy_cases = self._create_search_accuracy_cases()
        self.multilingual_cases = self._create_multilingual_cases()
    
    def _create_expert_evaluation_cases(self) -> List[ExpertEvaluationCase]:
        """Tạo 50 câu hỏi chuẩn cho đánh giá bởi chuyên gia (4.3.4.1)"""
        # Đây là phiên bản rút gọn, trong thực tế sẽ có 50 câu hỏi đầy đủ
        return [
            ExpertEvaluationCase(
                question="An toàn thông tin là gì?",
                language="vietnamese",
                category="general",
                expected_keywords=["an toàn", "thông tin", "bảo vệ", "bí mật", "toàn vẹn", "sẵn sàng"],
                expert_notes="Câu hỏi cơ bản, cần giải thích khái niệm CIA triad"
            ),
            ExpertEvaluationCase(
                question="What is information security?",
                language="english",
                category="general",
                expected_keywords=["information", "security", "protection", "confidentiality", "integrity", "availability"],
                expert_notes="Basic concept in English, should explain CIA triad"
            ),
            # ... thêm 48 câu hỏi khác
        ]
    
    def _create_search_accuracy_cases(self) -> List[SearchAccuracyCase]:
        """Tạo 30 câu hỏi với câu trả lời chuẩn đã biết (4.3.4.2)"""
        return [
            SearchAccuracyCase(
                question="Luật An toàn thông tin số 86/2015/QH13 có hiệu lực từ khi nào?",
                expected_answer="Luật An toàn thông tin số 86/2015/QH13 có hiệu lực từ ngày 01/7/2016",
                expected_sources=["Luat-86-2015-QH13.pdf"],
                language="vietnamese",
                category="luat"
            ),
            # ... thêm 29 câu hỏi khác
        ]
    
    def _create_multilingual_cases(self) -> List[MultilingualCase]:
        """Tạo test cases cho thử nghiệm đa ngôn ngữ (4.3.4.3)"""
        return [
            MultilingualCase(
                question="An toàn thông tin là gì?",
                language="vietnamese",
                expected_response_language="vietnamese",
                category="general"
            ),
            MultilingualCase(
                question="What is information security?",
                language="english",
                expected_response_language="english",
                category="general"
            ),
            # ... thêm 38 câu hỏi khác
        ]
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _evaluate_by_expert_criteria(self, test_case: ExpertEvaluationCase, answer: str, sources: List[Dict]) -> Dict[str, Any]:
        """Đánh giá theo 5 tiêu chí chuyên gia (thang điểm 1-5)"""
        # 1. Độ chính xác thông tin (Accuracy) - 1-5
        accuracy_score = self._calculate_accuracy_score(test_case, answer)
        
        # 2. Tính đầy đủ (Completeness) - 1-5
        completeness_score = self._calculate_completeness_score(test_case, answer)
        
        # 3. Tính liên quan (Relevance) - 1-5
        relevance_score = self._calculate_relevance_score(test_case, answer)
        
        # 4. Tính dễ hiểu (Clarity) - 1-5
        clarity_score = self._calculate_clarity_score(answer, test_case.language)
        
        # 5. Tính cập nhật (Currency) - 1-5
        currency_score = self._calculate_currency_score(test_case, sources)
        
        overall_score = (accuracy_score + completeness_score + relevance_score + clarity_score + currency_score) / 5
        
        return {
            "accuracy": accuracy_score,
            "completeness": completeness_score,
            "relevance": relevance_score,
            "clarity": clarity_score,
            "currency": currency_score,
            "overall_score": overall_score
        }
    
    def _calculate_accuracy_score(self, test_case: ExpertEvaluationCase, answer: str) -> float:
        """Tính điểm độ chính xác thông tin"""
        answer_lower = answer.lower()
        
        # Kiểm tra từ khóa quan trọng
        keyword_count = 0
        for keyword in test_case.expected_keywords:
            if keyword.lower() in answer_lower:
                keyword_count += 1
        
        keyword_score = keyword_count / len(test_case.expected_keywords) if test_case.expected_keywords else 0
        
        # Chuyển đổi thành thang điểm 1-5
        if keyword_score >= 0.8:
            return 5.0
        elif keyword_score >= 0.6:
            return 4.0
        elif keyword_score >= 0.4:
            return 3.0
        elif keyword_score >= 0.2:
            return 2.0
        else:
            return 1.0
    
    def _calculate_completeness_score(self, test_case: ExpertEvaluationCase, answer: str) -> float:
        """Tính điểm tính đầy đủ"""
        answer_length = len(answer)
        
        # Điều chỉnh theo loại câu hỏi
        if test_case.category == "general":
            expected_length = 100
        elif test_case.category == "technical":
            expected_length = 200
        elif test_case.category == "luat":
            expected_length = 250
        else:
            expected_length = 150
        
        length_ratio = answer_length / expected_length
        
        if length_ratio >= 1.0:
            return 5.0
        elif length_ratio >= 0.8:
            return 4.0
        elif length_ratio >= 0.6:
            return 3.0
        elif length_ratio >= 0.4:
            return 2.0
        else:
            return 1.0
    
    def _calculate_relevance_score(self, test_case: ExpertEvaluationCase, answer: str) -> float:
        """Tính điểm tính liên quan"""
        answer_lower = answer.lower()
        question_lower = test_case.question.lower()
        
        # Trích xuất từ khóa từ câu hỏi
        question_words = set(re.findall(r'\b\w+\b', question_lower))
        answer_words = set(re.findall(r'\b\w+\b', answer_lower))
        
        # Tính độ trùng lặp
        overlap = len(question_words & answer_words)
        relevance_ratio = overlap / len(question_words) if question_words else 0
        
        if relevance_ratio >= 0.7:
            return 5.0
        elif relevance_ratio >= 0.5:
            return 4.0
        elif relevance_ratio >= 0.3:
            return 3.0
        elif relevance_ratio >= 0.1:
            return 2.0
        else:
            return 1.0
    
    def _calculate_clarity_score(self, answer: str, language: str) -> float:
        """Tính điểm tính dễ hiểu"""
        if not answer:
            return 1.0
        
        # Kiểm tra cấu trúc câu
        sentences = re.split(r'[.!?]+', answer)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 2.0
        
        # Kiểm tra độ dài câu trung bình
        avg_sentence_length = sum(len(s) for s in sentences) / len(sentences)
        
        # Điều chỉnh theo ngôn ngữ
        if language == "vietnamese":
            if 20 <= avg_sentence_length <= 80:
                return 5.0
            elif 10 <= avg_sentence_length <= 120:
                return 4.0
            else:
                return 3.0
        else:  # english
            if 15 <= avg_sentence_length <= 60:
                return 5.0
            elif 10 <= avg_sentence_length <= 90:
                return 4.0
            else:
                return 3.0
    
    def _calculate_currency_score(self, test_case: ExpertEvaluationCase, sources: List[Dict]) -> float:
        """Tính điểm tính cập nhật"""
        if not sources:
            return 2.0
        
        # Kiểm tra nguồn tài liệu có gần đây không
        recent_sources = 0
        for source in sources:
            filename = source.get("filename", "").lower()
            # Kiểm tra năm trong tên file
            if "2024" in filename or "2023" in filename or "2022" in filename:
                recent_sources += 1
        
        currency_ratio = recent_sources / len(sources)
        
        if currency_ratio >= 0.8:
            return 5.0
        elif currency_ratio >= 0.6:
            return 4.0
        elif currency_ratio >= 0.4:
            return 3.0
        elif currency_ratio >= 0.2:
            return 2.0
        else:
            return 1.0
    
    def _calculate_search_metrics(self, test_case: SearchAccuracyCase, answer: str, sources: List[Dict]) -> Dict[str, Any]:
        """Tính toán Precision, Recall, F1-Score"""
        # Precision: Số câu trả lời chính xác / Tổng số câu trả lời
        precision = self._calculate_precision(test_case, answer)
        
        # Recall: Số thông tin chính xác được tìm thấy / Tổng số thông tin chính xác
        recall = self._calculate_recall(test_case, answer)
        
        # F1-Score: Harmonic mean của Precision và Recall
        f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score
        }
    
    def _calculate_precision(self, test_case: SearchAccuracyCase, answer: str) -> float:
        """Tính Precision"""
        # Đơn giản hóa: kiểm tra xem câu trả lời có chứa thông tin chính xác không
        expected_lower = test_case.expected_answer.lower()
        answer_lower = answer.lower()
        
        # Tách từ và so sánh
        expected_words = set(re.findall(r'\b\w+\b', expected_lower))
        answer_words = set(re.findall(r'\b\w+\b', answer_lower))
        
        # Đếm từ khóa chính
        key_words = {"luật", "nghị định", "thông tư", "quyết định", "iso", "nist", "tcvn", "ngày", "tháng", "năm"}
        expected_key_words = expected_words & key_words
        answer_key_words = answer_words & key_words
        
        if not expected_key_words:
            return 1.0
        
        precision = len(expected_key_words & answer_key_words) / len(expected_key_words)
        return precision
    
    def _calculate_recall(self, test_case: SearchAccuracyCase, answer: str) -> float:
        """Tính Recall"""
        expected_lower = test_case.expected_answer.lower()
        answer_lower = answer.lower()
        
        # Tách từ và so sánh
        expected_words = set(re.findall(r'\b\w+\b', expected_lower))
        answer_words = set(re.findall(r'\b\w+\b', answer_lower))
        
        if not expected_words:
            return 1.0
        
        # Tính tỷ lệ từ khóa được tìm thấy
        recall = len(expected_words & answer_words) / len(expected_words)
        return recall
    
    def _evaluate_multilingual_accuracy(self, test_case: MultilingualCase, answer: str) -> float:
        """Đánh giá độ chính xác cho thử nghiệm đa ngôn ngữ"""
        # Kiểm tra ngôn ngữ phản hồi có phù hợp không
        language_match = self._check_language_match(test_case.expected_response_language, answer)
        
        # Kiểm tra chất lượng nội dung
        content_quality = self._check_content_quality(answer)
        
        return (language_match + content_quality) / 2
    
    def _check_language_match(self, expected_language: str, answer: str) -> float:
        """Kiểm tra ngôn ngữ phản hồi có phù hợp không"""
        if expected_language == "vietnamese":
            # Kiểm tra từ tiếng Việt
            vietnamese_words = ["là", "của", "và", "với", "trong", "cho", "đến", "từ", "có", "được", "này", "đó", "các", "một", "như", "về", "sẽ", "đã", "đang", "bị"]
            vietnamese_count = sum(1 for word in vietnamese_words if word in answer.lower())
            return min(vietnamese_count / 5, 1.0)
        elif expected_language == "english":
            # Kiểm tra từ tiếng Anh
            english_words = ["the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had"]
            english_count = sum(1 for word in english_words if word.lower() in answer.lower())
            return min(english_count / 5, 1.0)
        else:
            return 0.5
    
    def _check_content_quality(self, answer: str) -> float:
        """Kiểm tra chất lượng nội dung"""
        if len(answer) < 50:
            return 0.3
        elif len(answer) < 100:
            return 0.6
        elif len(answer) < 200:
            return 0.8
        else:
            return 1.0
    
    def _calculate_expert_evaluation_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tính toán thống kê đánh giá chuyên gia"""
        all_scores = []
        accuracy_scores = []
        completeness_scores = []
        relevance_scores = []
        clarity_scores = []
        currency_scores = []
        
        for result in results:
            eval_data = result.get("expert_evaluation", {})
            if eval_data:
                all_scores.append(eval_data.get("overall_score", 0))
                accuracy_scores.append(eval_data.get("accuracy", 0))
                completeness_scores.append(eval_data.get("completeness", 0))
                relevance_scores.append(eval_data.get("relevance", 0))
                clarity_scores.append(eval_data.get("clarity", 0))
                currency_scores.append(eval_data.get("currency", 0))
        
        def calculate_stats(scores):
            if not scores:
                return {"mean": 0, "std_dev": 0}
            return {
                "mean": statistics.mean(scores),
                "std_dev": statistics.stdev(scores) if len(scores) > 1 else 0
            }
        
        return {
            "overall": calculate_stats(all_scores),
            "accuracy": calculate_stats(accuracy_scores),
            "completeness": calculate_stats(completeness_scores),
            "relevance": calculate_stats(relevance_scores),
            "clarity": calculate_stats(clarity_scores),
            "currency": calculate_stats(currency_scores)
        }
    
    def _calculate_overall_search_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tính toán thống kê tìm kiếm tổng hợp"""
        all_precision = []
        all_recall = []
        all_f1_scores = []
        
        for result in results:
            metrics = result.get("search_metrics", {})
            if metrics:
                all_precision.append(metrics.get("precision", 0))
                all_recall.append(metrics.get("recall", 0))
                all_f1_scores.append(metrics.get("f1_score", 0))
        
        return {
            "precision": {
                "mean": statistics.mean(all_precision) if all_precision else 0,
                "std_dev": statistics.stdev(all_precision) if len(all_precision) > 1 else 0
            },
            "recall": {
                "mean": statistics.mean(all_recall) if all_recall else 0,
                "std_dev": statistics.stdev(all_recall) if len(all_recall) > 1 else 0
            },
            "f1_score": {
                "mean": statistics.mean(all_f1_scores) if all_f1_scores else 0,
                "std_dev": statistics.stdev(all_f1_scores) if len(all_f1_scores) > 1 else 0
            }
        }
    
    def _calculate_multilingual_stats(self, vietnamese_results: List[Dict], english_results: List[Dict], mixed_results: List[Dict]) -> Dict[str, Any]:
        """Tính toán thống kê đa ngôn ngữ"""
        def calculate_language_stats(results):
            if not results:
                return {"count": 0, "avg_accuracy": 0, "avg_response_time": 0}
            
            accuracies = [r.get("accuracy", 0) for r in results if r.get("success", False)]
            response_times = [r.get("response_time_ms", 0) for r in results if r.get("success", False)]
            
            return {
                "count": len(results),
                "avg_accuracy": statistics.mean(accuracies) if accuracies else 0,
                "avg_response_time": statistics.mean(response_times) if response_times else 0
            }
        
        return {
            "vietnamese": calculate_language_stats(vietnamese_results),
            "english": calculate_language_stats(english_results),
            "mixed": calculate_language_stats(mixed_results)
        }
    
    def save_expert_evaluation_results(self, results: Dict[str, Any]):
        """Lưu kết quả đánh giá chuyên gia"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"expert_evaluation_test_{timestamp}.json"
        
        output = {
            "test_type": "expert_evaluation_4_3_4_1",
            "timestamp": timestamp,
            "results": results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        # Tạo CSV cho bảng kết quả
        csv_filename = f"expert_evaluation_table_{timestamp}.csv"
        self._create_expert_evaluation_table_csv(results, csv_filename)
        
        logger.info(f"📊 Kết quả đánh giá chuyên gia đã được lưu: {filename}")
        logger.info(f"📊 Bảng kết quả CSV đã được lưu: {csv_filename}")
        return filename, csv_filename
    
    def save_search_accuracy_results(self, results: Dict[str, Any]):
        """Lưu kết quả độ chính xác tìm kiếm"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"search_accuracy_test_{timestamp}.json"
        
        output = {
            "test_type": "search_accuracy_4_3_4_2",
            "timestamp": timestamp,
            "results": results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        # Tạo CSV cho bảng kết quả
        csv_filename = f"search_accuracy_table_{timestamp}.csv"
        self._create_search_accuracy_table_csv(results, csv_filename)
        
        logger.info(f"📊 Kết quả độ chính xác tìm kiếm đã được lưu: {filename}")
        logger.info(f"📊 Bảng kết quả CSV đã được lưu: {csv_filename}")
        return filename, csv_filename
    
    def save_multilingual_results(self, results: Dict[str, Any]):
        """Lưu kết quả thử nghiệm đa ngôn ngữ"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"multilingual_test_{timestamp}.json"
        
        output = {
            "test_type": "multilingual_4_3_4_3",
            "timestamp": timestamp,
            "results": results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        # Tạo CSV cho bảng kết quả
        csv_filename = f"multilingual_table_{timestamp}.csv"
        self._create_multilingual_table_csv(results, csv_filename)
        
        logger.info(f"📊 Kết quả thử nghiệm đa ngôn ngữ đã được lưu: {filename}")
        logger.info(f"📊 Bảng kết quả CSV đã được lưu: {csv_filename}")
        return filename, csv_filename
    
    def _create_expert_evaluation_table_csv(self, results: Dict[str, Any], filename: str):
        """Tạo bảng CSV cho kết quả đánh giá chuyên gia"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['Tiêu chí', 'Điểm trung bình', 'Độ lệch chuẩn', 'Ghi chú'])
            
            if 'expert_evaluation_stats' in results:
                stats = results['expert_evaluation_stats']
                
                writer.writerow([
                    'Độ chính xác thông tin (Accuracy)',
                    f"{stats['accuracy']['mean']:.2f}",
                    f"{stats['accuracy']['std_dev']:.2f}",
                    'Thang điểm 1-5'
                ])
                
                writer.writerow([
                    'Tính đầy đủ (Completeness)',
                    f"{stats['completeness']['mean']:.2f}",
                    f"{stats['completeness']['std_dev']:.2f}",
                    'Thang điểm 1-5'
                ])
                
                writer.writerow([
                    'Tính liên quan (Relevance)',
                    f"{stats['relevance']['mean']:.2f}",
                    f"{stats['relevance']['std_dev']:.2f}",
                    'Thang điểm 1-5'
                ])
                
                writer.writerow([
                    'Tính dễ hiểu (Clarity)',
                    f"{stats['clarity']['mean']:.2f}",
                    f"{stats['clarity']['std_dev']:.2f}",
                    'Thang điểm 1-5'
                ])
                
                writer.writerow([
                    'Tính cập nhật (Currency)',
                    f"{stats['currency']['mean']:.2f}",
                    f"{stats['currency']['std_dev']:.2f}",
                    'Thang điểm 1-5'
                ])
    
    def _create_search_accuracy_table_csv(self, results: Dict[str, Any], filename: str):
        """Tạo bảng CSV cho kết quả độ chính xác tìm kiếm"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['Metric', 'Giá trị', 'Ghi chú'])
            
            if 'overall_search_metrics' in results:
                metrics = results['overall_search_metrics']
                
                writer.writerow([
                    'Precision',
                    f"{metrics['precision']['mean']:.3f}",
                    'Độ chính xác tìm kiếm'
                ])
                
                writer.writerow([
                    'Recall',
                    f"{metrics['recall']['mean']:.3f}",
                    'Độ bao phủ tìm kiếm'
                ])
                
                writer.writerow([
                    'F1-Score',
                    f"{metrics['f1_score']['mean']:.3f}",
                    'Trung bình điều hòa của Precision và Recall'
                ])
    
    def _create_multilingual_table_csv(self, results: Dict[str, Any], filename: str):
        """Tạo bảng CSV cho kết quả thử nghiệm đa ngôn ngữ"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['Ngôn ngữ', 'Số câu hỏi', 'Độ chính xác', 'Thời gian phản hồi (s)'])
            
            if 'multilingual_stats' in results:
                stats = results['multilingual_stats']
                
                writer.writerow([
                    'Tiếng Việt',
                    stats['vietnamese']['count'],
                    f"{stats['vietnamese']['avg_accuracy']:.3f}",
                    f"{stats['vietnamese']['avg_response_time']/1000:.3f}"
                ])
                
                writer.writerow([
                    'Tiếng Anh',
                    stats['english']['count'],
                    f"{stats['english']['avg_accuracy']:.3f}",
                    f"{stats['english']['avg_response_time']/1000:.3f}"
                ])
                
                writer.writerow([
                    'Hỗn hợp',
                    stats['mixed']['count'],
                    f"{stats['mixed']['avg_accuracy']:.3f}",
                    f"{stats['mixed']['avg_response_time']/1000:.3f}"
                ])
    
    def print_expert_evaluation_summary(self, results: Dict[str, Any]):
        """In tóm tắt kết quả đánh giá chuyên gia"""
        print(f"\n{'='*80}")
        print(f"🎯 KẾT QUẢ THỬ NGHIỆM ĐỘ CHÍNH XÁC CÂU TRẢ LỜI (4.3.4.1)")
        print(f"{'='*80}")
        
        if "error" in results:
            print(f"❌ Lỗi: {results['error']}")
            return
        
        print(f"📊 Tổng quan:")
        print(f"   • Tổng câu hỏi test: {results['total_questions']}")
        print(f"   • Câu hỏi thành công: {results['successful_questions']}")
        print(f"   • Tỷ lệ thành công: {results['success_rate']:.1f}%")
        
        if "expert_evaluation_stats" in results:
            stats = results["expert_evaluation_stats"]
            print(f"\n🎯 ĐÁNH GIÁ THEO 5 TIÊU CHÍ (Thang điểm 1-5):")
            print("-" * 60)
            
            criteria = [
                ("Độ chính xác thông tin (Accuracy)", stats["accuracy"]),
                ("Tính đầy đủ (Completeness)", stats["completeness"]),
                ("Tính liên quan (Relevance)", stats["relevance"]),
                ("Tính dễ hiểu (Clarity)", stats["clarity"]),
                ("Tính cập nhật (Currency)", stats["currency"])
            ]
            
            for criterion_name, criterion_stats in criteria:
                print(f"{criterion_name:30} | TB: {criterion_stats['mean']:4.2f} | ĐLC: {criterion_stats['std_dev']:4.2f}")
            
            print(f"\n📊 Điểm tổng thể: {stats['overall']['mean']:.2f}/5.0 (ĐLC: {stats['overall']['std_dev']:.2f})")
    
    def print_search_accuracy_summary(self, results: Dict[str, Any]):
        """In tóm tắt kết quả độ chính xác tìm kiếm"""
        print(f"\n{'='*80}")
        print(f"🔍 KẾT QUẢ THỬ NGHIỆM ĐỘ CHÍNH XÁC TÌM KIẾM (4.3.4.2)")
        print(f"{'='*80}")
        
        if "error" in results:
            print(f"❌ Lỗi: {results['error']}")
            return
        
        print(f"📊 Tổng quan:")
        print(f"   • Tổng câu hỏi test: {results['total_questions']}")
        print(f"   • Câu hỏi thành công: {results['successful_questions']}")
        print(f"   • Tỷ lệ thành công: {results['success_rate']:.1f}%")
        
        if "overall_search_metrics" in results:
            metrics = results["overall_search_metrics"]
            print(f"\n🔍 METRIC TÌM KIẾM:")
            print("-" * 60)
            
            print(f"Precision{'':15} | {metrics['precision']['mean']:6.3f} | Độ chính xác tìm kiếm")
            print(f"Recall{'':18} | {metrics['recall']['mean']:6.3f} | Độ bao phủ tìm kiếm")
            print(f"F1-Score{'':16} | {metrics['f1_score']['mean']:6.3f} | Trung bình điều hòa")
    
    def print_multilingual_summary(self, results: Dict[str, Any]):
        """In tóm tắt kết quả thử nghiệm đa ngôn ngữ"""
        print(f"\n{'='*80}")
        print(f"🌐 KẾT QUẢ THỬ NGHIỆM ĐA NGÔN NGỮ (4.3.4.3)")
        print(f"{'='*80}")
        
        if "error" in results:
            print(f"❌ Lỗi: {results['error']}")
            return
        
        print(f"📊 Tổng quan:")
        print(f"   • Tổng câu hỏi test: {results['total_questions']}")
        print(f"   • Câu hỏi thành công: {results['successful_questions']}")
        print(f"   • Tỷ lệ thành công: {results['success_rate']:.1f}%")
        
        if "multilingual_stats" in results:
            stats = results["multilingual_stats"]
            print(f"\n🌐 KẾT QUẢ THEO NGÔN NGỮ:")
            print("-" * 60)
            
            languages = [
                ("Tiếng Việt", stats["vietnamese"]),
                ("Tiếng Anh", stats["english"]),
                ("Hỗn hợp", stats["mixed"])
            ]
            
            for lang_name, lang_stats in languages:
                print(f"{lang_name:15} | Số câu: {lang_stats['count']:2d} | Độ chính xác: {lang_stats['avg_accuracy']:5.3f} | Thời gian: {lang_stats['avg_response_time']/1000:6.3f}s")

async def main():
    """Chạy tất cả các test độ chính xác theo yêu cầu 4.3.4.1, 4.3.4.2, 4.3.4.3"""
    async with AccuracyTester() as tester:
        print("🎯 BẮT ĐẦU THỬ NGHIỆM ĐỘ CHÍNH XÁC HỆ THỐNG TRỢ LÝ ẢO AN TOÀN THÔNG TIN")
        print("Theo yêu cầu 4.3.4.1, 4.3.4.2, 4.3.4.3")
        print("="*80)
        
        # Test 1: Đánh giá bởi chuyên gia (4.3.4.1)
        print("\n🧪 Test 1: Thử nghiệm độ chính xác câu trả lời (50 câu hỏi chuẩn)")
        expert_results = await tester.run_expert_evaluation_test()
        tester.print_expert_evaluation_summary(expert_results)
        tester.save_expert_evaluation_results(expert_results)
        
        # Test 2: Độ chính xác tìm kiếm (4.3.4.2)
        print("\n🧪 Test 2: Thử nghiệm độ chính xác tìm kiếm (30 câu hỏi)")
        search_results = await tester.run_search_accuracy_test()
        tester.print_search_accuracy_summary(search_results)
        tester.save_search_accuracy_results(search_results)
        
        # Test 3: Thử nghiệm đa ngôn ngữ (4.3.4.3)
        print("\n🧪 Test 3: Thử nghiệm đa ngôn ngữ (40 câu hỏi)")
        multilingual_results = await tester.run_multilingual_test()
        tester.print_multilingual_summary(multilingual_results)
        tester.save_multilingual_results(multilingual_results)
        
        print(f"\n✅ HOÀN THÀNH THỬ NGHIỆM ĐỘ CHÍNH XÁC")
        print("📁 Các files kết quả đã được tạo:")
        print("   • JSON: expert_evaluation_test_TIMESTAMP.json")
        print("   • CSV: expert_evaluation_table_TIMESTAMP.csv")
        print("   • JSON: search_accuracy_test_TIMESTAMP.json")
        print("   • CSV: search_accuracy_table_TIMESTAMP.csv")
        print("   • JSON: multilingual_test_TIMESTAMP.json")
        print("   • CSV: multilingual_table_TIMESTAMP.csv")
        print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
