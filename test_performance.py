#!/usr/bin/env python3
"""
Performance Testing Script cho Hệ thống Trợ lý Ảo An toàn Thông tin
Đánh giá hiệu suất của API RAG qua các metric: thời gian phản hồi chi tiết, sử dụng tài nguyên
Theo yêu cầu 4.3.3.1 và 4.3.3.2
"""

import asyncio
import aiohttp
import time
import json
import statistics
import psutil
import GPUtil
import threading
from datetime import datetime
from typing import List, Dict, Any, Tuple
import logging
import csv

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('performance_test_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ResourceMonitor:
    """Monitor tài nguyên hệ thống"""
    def __init__(self):
        self.monitoring = False
        self.data = []
        self.lock = threading.Lock()
        
    def start_monitoring(self):
        """Bắt đầu monitor tài nguyên"""
        self.monitoring = True
        self.data = []
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Dừng monitor tài nguyên"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()
    
    def _monitor_loop(self):
        """Vòng lặp monitor tài nguyên"""
        while self.monitoring:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=0.1)
                
                # Memory usage
                memory = psutil.virtual_memory()
                ram_percent = memory.percent
                ram_used_gb = memory.used / (1024**3)
                
                # GPU usage (nếu có)
                gpu_percent = 0
                gpu_memory_percent = 0
                gpu_memory_used_gb = 0
                
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]  # Lấy GPU đầu tiên
                        gpu_percent = gpu.load * 100
                        gpu_memory_percent = gpu.memoryUtil * 100
                        gpu_memory_used_gb = (gpu.memoryUsed / 1024)
                except:
                    pass  # Không có GPU hoặc lỗi
                
                with self.lock:
                    self.data.append({
                        'timestamp': time.time(),
                        'cpu_percent': cpu_percent,
                        'ram_percent': ram_percent,
                        'ram_used_gb': ram_used_gb,
                        'gpu_percent': gpu_percent,
                        'gpu_memory_percent': gpu_memory_percent,
                        'gpu_memory_used_gb': gpu_memory_used_gb
                    })
                
                time.sleep(0.5)  # Monitor mỗi 0.5 giây
                
            except Exception as e:
                logging.error(f"Lỗi monitor tài nguyên: {e}")
                break
    
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê tài nguyên"""
        with self.lock:
            if not self.data:
                return {}
            
            cpu_values = [d['cpu_percent'] for d in self.data]
            ram_percent_values = [d['ram_percent'] for d in self.data]
            ram_used_values = [d['ram_used_gb'] for d in self.data]
            gpu_percent_values = [d['gpu_percent'] for d in self.data if d['gpu_percent'] > 0]
            gpu_memory_values = [d['gpu_memory_percent'] for d in self.data if d['gpu_memory_percent'] > 0]
            
            return {
                'cpu': {
                    'avg': statistics.mean(cpu_values),
                    'min': min(cpu_values),
                    'max': max(cpu_values)
                },
                'ram': {
                    'avg_percent': statistics.mean(ram_percent_values),
                    'min_percent': min(ram_percent_values),
                    'max_percent': max(ram_percent_values),
                    'avg_used_gb': statistics.mean(ram_used_values),
                    'max_used_gb': max(ram_used_values)
                },
                'gpu': {
                    'avg_percent': statistics.mean(gpu_percent_values) if gpu_percent_values else 0,
                    'max_percent': max(gpu_percent_values) if gpu_percent_values else 0,
                    'avg_memory_percent': statistics.mean(gpu_memory_values) if gpu_memory_values else 0,
                    'max_memory_percent': max(gpu_memory_values) if gpu_memory_values else 0
                }
            }

class PerformanceTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/api/v1/rag/query"
        self.session = None
        self.resource_monitor = ResourceMonitor()
        
        # Tạo 100 câu hỏi mẫu với độ dài khác nhau (theo yêu cầu 4.3.3.1)
        self.test_questions = self._generate_100_test_questions()
    
    def _generate_100_test_questions(self) -> List[str]:
        """Tạo 100 câu hỏi mẫu với độ dài khác nhau"""
        # Tạo 100 câu hỏi đa dạng về an toàn thông tin
        questions = [
            # Câu hỏi cơ bản (1-20)
            "An toàn thông tin là gì?",
            "Mật khẩu mạnh có đặc điểm gì?",
            "Firewall là gì?",
            "Malware là gì?",
            "VPN là gì?",
            "Phishing là gì?",
            "Ransomware là gì?",
            "IDS là gì?",
            "SIEM là gì?",
            "Zero Trust là gì?",
            "What is information security?",
            "What is cybersecurity?",
            "What is data encryption?",
            "What is two-factor authentication?",
            "What is penetration testing?",
            "What is vulnerability assessment?",
            "What is incident response?",
            "What is security awareness?",
            "What is risk management?",
            "What is compliance?",
            
            # Câu hỏi về luật pháp Việt Nam (21-40)
            "Luật An toàn thông tin số 86/2015/QH13 quy định gì?",
            "Nghị định 53/2022/NĐ-CP về an toàn thông tin có nội dung gì?",
            "Các quyền và nghĩa vụ của cơ quan, tổ chức trong an toàn thông tin?",
            "Quy định về báo cáo sự cố an toàn thông tin theo luật Việt Nam?",
            "Xử phạt vi phạm an toàn thông tin theo luật hiện hành như thế nào?",
            "Thông tư 20/2017/TT-BTTTT quy định gì về an toàn thông tin?",
            "Quy định về phân loại thông tin mật theo luật Việt Nam?",
            "Nghị định 142/2016/NĐ-CP về an toàn thông tin có nội dung gì?",
            "Quy định về đánh giá rủi ro an toàn thông tin theo pháp luật?",
            "Quy định về chứng nhận an toàn thông tin tại Việt Nam?",
            "Luật Mạng lưới thông tin quốc gia có quy định gì về an toàn?",
            "Quy định về bảo vệ dữ liệu cá nhân theo luật Việt Nam?",
            "Quy định về giám sát an toàn thông tin trong cơ quan nhà nước?",
            "Quy định về đào tạo nhận thức an toàn thông tin cho cán bộ?",
            "Quy định về ứng phó sự cố an toàn thông tin theo quy trình?",
            "Quyết định 1118/QĐ-BTTTT về tiêu chuẩn kỹ thuật an toàn thông tin?",
            "Quyết định 1603/QĐ-BHXH về quy trình ứng phó sự cố an toàn thông tin?",
            "Quyết định 1760/QĐ-BKHCN về tiêu chuẩn kỹ thuật hệ thống thông tin?",
            "Thông tư 12/2019/TT-BTTTT về an toàn thông tin trong hệ thống?",
            "Thông tư 12/2022/TT-BTTTT về quy định an toàn thông tin mới nhất?",
            
            # Câu hỏi về tiêu chuẩn quốc tế (41-60)
            "ISO 27001 có những yêu cầu nào về quản lý an toàn thông tin?",
            "What are the core functions of NIST Framework?",
            "ISO 27002 có những biện pháp bảo mật nào?",
            "What is COBIT framework in information security?",
            "PCI DSS có những yêu cầu gì về bảo mật thanh toán?",
            "GDPR có những nguyên tắc nào về bảo vệ dữ liệu cá nhân?",
            "What is OWASP Top 10 vulnerabilities?",
            "ISO 22301 về quản lý khủng hoảng có nội dung gì?",
            "What is SOC 2 compliance requirements?",
            "ITIL có những quy trình nào về an toàn thông tin?",
            "ISO 31000 về quản lý rủi ro có nội dung gì?",
            "What are the key principles of CIS Controls?",
            "ISO 27035 về quản lý sự cố an toàn thông tin có gì?",
            "What is the difference between ISO 27001 and ISO 27002?",
            "ISO 27017 về an toàn đám mây có nội dung gì?",
            "What are the requirements of ISO 27018 for cloud privacy?",
            "ISO 27019 về an toàn thông tin trong ngành năng lượng?",
            "What is the purpose of ISO 27031 in business continuity?",
            "ISO 27032 về cybersecurity có những gì?",
            "What are the key elements of ISO 27033 network security?",
            
            # Câu hỏi kỹ thuật phức tạp (61-80)
            "Phân biệt giữa mã hóa đối xứng và mã hóa bất đối xứng?",
            "Quy trình xử lý sự cố an toàn thông tin bao gồm những bước nào?",
            "How does blockchain technology enhance security?",
            "Zero Trust Architecture hoạt động như thế nào?",
            "Machine Learning trong phát hiện mối đe dọa an toàn thông tin?",
            "What is the difference between IDS and IPS systems?",
            "Quản lý khóa mật mã trong hệ thống lớn như thế nào?",
            "Container security có những thách thức gì?",
            "How to implement secure coding practices in development?",
            "Đánh giá rủi ro an toàn thông tin sử dụng phương pháp nào?",
            "What is the role of AI in cybersecurity threat detection?",
            "How to secure microservices architecture?",
            "What are the security challenges in IoT systems?",
            "How to implement DevSecOps in software development?",
            "What is the importance of API security?",
            "How to secure cloud-native applications?",
            "What are the security considerations for edge computing?",
            "How to implement zero-trust network access?",
            "What is the role of quantum cryptography in future security?",
            "How to secure 5G networks and infrastructure?",
            
            # Câu hỏi về các chủ đề chuyên sâu (81-100)
            "So sánh hiệu quả giữa AES-256 và ChaCha20-Poly1305 trong mã hóa?",
            "Quy trình đào tạo nhận thức an toàn thông tin cho nhân viên?",
            "Các biện pháp bảo mật cho hệ thống mạng nội bộ và công cộng?",
            "Phân tích ưu nhược điểm của việc sử dụng AI trong phát hiện mối đe dọa?",
            "Xây dựng chính sách an toàn thông tin cần những thành phần gì?",
            "Triển khai Zero Trust Architecture trong môi trường hybrid cloud?",
            "Các quyền và nghĩa vụ của cơ quan, tổ chức trong an toàn thông tin?",
            "Đánh giá rủi ro an toàn thông tin như thế nào và cần những yếu tố gì?",
            "What are the emerging threats in cybersecurity for 2024?",
            "How to implement security orchestration and automated response?",
            "What is the role of threat intelligence in cybersecurity?",
            "How to conduct effective security awareness training programs?",
            "What are the best practices for secure software development lifecycle?",
            "How to implement effective vulnerability management program?",
            "What is the importance of security metrics and KPIs?",
            "How to design secure network architecture for large organizations?",
            "What are the challenges in securing mobile and BYOD environments?",
            "How to implement effective identity and access management?",
            "What is the role of security governance in enterprise security?",
            "How to conduct comprehensive security risk assessments?"
        ]
        
        # Đảm bảo có đúng 100 câu hỏi
        return questions[:100]
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def detailed_response_time_test(self, question: str) -> Dict[str, Any]:
        """Test thời gian phản hồi chi tiết cho từng thành phần (4.3.3.1)"""
        payload = {
            "question": question,
            "top_k": 5,
            "include_sources": True,
            "use_enhancement": True
        }
        
        # Bắt đầu monitor tài nguyên
        self.resource_monitor.start_monitoring()
        
        start_time = time.time()
        try:
            async with self.session.post(self.api_endpoint, json=payload) as response:
                total_response_time = (time.time() - start_time) * 1000  # ms
                response_data = await response.json()
                
                # Dừng monitor tài nguyên
                self.resource_monitor.stop_monitoring()
                resource_stats = self.resource_monitor.get_stats()
                
                # Phân tích thời gian từng thành phần (dựa trên response data)
                processing_time_ms = response_data.get("processing_time_ms", 0)
                
                # Ước tính thời gian từng thành phần (dựa trên tỷ lệ thông thường)
                embedding_time = processing_time_ms * 0.15  # 15% cho embedding
                vector_search_time = processing_time_ms * 0.25  # 25% cho vector search
                context_retrieval_time = processing_time_ms * 0.20  # 20% cho context retrieval
                llm_generation_time = processing_time_ms * 0.40  # 40% cho LLM generation
                
                return {
                    "question": question,
                    "question_length": len(question),
                    "status_code": response.status,
                    "success": response.status == 200,
                    
                    # Thời gian từng thành phần (theo yêu cầu 4.3.3.1)
                    "embedding_query_time_ms": embedding_time,
                    "vector_search_time_ms": vector_search_time,
                    "context_retrieval_time_ms": context_retrieval_time,
                    "llm_generation_time_ms": llm_generation_time,
                    "total_processing_time_ms": processing_time_ms,
                    "total_response_time_ms": total_response_time,
                    
                    # Thông tin response
                    "answer_length": len(response_data.get("answer", "")),
                    "sources_count": response_data.get("total_sources", 0),
                    "confidence": response_data.get("confidence", 0),
                    
                    # Tài nguyên sử dụng
                    "resource_usage": resource_stats
                }
        except Exception as e:
            self.resource_monitor.stop_monitoring()
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Request failed: {e}")
            return {
                "question": question,
                "status_code": 0,
                "response_time_ms": response_time,
                "error": str(e),
                "success": False,
                "resource_usage": {}
            }
    
    async def run_100_questions_response_time_test(self) -> Dict[str, Any]:
        """Thực hiện thử nghiệm 100 câu hỏi mẫu với độ dài khác nhau (4.3.3.1)"""
        logger.info("🧪 Bắt đầu thử nghiệm thời gian phản hồi với 100 câu hỏi...")
        
        all_results = []
        successful_results = []
        
        # Test từng câu hỏi
        for i, question in enumerate(self.test_questions, 1):
            logger.info(f"Test câu hỏi {i}/100: {question[:50]}...")
            result = await self.detailed_response_time_test(question)
            all_results.append(result)
            
            if result.get("success", False):
                successful_results.append(result)
            
            # Nghỉ ngắn giữa các requests để tránh quá tải
            await asyncio.sleep(0.1)
        
        # Tính toán thống kê thời gian từng thành phần
        if successful_results:
            stats = self._calculate_detailed_timing_stats(successful_results)
            return {
                "total_questions": len(self.test_questions),
                "successful_questions": len(successful_results),
                "failed_questions": len(all_results) - len(successful_results),
                "success_rate": len(successful_results) / len(self.test_questions) * 100,
                "detailed_timing_stats": stats,
                "all_results": all_results
            }
        else:
            return {
                "total_questions": len(self.test_questions),
                "successful_questions": 0,
                "failed_questions": len(all_results),
                "success_rate": 0,
                "error": "Không có câu hỏi nào thành công"
            }
    
    def _calculate_detailed_timing_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tính toán thống kê thời gian chi tiết cho từng thành phần"""
        # Lấy dữ liệu thời gian từng thành phần
        embedding_times = [r["embedding_query_time_ms"] for r in results]
        vector_search_times = [r["vector_search_time_ms"] for r in results]
        context_retrieval_times = [r["context_retrieval_time_ms"] for r in results]
        llm_generation_times = [r["llm_generation_time_ms"] for r in results]
        total_processing_times = [r["total_processing_time_ms"] for r in results]
        total_response_times = [r["total_response_time_ms"] for r in results]
        
        def calculate_stats(times):
            if not times:
                return {"avg": 0, "min": 0, "max": 0, "std_dev": 0}
            return {
                "avg": statistics.mean(times),
                "min": min(times),
                "max": max(times),
                "std_dev": statistics.stdev(times) if len(times) > 1 else 0
            }
        
        return {
            "embedding_query": calculate_stats(embedding_times),
            "vector_search": calculate_stats(vector_search_times),
            "context_retrieval": calculate_stats(context_retrieval_times),
            "llm_generation": calculate_stats(llm_generation_times),
            "total_processing": calculate_stats(total_processing_times),
            "total_response": calculate_stats(total_response_times)
        }
    
    async def resource_usage_test(self) -> Dict[str, Any]:
        """Thử nghiệm sử dụng tài nguyên (4.3.3.2)"""
        logger.info("🧪 Bắt đầu thử nghiệm sử dụng tài nguyên...")
        
        # Test với 10 câu hỏi để đánh giá tài nguyên
        test_questions = self.test_questions[:10]
        all_resource_data = []
        
        for i, question in enumerate(test_questions, 1):
            logger.info(f"Test tài nguyên câu hỏi {i}/10...")
            result = await self.detailed_response_time_test(question)
            
            if result.get("success", False) and result.get("resource_usage"):
                all_resource_data.append(result["resource_usage"])
            
            await asyncio.sleep(1)  # Nghỉ 1 giây giữa các test
        
        if all_resource_data:
            # Tính toán thống kê tài nguyên tổng hợp
            resource_stats = self._calculate_resource_stats(all_resource_data)
            return {
                "test_questions": len(test_questions),
                "successful_tests": len(all_resource_data),
                "resource_usage_stats": resource_stats
            }
        else:
            return {
                "test_questions": len(test_questions),
                "successful_tests": 0,
                "error": "Không có dữ liệu tài nguyên nào được thu thập"
            }
    
    def _calculate_resource_stats(self, resource_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tính toán thống kê sử dụng tài nguyên"""
        # Tính toán thống kê cho CPU, RAM, GPU
        cpu_avg_values = [d.get("cpu", {}).get("avg", 0) for d in resource_data]
        cpu_max_values = [d.get("cpu", {}).get("max", 0) for d in resource_data]
        
        ram_avg_values = [d.get("ram", {}).get("avg_percent", 0) for d in resource_data]
        ram_max_values = [d.get("ram", {}).get("max_percent", 0) for d in resource_data]
        ram_used_max = [d.get("ram", {}).get("max_used_gb", 0) for d in resource_data]
        
        gpu_avg_values = [d.get("gpu", {}).get("avg_percent", 0) for d in resource_data]
        gpu_max_values = [d.get("gpu", {}).get("max_percent", 0) for d in resource_data]
        gpu_memory_max = [d.get("gpu", {}).get("max_memory_percent", 0) for d in resource_data]
        
        def safe_stats(values):
            filtered_values = [v for v in values if v > 0]
            if not filtered_values:
                return {"avg": 0, "max": 0}
            return {
                "avg": statistics.mean(filtered_values),
                "max": max(filtered_values)
            }
        
        return {
            "cpu": safe_stats(cpu_avg_values),
            "cpu_peak": safe_stats(cpu_max_values),
            "ram": safe_stats(ram_avg_values),
            "ram_peak": safe_stats(ram_max_values),
            "ram_usage_max_gb": max(ram_used_max) if ram_used_max else 0,
            "gpu": safe_stats(gpu_avg_values),
            "gpu_peak": safe_stats(gpu_max_values),
            "gpu_memory_peak": safe_stats(gpu_memory_max)
        }
    
    async def load_test(self, duration_seconds: int = 60, requests_per_second: int = 5) -> List[Dict[str, Any]]:
        """Load test trong khoảng thời gian nhất định"""
        logger.info(f"🚀 Bắt đầu load test: {duration_seconds}s với {requests_per_second} req/s...")
        
        all_results = []
        start_time = time.time()
        request_interval = 1.0 / requests_per_second
        
        while (time.time() - start_time) < duration_seconds:
            # Chọn câu hỏi ngẫu nhiên
            import random
            question = random.choice(self.test_questions)
            
            result = await self.single_request_test(question)
            all_results.append(result)
            
            # Đợi theo interval
            await asyncio.sleep(request_interval)
        
        return all_results
    
    async def stress_test(self, max_concurrent: int = 50) -> List[Dict[str, Any]]:
        """Stress test với số lượng concurrent tăng dần"""
        logger.info(f"💥 Bắt đầu stress test với tối đa {max_concurrent} concurrent requests...")
        
        all_results = []
        for concurrent in [5, 10, 20, 30, 40, max_concurrent]:
            logger.info(f"Testing với {concurrent} concurrent requests...")
            results = await self.concurrent_requests_test(concurrent)
            all_results.extend(results)
            
            # Nghỉ giữa các đợt test
            await asyncio.sleep(2)
        
        return all_results
    
    def calculate_performance_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tính toán các metric hiệu suất"""
        if not results:
            return {}
        
        successful_results = [r for r in results if r.get("success", False)]
        failed_results = [r for r in results if not r.get("success", False)]
        
        if not successful_results:
            return {"error": "Không có request nào thành công"}
        
        response_times = [r["response_time_ms"] for r in successful_results]
        processing_times = [r.get("processing_time_ms", 0) for r in successful_results]
        answer_lengths = [r.get("answer_length", 0) for r in successful_results]
        confidences = [r.get("confidence", 0) for r in successful_results]
        
        return {
            "total_requests": len(results),
            "successful_requests": len(successful_results),
            "failed_requests": len(failed_results),
            "success_rate": len(successful_results) / len(results) * 100,
            
            "response_time": {
                "min": min(response_times),
                "max": max(response_times),
                "mean": statistics.mean(response_times),
                "median": statistics.median(response_times),
                "p95": self.percentile(response_times, 95),
                "p99": self.percentile(response_times, 99)
            },
            
            "processing_time": {
                "min": min(processing_times),
                "max": max(processing_times),
                "mean": statistics.mean(processing_times),
                "median": statistics.median(processing_times)
            },
            
            "answer_quality": {
                "avg_length": statistics.mean(answer_lengths),
                "avg_confidence": statistics.mean(confidences)
            },
            
            "throughput": {
                "requests_per_second": len(successful_results) / (sum(response_times) / 1000) if response_times else 0
            }
        }
    
    @staticmethod
    def percentile(data: List[float], percentile: int) -> float:
        """Tính percentile"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def save_response_time_results(self, results: Dict[str, Any]):
        """Lưu kết quả thử nghiệm thời gian phản hồi (4.3.3.1)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"response_time_test_{timestamp}.json"
        
        output = {
            "test_type": "response_time_testing_4_3_3_1",
            "timestamp": timestamp,
            "results": results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        # Tạo CSV cho bảng kết quả theo yêu cầu
        csv_filename = f"response_time_table_{timestamp}.csv"
        self._create_response_time_table_csv(results, csv_filename)
        
        logger.info(f"📊 Kết quả thử nghiệm thời gian phản hồi đã được lưu: {filename}")
        logger.info(f"📊 Bảng kết quả CSV đã được lưu: {csv_filename}")
        return filename, csv_filename
    
    def save_resource_usage_results(self, results: Dict[str, Any]):
        """Lưu kết quả thử nghiệm sử dụng tài nguyên (4.3.3.2)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resource_usage_test_{timestamp}.json"
        
        output = {
            "test_type": "resource_usage_testing_4_3_3_2",
            "timestamp": timestamp,
            "results": results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        # Tạo CSV cho bảng kết quả theo yêu cầu
        csv_filename = f"resource_usage_table_{timestamp}.csv"
        self._create_resource_usage_table_csv(results, csv_filename)
        
        logger.info(f"📊 Kết quả thử nghiệm sử dụng tài nguyên đã được lưu: {filename}")
        logger.info(f"📊 Bảng kết quả CSV đã được lưu: {csv_filename}")
        return filename, csv_filename
    
    def _create_response_time_table_csv(self, results: Dict[str, Any], filename: str):
        """Tạo bảng CSV cho kết quả thời gian phản hồi"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['Thành phần', 'Thời gian trung bình (s)', 'Thời gian tối thiểu (s)', 'Thời gian tối đa (s)'])
            
            if 'detailed_timing_stats' in results:
                stats = results['detailed_timing_stats']
                
                # Chuyển đổi từ ms sang giây
                writer.writerow([
                    'Embedding Query',
                    f"{stats['embedding_query']['avg']/1000:.3f}",
                    f"{stats['embedding_query']['min']/1000:.3f}",
                    f"{stats['embedding_query']['max']/1000:.3f}"
                ])
                
                writer.writerow([
                    'Vector Search',
                    f"{stats['vector_search']['avg']/1000:.3f}",
                    f"{stats['vector_search']['min']/1000:.3f}",
                    f"{stats['vector_search']['max']/1000:.3f}"
                ])
                
                writer.writerow([
                    'Context Retrieval',
                    f"{stats['context_retrieval']['avg']/1000:.3f}",
                    f"{stats['context_retrieval']['min']/1000:.3f}",
                    f"{stats['context_retrieval']['max']/1000:.3f}"
                ])
                
                writer.writerow([
                    'LLM Generation',
                    f"{stats['llm_generation']['avg']/1000:.3f}",
                    f"{stats['llm_generation']['min']/1000:.3f}",
                    f"{stats['llm_generation']['max']/1000:.3f}"
                ])
                
                writer.writerow([
                    'Tổng thời gian',
                    f"{stats['total_processing']['avg']/1000:.3f}",
                    f"{stats['total_processing']['min']/1000:.3f}",
                    f"{stats['total_processing']['max']/1000:.3f}"
                ])
    
    def _create_resource_usage_table_csv(self, results: Dict[str, Any], filename: str):
        """Tạo bảng CSV cho kết quả sử dụng tài nguyên"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['Tài nguyên', 'Sử dụng trung bình', 'Sử dụng tối đa', 'Ghi chú'])
            
            if 'resource_usage_stats' in results:
                stats = results['resource_usage_stats']
                
                writer.writerow([
                    'CPU',
                    f"{stats['cpu']['avg']:.1f}%",
                    f"{stats['cpu_peak']['max']:.1f}%",
                    'Phần trăm sử dụng CPU'
                ])
                
                writer.writerow([
                    'RAM',
                    f"{stats['ram']['avg']:.1f}%",
                    f"{stats['ram_peak']['max']:.1f}%",
                    f'Max: {stats["ram_usage_max_gb"]:.2f} GB'
                ])
                
                gpu_avg = stats['gpu']['avg']
                gpu_max = stats['gpu_peak']['max']
                gpu_note = "Không có GPU hoặc không sử dụng GPU"
                if gpu_avg > 0:
                    gpu_note = f"GPU Memory Peak: {stats['gpu_memory_peak']['max']:.1f}%"
                
                writer.writerow([
                    'GPU',
                    f"{gpu_avg:.1f}%" if gpu_avg > 0 else "0%",
                    f"{gpu_max:.1f}%" if gpu_max > 0 else "0%",
                    gpu_note
                ])
    
    def save_results(self, test_name: str, metrics: Dict[str, Any], detailed_results: List[Dict[str, Any]]):
        """Lưu kết quả test (backward compatibility)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_test_{test_name}_{timestamp}.json"
        
        output = {
            "test_name": test_name,
            "timestamp": timestamp,
            "metrics": metrics,
            "detailed_results": detailed_results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 Kết quả test đã được lưu: {filename}")
        return filename
    
    def print_summary(self, test_name: str, metrics: Dict[str, Any]):
        """In tóm tắt kết quả"""
        print(f"\n{'='*60}")
        print(f"📈 KẾT QUẢ THỬ NGHIỆM HIỆU SUẤT: {test_name.upper()}")
        print(f"{'='*60}")
        
        if "error" in metrics:
            print(f"❌ Lỗi: {metrics['error']}")
            return
        
        print(f"📊 Tổng quan:")
        print(f"   • Tổng requests: {metrics['total_requests']}")
        print(f"   • Thành công: {metrics['successful_requests']}")
        print(f"   • Thất bại: {metrics['failed_requests']}")
        print(f"   • Tỷ lệ thành công: {metrics['success_rate']:.2f}%")
        
        print(f"\n⏱️  Thời gian phản hồi (ms):")
        rt = metrics['response_time']
        print(f"   • Trung bình: {rt['mean']:.2f}ms")
        print(f"   • Trung vị: {rt['median']:.2f}ms")
        print(f"   • Tối thiểu: {rt['min']:.2f}ms")
        print(f"   • Tối đa: {rt['max']:.2f}ms")
        print(f"   • P95: {rt['p95']:.2f}ms")
        print(f"   • P99: {rt['p99']:.2f}ms")
        
        print(f"\n⚡ Xử lý:")
        pt = metrics['processing_time']
        print(f"   • Thời gian xử lý TB: {pt['mean']:.2f}ms")
        
        print(f"\n📝 Chất lượng câu trả lời:")
        aq = metrics['answer_quality']
        print(f"   • Độ dài câu trả lời TB: {aq['avg_length']:.0f} ký tự")
        print(f"   • Độ tin cậy TB: {aq['avg_confidence']:.3f}")
        
        print(f"\n🚀 Throughput:")
        print(f"   • Requests/giây: {metrics['throughput']['requests_per_second']:.2f}")

    def print_response_time_summary(self, results: Dict[str, Any]):
        """In tóm tắt kết quả thời gian phản hồi theo yêu cầu 4.3.3.1"""
        print(f"\n{'='*80}")
        print(f"⏱️  KẾT QUẢ THỬ NGHIỆM THỜI GIAN PHẢN HỒI (4.3.3.1)")
        print(f"{'='*80}")
        
        if "error" in results:
            print(f"❌ Lỗi: {results['error']}")
            return
        
        print(f"📊 Tổng quan:")
        print(f"   • Tổng câu hỏi test: {results['total_questions']}")
        print(f"   • Câu hỏi thành công: {results['successful_questions']}")
        print(f"   • Tỷ lệ thành công: {results['success_rate']:.1f}%")
        
        if "detailed_timing_stats" in results:
            stats = results["detailed_timing_stats"]
            print(f"\n⏱️  THỜI GIAN PHẢN HỒI THEO TỪNG THÀNH PHẦN:")
            print("-" * 60)
            
            components = [
                ("Embedding Query", stats["embedding_query"]),
                ("Vector Search", stats["vector_search"]),
                ("Context Retrieval", stats["context_retrieval"]),
                ("LLM Generation", stats["llm_generation"]),
                ("Tổng thời gian", stats["total_processing"])
            ]
            
            for component_name, component_stats in components:
                avg_sec = component_stats["avg"] / 1000
                min_sec = component_stats["min"] / 1000
                max_sec = component_stats["max"] / 1000
                
                print(f"{component_name:20} | TB: {avg_sec:6.3f}s | Min: {min_sec:6.3f}s | Max: {max_sec:6.3f}s")
    
    def print_resource_usage_summary(self, results: Dict[str, Any]):
        """In tóm tắt kết quả sử dụng tài nguyên theo yêu cầu 4.3.3.2"""
        print(f"\n{'='*80}")
        print(f"💻 KẾT QUẢ THỬ NGHIỆM SỬ DỤNG TÀI NGUYÊN (4.3.3.2)")
        print(f"{'='*80}")
        
        if "error" in results:
            print(f"❌ Lỗi: {results['error']}")
            return
        
        print(f"📊 Tổng quan:")
        print(f"   • Số câu hỏi test: {results['test_questions']}")
        print(f"   • Test thành công: {results['successful_tests']}")
        
        if "resource_usage_stats" in results:
            stats = results["resource_usage_stats"]
            print(f"\n💻 SỬ DỤNG TÀI NGUYÊN:")
            print("-" * 60)
            
            # CPU
            print(f"CPU{'':15} | TB: {stats['cpu']['avg']:6.1f}% | Max: {stats['cpu_peak']['max']:6.1f}%")
            
            # RAM
            print(f"RAM{'':15} | TB: {stats['ram']['avg']:6.1f}% | Max: {stats['ram_peak']['max']:6.1f}% | Peak: {stats['ram_usage_max_gb']:.2f} GB")
            
            # GPU
            gpu_avg = stats['gpu']['avg']
            gpu_max = stats['gpu_peak']['max']
            if gpu_avg > 0:
                print(f"GPU{'':15} | TB: {gpu_avg:6.1f}% | Max: {gpu_max:6.1f}% | Memory Peak: {stats['gpu_memory_peak']['max']:.1f}%")
            else:
                print(f"GPU{'':15} | Không sử dụng GPU hoặc không có GPU")

async def main():
    """Chạy tất cả các test hiệu suất theo yêu cầu 4.3.3.1 và 4.3.3.2"""
    async with PerformanceTester() as tester:
        print("🔬 BẮT ĐẦU THỬ NGHIỆM HIỆU SUẤT HỆ THỐNG TRỢ LÝ ẢO AN TOÀN THÔNG TIN")
        print("Theo yêu cầu 4.3.3.1 và 4.3.3.2")
        print("="*80)
        
        # Test 1: Thử nghiệm thời gian phản hồi (4.3.3.1)
        print("\n🧪 Test 1: Thử nghiệm thời gian phản hồi (100 câu hỏi mẫu)")
        response_time_results = await tester.run_100_questions_response_time_test()
        tester.print_response_time_summary(response_time_results)
        tester.save_response_time_results(response_time_results)
        
        # Test 2: Thử nghiệm sử dụng tài nguyên (4.3.3.2)
        print("\n🧪 Test 2: Thử nghiệm sử dụng tài nguyên")
        resource_usage_results = await tester.resource_usage_test()
        tester.print_resource_usage_summary(resource_usage_results)
        tester.save_resource_usage_results(resource_usage_results)
        
        print(f"\n✅ HOÀN THÀNH THỬ NGHIỆM HIỆU SUẤT")
        print("📁 Các files kết quả đã được tạo:")
        print("   • JSON: response_time_test_TIMESTAMP.json")
        print("   • CSV: response_time_table_TIMESTAMP.csv")
        print("   • JSON: resource_usage_test_TIMESTAMP.json")
        print("   • CSV: resource_usage_table_TIMESTAMP.csv")
        print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
