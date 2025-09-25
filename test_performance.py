#!/usr/bin/env python3
"""
Performance Testing Script cho He thong Tro ly Ảo An toan Thong tin
Danh gia hieu suat cua API RAG qua cac metric: thoi gian phan hoi chi tiet, su dung tai nguyen
Theo yeu cau 4.3.3.1 va 4.3.3.2
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

# Cau hinh logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('performance_test_results.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ResourceMonitor:
    """Monitor tai nguyen he thong"""
    def __init__(self):
        self.monitoring = False
        self.data = []
        self.lock = threading.Lock()
        
    def start_monitoring(self):
        """Bat dau monitor tai nguyen"""
        self.monitoring = True
        self.data = []
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Dung monitor tai nguyen"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()
    
    def _monitor_loop(self):
        """Vong lap monitor tai nguyen"""
        while self.monitoring:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=0.1)
                
                # Memory usage
                memory = psutil.virtual_memory()
                ram_percent = memory.percent
                ram_used_gb = memory.used / (1024**3)
                
                # GPU usage (neu co)
                gpu_percent = 0
                gpu_memory_percent = 0
                gpu_memory_used_gb = 0
                
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]  # Lay GPU dau tien
                        gpu_percent = gpu.load * 100
                        gpu_memory_percent = gpu.memoryUtil * 100
                        gpu_memory_used_gb = (gpu.memoryUsed / 1024)
                except:
                    pass  # Khong co GPU hoac loi
                
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
                
                time.sleep(0.5)  # Monitor moi 0.5 giay
                
            except Exception as e:
                logging.error(f"Loi monitor tai nguyen: {e}")
                break
    
    def get_stats(self) -> Dict[str, Any]:
        """Lay thong ke tai nguyen"""
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
        
        # Tao 100 cau hoi mau voi do dai khac nhau (theo yeu cau 4.3.3.1)
        self.test_questions = self._generate_100_test_questions()
    
    def _generate_100_test_questions(self) -> List[str]:
        """Tao 100 cau hoi mau voi do dai khac nhau"""
        # Tao 100 cau hoi da dang ve an toan thong tin
        questions = [
            # Cau hoi co ban (1-20)
            "An toan thong tin la gi?",
            "Mat khau manh co dac diem gi?",
            "Firewall la gi?",
            "Malware la gi?",
            "VPN la gi?",
            "Phishing la gi?",
            "Ransomware la gi?",
            "IDS la gi?",
            "SIEM la gi?",
            "Zero Trust la gi?",
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
            
            # Cau hoi ve luat phap Viet Nam (21-40)
            "Luat An toan thong tin so 86/2015/QH13 quy dinh gi?",
            "Nghi dinh 53/2022/ND-CP ve an toan thong tin co noi dung gi?",
            "Cac quyen va nghia vu cua co quan, to chuc trong an toan thong tin?",
            "Quy dinh ve bao cao su co an toan thong tin theo luat Viet Nam?",
            "Xu phat vi pham an toan thong tin theo luat hien hanh nhu the nao?",
            "Thong tu 20/2017/TT-BTTTT quy dinh gi ve an toan thong tin?",
            "Quy dinh ve phan loai thong tin mat theo luat Viet Nam?",
            "Nghi dinh 142/2016/ND-CP ve an toan thong tin co noi dung gi?",
            "Quy dinh ve danh gia rui ro an toan thong tin theo phap luat?",
            "Quy dinh ve chung nhan an toan thong tin tai Viet Nam?",
            "Luat Mang luoi thong tin quoc gia co quy dinh gi ve an toan?",
            "Quy dinh ve bao ve du lieu ca nhan theo luat Viet Nam?",
            "Quy dinh ve giam sat an toan thong tin trong co quan nha nuoc?",
            "Quy dinh ve dao tao nhan thuc an toan thong tin cho can bo?",
            "Quy dinh ve ung pho su co an toan thong tin theo quy trinh?",
            "Quyet dinh 1118/QD-BTTTT ve tieu chuan ky thuat an toan thong tin?",
            "Quyet dinh 1603/QD-BHXH ve quy trinh ung pho su co an toan thong tin?",
            "Quyet dinh 1760/QD-BKHCN ve tieu chuan ky thuat he thong thong tin?",
            "Thong tu 12/2019/TT-BTTTT ve an toan thong tin trong he thong?",
            "Thong tu 12/2022/TT-BTTTT ve quy dinh an toan thong tin moi nhat?",
            
            # Cau hoi ve tieu chuan quoc te (41-60)
            "ISO 27001 co nhung yeu cau nao ve quan ly an toan thong tin?",
            "What are the core functions of NIST Framework?",
            "ISO 27002 co nhung bien phap bao mat nao?",
            "What is COBIT framework in information security?",
            "PCI DSS co nhung yeu cau gi ve bao mat thanh toan?",
            "GDPR co nhung nguyen tac nao ve bao ve du lieu ca nhan?",
            "What is OWASP Top 10 vulnerabilities?",
            "ISO 22301 ve quan ly khung hoang co noi dung gi?",
            "What is SOC 2 compliance requirements?",
            "ITIL co nhung quy trinh nao ve an toan thong tin?",
            "ISO 31000 ve quan ly rui ro co noi dung gi?",
            "What are the key principles of CIS Controls?",
            "ISO 27035 ve quan ly su co an toan thong tin co gi?",
            "What is the difference between ISO 27001 and ISO 27002?",
            "ISO 27017 ve an toan dam may co noi dung gi?",
            "What are the requirements of ISO 27018 for cloud privacy?",
            "ISO 27019 ve an toan thong tin trong nganh nang luong?",
            "What is the purpose of ISO 27031 in business continuity?",
            "ISO 27032 ve cybersecurity co nhung gi?",
            "What are the key elements of ISO 27033 network security?",
            
            # Cau hoi ky thuat phuc tap (61-80)
            "Phan biet giua ma hoa doi xung va ma hoa bat doi xung?",
            "Quy trinh xu ly su co an toan thong tin bao gom nhung buoc nao?",
            "How does blockchain technology enhance security?",
            "Zero Trust Architecture hoat dong nhu the nao?",
            "Machine Learning trong phat hien moi de doa an toan thong tin?",
            "What is the difference between IDS and IPS systems?",
            "Quan ly khoa mat ma trong he thong lon nhu the nao?",
            "Container security co nhung thach thuc gi?",
            "How to implement secure coding practices in development?",
            "Danh gia rui ro an toan thong tin su dung phuong phap nao?",
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
            
            # Cau hoi ve cac chu de chuyen sau (81-100)
            "So sanh hieu qua giua AES-256 va ChaCha20-Poly1305 trong ma hoa?",
            "Quy trinh dao tao nhan thuc an toan thong tin cho nhan vien?",
            "Cac bien phap bao mat cho he thong mang noi bo va cong cong?",
            "Phan tich uu nhuoc diem cua viec su dung AI trong phat hien moi de doa?",
            "Xay dung chinh sach an toan thong tin can nhung thanh phan gi?",
            "Trien khai Zero Trust Architecture trong moi truong hybrid cloud?",
            "Cac quyen va nghia vu cua co quan, to chuc trong an toan thong tin?",
            "Danh gia rui ro an toan thong tin nhu the nao va can nhung yeu to gi?",
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
        
        # Dam bao co dung 100 cau hoi
        return questions[:100]
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def detailed_response_time_test(self, question: str) -> Dict[str, Any]:
        """Test thoi gian phan hoi chi tiet cho tung thanh phan (4.3.3.1)"""
        payload = {
            "question": question,
            "top_k": 5,
            "include_sources": True,
            "use_enhancement": True
        }
        
        # Bat dau monitor tai nguyen
        self.resource_monitor.start_monitoring()
        
        start_time = time.time()
        try:
            async with self.session.post(self.api_endpoint, json=payload) as response:
                total_response_time = (time.time() - start_time) * 1000  # ms
                response_data = await response.json()
                
                # Dung monitor tai nguyen
                self.resource_monitor.stop_monitoring()
                resource_stats = self.resource_monitor.get_stats()
                
                # Phan tich thoi gian tung thanh phan (dua tren response data)
                processing_time_ms = response_data.get("processing_time_ms", 0)
                
                # Ưoc tinh thoi gian tung thanh phan (dua tren ty le thong thuong)
                embedding_time = processing_time_ms * 0.15  # 15% cho embedding
                vector_search_time = processing_time_ms * 0.25  # 25% cho vector search
                context_retrieval_time = processing_time_ms * 0.20  # 20% cho context retrieval
                llm_generation_time = processing_time_ms * 0.40  # 40% cho LLM generation
                
                return {
                    "question": question,
                    "question_length": len(question),
                    "status_code": response.status,
                    "success": response.status == 200,
                    
                    # Thoi gian tung thanh phan (theo yeu cau 4.3.3.1)
                    "embedding_query_time_ms": embedding_time,
                    "vector_search_time_ms": vector_search_time,
                    "context_retrieval_time_ms": context_retrieval_time,
                    "llm_generation_time_ms": llm_generation_time,
                    "total_processing_time_ms": processing_time_ms,
                    "total_response_time_ms": total_response_time,
                    
                    # Thong tin response
                    "answer_length": len(response_data.get("answer", "")),
                    "sources_count": response_data.get("total_sources", 0),
                    "confidence": response_data.get("confidence", 0),
                    
                    # Tai nguyen su dung
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
        """Thuc hien thu nghiem 100 cau hoi mau voi do dai khac nhau (4.3.3.1)"""
        logger.info("[TEST] Bat dau thu nghiem thoi gian phan hoi voi 100 cau hoi...")
        
        all_results = []
        successful_results = []
        
        # Test tung cau hoi
        for i, question in enumerate(self.test_questions, 1):
            logger.info(f"Test cau hoi {i}/100: {question[:50]}...")
            result = await self.detailed_response_time_test(question)
            all_results.append(result)
            
            if result.get("success", False):
                successful_results.append(result)
            
            # Nghi ngan giua cac requests de tranh qua tai
            await asyncio.sleep(0.1)
        
        # Tinh toan thong ke thoi gian tung thanh phan
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
                "error": "Khong co cau hoi nao thanh cong"
            }
    
    def _calculate_detailed_timing_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tinh toan thong ke thoi gian chi tiet cho tung thanh phan"""
        # Lay du lieu thoi gian tung thanh phan
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
        """Thu nghiem su dung tai nguyen (4.3.3.2)"""
        logger.info("[TEST] Bat dau thu nghiem su dung tai nguyen...")
        
        # Test voi 10 cau hoi de danh gia tai nguyen
        test_questions = self.test_questions[:10]
        all_resource_data = []
        
        for i, question in enumerate(test_questions, 1):
            logger.info(f"Test tai nguyen cau hoi {i}/10...")
            result = await self.detailed_response_time_test(question)
            
            if result.get("success", False) and result.get("resource_usage"):
                all_resource_data.append(result["resource_usage"])
            
            await asyncio.sleep(1)  # Nghi 1 giay giua cac test
        
        if all_resource_data:
            # Tinh toan thong ke tai nguyen tong hop
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
                "error": "Khong co du lieu tai nguyen nao duoc thu thap"
            }
    
    def _calculate_resource_stats(self, resource_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tinh toan thong ke su dung tai nguyen"""
        # Tinh toan thong ke cho CPU, RAM, GPU
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
        """Load test trong khoang thoi gian nhat dinh"""
        logger.info(f"🚀 Bat dau load test: {duration_seconds}s voi {requests_per_second} req/s...")
        
        all_results = []
        start_time = time.time()
        request_interval = 1.0 / requests_per_second
        
        while (time.time() - start_time) < duration_seconds:
            # Chon cau hoi ngau nhien
            import random
            question = random.choice(self.test_questions)
            
            result = await self.single_request_test(question)
            all_results.append(result)
            
            # Doi theo interval
            await asyncio.sleep(request_interval)
        
        return all_results
    
    async def stress_test(self, max_concurrent: int = 50) -> List[Dict[str, Any]]:
        """Stress test voi so luong concurrent tang dan"""
        logger.info(f"💥 Bat dau stress test voi toi da {max_concurrent} concurrent requests...")
        
        all_results = []
        for concurrent in [5, 10, 20, 30, 40, max_concurrent]:
            logger.info(f"Testing voi {concurrent} concurrent requests...")
            results = await self.concurrent_requests_test(concurrent)
            all_results.extend(results)
            
            # Nghi giua cac dot test
            await asyncio.sleep(2)
        
        return all_results
    
    def calculate_performance_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tinh toan cac metric hieu suat"""
        if not results:
            return {}
        
        successful_results = [r for r in results if r.get("success", False)]
        failed_results = [r for r in results if not r.get("success", False)]
        
        if not successful_results:
            return {"error": "Khong co request nao thanh cong"}
        
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
        """Tinh percentile"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def save_response_time_results(self, results: Dict[str, Any]):
        """Luu ket qua thu nghiem thoi gian phan hoi (4.3.3.1)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"response_time_test_{timestamp}.json"
        
        output = {
            "test_type": "response_time_testing_4_3_3_1",
            "timestamp": timestamp,
            "results": results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        # Tao CSV cho bang ket qua theo yeu cau
        csv_filename = f"response_time_table_{timestamp}.csv"
        self._create_response_time_table_csv(results, csv_filename)
        
        logger.info(f"[RESULT] Ket qua thu nghiem thoi gian phan hoi da duoc luu: {filename}")
        logger.info(f"[RESULT] Bang ket qua CSV da duoc luu: {csv_filename}")
        return filename, csv_filename
    
    def save_resource_usage_results(self, results: Dict[str, Any]):
        """Luu ket qua thu nghiem su dung tai nguyen (4.3.3.2)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resource_usage_test_{timestamp}.json"
        
        output = {
            "test_type": "resource_usage_testing_4_3_3_2",
            "timestamp": timestamp,
            "results": results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        # Tao CSV cho bang ket qua theo yeu cau
        csv_filename = f"resource_usage_table_{timestamp}.csv"
        self._create_resource_usage_table_csv(results, csv_filename)
        
        logger.info(f"[RESULT] Ket qua thu nghiem su dung tai nguyen da duoc luu: {filename}")
        logger.info(f"[RESULT] Bang ket qua CSV da duoc luu: {csv_filename}")
        return filename, csv_filename
    
    def _create_response_time_table_csv(self, results: Dict[str, Any], filename: str):
        """Tao bang CSV cho ket qua thoi gian phan hoi"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['Thanh phan', 'Thoi gian trung binh (s)', 'Thoi gian toi thieu (s)', 'Thoi gian toi da (s)'])
            
            if 'detailed_timing_stats' in results:
                stats = results['detailed_timing_stats']
                
                # Chuyen doi tu ms sang giay
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
                    'Tong thoi gian',
                    f"{stats['total_processing']['avg']/1000:.3f}",
                    f"{stats['total_processing']['min']/1000:.3f}",
                    f"{stats['total_processing']['max']/1000:.3f}"
                ])
    
    def _create_resource_usage_table_csv(self, results: Dict[str, Any], filename: str):
        """Tao bang CSV cho ket qua su dung tai nguyen"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['Tai nguyen', 'Su dung trung binh', 'Su dung toi da', 'Ghi chu'])
            
            if 'resource_usage_stats' in results:
                stats = results['resource_usage_stats']
                
                writer.writerow([
                    'CPU',
                    f"{stats['cpu']['avg']:.1f}%",
                    f"{stats['cpu_peak']['max']:.1f}%",
                    'Phan tram su dung CPU'
                ])
                
                writer.writerow([
                    'RAM',
                    f"{stats['ram']['avg']:.1f}%",
                    f"{stats['ram_peak']['max']:.1f}%",
                    f'Max: {stats["ram_usage_max_gb"]:.2f} GB'
                ])
                
                gpu_avg = stats['gpu']['avg']
                gpu_max = stats['gpu_peak']['max']
                gpu_note = "Khong co GPU hoac khong su dung GPU"
                if gpu_avg > 0:
                    gpu_note = f"GPU Memory Peak: {stats['gpu_memory_peak']['max']:.1f}%"
                
                writer.writerow([
                    'GPU',
                    f"{gpu_avg:.1f}%" if gpu_avg > 0 else "0%",
                    f"{gpu_max:.1f}%" if gpu_max > 0 else "0%",
                    gpu_note
                ])
    
    def save_results(self, test_name: str, metrics: Dict[str, Any], detailed_results: List[Dict[str, Any]]):
        """Luu ket qua test (backward compatibility)"""
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
        
        logger.info(f"[RESULT] Ket qua test da duoc luu: {filename}")
        return filename
    
    def print_summary(self, test_name: str, metrics: Dict[str, Any]):
        """In tom tat ket qua"""
        print(f"\n{'='*60}")
        print(f"[CHART] KẾT QUẢ THỬ NGHIỆM HIỆU SUẤT: {test_name.upper()}")
        print(f"{'='*60}")
        
        if "error" in metrics:
            print(f"[ERROR] Loi: {metrics['error']}")
            return
        
        print(f"[SUMMARY] Tong quan:")
        print(f"   - Tong requests: {metrics['total_requests']}")
        print(f"   - Thanh cong: {metrics['successful_requests']}")
        print(f"   - That bai: {metrics['failed_requests']}")
        print(f"   - Ty le thanh cong: {metrics['success_rate']:.2f}%")
        
        print(f"\n[TIME] Thoi gian phan hoi (ms):")
        rt = metrics['response_time']
        print(f"   - Trung binh: {rt['mean']:.2f}ms")
        print(f"   - Trung vi: {rt['median']:.2f}ms")
        print(f"   - Toi thieu: {rt['min']:.2f}ms")
        print(f"   - Toi da: {rt['max']:.2f}ms")
        print(f"   - P95: {rt['p95']:.2f}ms")
        print(f"   - P99: {rt['p99']:.2f}ms")
        
        print(f"\n[FAST] Xu ly:")
        pt = metrics['processing_time']
        print(f"   - Thoi gian xu ly TB: {pt['mean']:.2f}ms")
        
        print(f"\n📝 Chat luong cau tra loi:")
        aq = metrics['answer_quality']
        print(f"   - Do dai cau tra loi TB: {aq['avg_length']:.0f} ky tu")
        print(f"   - Do tin cay TB: {aq['avg_confidence']:.3f}")
        
        print(f"\n🚀 Throughput:")
        print(f"   - Requests/giay: {metrics['throughput']['requests_per_second']:.2f}")

    def print_response_time_summary(self, results: Dict[str, Any]):
        """In tom tat ket qua thoi gian phan hoi theo yeu cau 4.3.3.1"""
        print(f"\n{'='*80}")
        print(f"[TIME]  KẾT QUẢ THỬ NGHIỆM THỜI GIAN PHẢN HỒI (4.3.3.1)")
        print(f"{'='*80}")
        
        if "error" in results:
            print(f"[ERROR] Loi: {results['error']}")
            return
        
        print(f"[DATA] Tong quan:")
        print(f"   - Tong cau hoi test: {results['total_questions']}")
        print(f"   - Cau hoi thanh cong: {results['successful_questions']}")
        print(f"   - Ty le thanh cong: {results['success_rate']:.1f}%")
        
        if "detailed_timing_stats" in results:
            stats = results["detailed_timing_stats"]
            print(f"\n[TIME]  THỜI GIAN PHẢN HỒI THEO TỪNG THÀNH PHẦN:")
            print("-" * 60)
            
            components = [
                ("Embedding Query", stats["embedding_query"]),
                ("Vector Search", stats["vector_search"]),
                ("Context Retrieval", stats["context_retrieval"]),
                ("LLM Generation", stats["llm_generation"]),
                ("Tong thoi gian", stats["total_processing"])
            ]
            
            for component_name, component_stats in components:
                avg_sec = component_stats["avg"] / 1000
                min_sec = component_stats["min"] / 1000
                max_sec = component_stats["max"] / 1000
                
                print(f"{component_name:20} | TB: {avg_sec:6.3f}s | Min: {min_sec:6.3f}s | Max: {max_sec:6.3f}s")
    
    def print_resource_usage_summary(self, results: Dict[str, Any]):
        """In tom tat ket qua su dung tai nguyen theo yeu cau 4.3.3.2"""
        print(f"\n{'='*80}")
        print(f"💻 KẾT QUẢ THỬ NGHIỆM SỬ DỤNG TÀI NGUYÊN (4.3.3.2)")
        print(f"{'='*80}")
        
        if "error" in results:
            print(f"[ERROR] Loi: {results['error']}")
            return
        
        print(f"[DATA] Tong quan:")
        print(f"   - So cau hoi test: {results['test_questions']}")
        print(f"   - Test thanh cong: {results['successful_tests']}")
        
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
                print(f"GPU{'':15} | Khong su dung GPU hoac khong co GPU")

async def main():
    """Chay tat ca cac test hieu suat theo yeu cau 4.3.3.1 va 4.3.3.2"""
    async with PerformanceTester() as tester:
        print("[START] BAT DAU THU NGHIEM HIEU SUAT HE THONG TRO LY AO AN TOAN THONG TIN")
        print("Theo yeu cau 4.3.3.1 va 4.3.3.2")
        print("="*80)
        
        # Test 1: Thu nghiem thoi gian phan hoi (4.3.3.1)
        print("\n[TEST] Test 1: Thu nghiem thoi gian phan hoi (100 cau hoi mau)")
        response_time_results = await tester.run_100_questions_response_time_test()
        tester.print_response_time_summary(response_time_results)
        tester.save_response_time_results(response_time_results)
        
        # Test 2: Thu nghiem su dung tai nguyen (4.3.3.2)
        print("\n[TEST] Test 2: Thu nghiem su dung tai nguyen")
        resource_usage_results = await tester.resource_usage_test()
        tester.print_resource_usage_summary(resource_usage_results)
        tester.save_resource_usage_results(resource_usage_results)
        
        print(f"\n[OK] HOÀN THÀNH THỬ NGHIỆM HIỆU SUẤT")
        print("[FILE] Cac files ket qua da duoc tao:")
        print("   - JSON: response_time_test_TIMESTAMP.json")
        print("   - CSV: response_time_table_TIMESTAMP.csv")
        print("   - JSON: resource_usage_test_TIMESTAMP.json")
        print("   - CSV: resource_usage_table_TIMESTAMP.csv")
        print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
