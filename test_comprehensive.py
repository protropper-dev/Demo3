#!/usr/bin/env python3
"""
Comprehensive Testing Script cho Hệ thống Trợ lý Ảo An toàn Thông tin
Chạy tất cả các loại thử nghiệm: Performance, Accuracy, Response Quality
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List
import logging
import os
import sys

# Import các module test
from test_performance import PerformanceTester
from test_accuracy import AccuracyTester
from test_response_quality import ResponseQualityTester

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive_test_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.start_time = None
        self.end_time = None
        self.all_results = {}
        
    async def run_performance_tests(self) -> Dict[str, Any]:
        """Chạy các test hiệu suất"""
        logger.info("🚀 Bắt đầu Performance Testing...")
        
        async with PerformanceTester(self.base_url) as tester:
            # Test 1: Single Request
            single_result = await tester.single_request_test("An toàn thông tin là gì?")
            single_metrics = tester.calculate_performance_metrics([single_result])
            
            # Test 2: Concurrent Requests
            concurrent_results = await tester.concurrent_requests_test(10)
            concurrent_metrics = tester.calculate_performance_metrics(concurrent_results)
            
            # Test 3: Load Test (ngắn hơn cho comprehensive test)
            load_results = await tester.load_test(duration_seconds=20, requests_per_second=2)
            load_metrics = tester.calculate_performance_metrics(load_results)
            
            # Test 4: Stress Test (nhẹ hơn)
            stress_results = await tester.stress_test(max_concurrent=20)
            stress_metrics = tester.calculate_performance_metrics(stress_results)
            
            performance_results = {
                "single_request": {
                    "metrics": single_metrics,
                    "results": [single_result]
                },
                "concurrent_requests": {
                    "metrics": concurrent_metrics,
                    "results": concurrent_results
                },
                "load_test": {
                    "metrics": load_metrics,
                    "results": load_results
                },
                "stress_test": {
                    "metrics": stress_metrics,
                    "results": stress_results
                }
            }
            
            logger.info("✅ Performance Testing hoàn thành")
            return performance_results
    
    async def run_accuracy_tests(self) -> Dict[str, Any]:
        """Chạy các test độ chính xác"""
        logger.info("🎯 Bắt đầu Accuracy Testing...")
        
        async with AccuracyTester(self.base_url) as tester:
            # Chạy tất cả accuracy test cases
            results = await tester.run_all_tests()
            metrics = tester.calculate_overall_metrics(results)
            
            accuracy_results = {
                "metrics": metrics,
                "results": results
            }
            
            logger.info("✅ Accuracy Testing hoàn thành")
            return accuracy_results
    
    async def run_response_quality_tests(self) -> Dict[str, Any]:
        """Chạy các test chất lượng phản hồi"""
        logger.info("📝 Bắt đầu Response Quality Testing...")
        
        async with ResponseQualityTester(self.base_url) as tester:
            # Chạy tất cả quality test cases
            results = await tester.run_all_quality_tests()
            metrics = tester.calculate_quality_metrics(results)
            
            quality_results = {
                "metrics": metrics,
                "results": results
            }
            
            logger.info("✅ Response Quality Testing hoàn thành")
            return quality_results
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Chạy tất cả các loại test"""
        self.start_time = datetime.now()
        logger.info("🔬 BẮT ĐẦU THỬ NGHIỆM TOÀN DIỆN HỆ THỐNG TRỢ LÝ ẢO AN TOÀN THÔNG TIN")
        logger.info("="*80)
        
        all_results = {}
        
        try:
            # 1. Performance Testing
            logger.info("\n📊 PHẦN 1: THỬ NGHIỆM HIỆU SUẤT")
            logger.info("-" * 50)
            all_results["performance"] = await self.run_performance_tests()
            
            # 2. Accuracy Testing
            logger.info("\n🎯 PHẦN 2: THỬ NGHIỆM ĐỘ CHÍNH XÁC")
            logger.info("-" * 50)
            all_results["accuracy"] = await self.run_accuracy_tests()
            
            # 3. Response Quality Testing
            logger.info("\n📝 PHẦN 3: THỬ NGHIỆM CHẤT LƯỢNG PHẢN HỒI")
            logger.info("-" * 50)
            all_results["response_quality"] = await self.run_response_quality_tests()
            
        except Exception as e:
            logger.error(f"❌ Lỗi trong quá trình test: {e}")
            all_results["error"] = str(e)
        
        self.end_time = datetime.now()
        all_results["test_summary"] = self._generate_test_summary(all_results)
        
        return all_results
    
    def _generate_test_summary(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo tóm tắt tổng thể của tất cả các test"""
        summary = {
            "test_start_time": self.start_time.isoformat() if self.start_time else None,
            "test_end_time": self.end_time.isoformat() if self.end_time else None,
            "total_duration_minutes": None,
            "overall_status": "completed",
            "test_categories": {},
            "overall_score": 0.0,
            "recommendations": []
        }
        
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
            summary["total_duration_minutes"] = round(duration / 60, 2)
        
        # Tính điểm tổng thể
        scores = []
        
        # Performance scores
        if "performance" in all_results:
            perf = all_results["performance"]
            perf_score = self._calculate_performance_score(perf)
            summary["test_categories"]["performance"] = {
                "status": "completed",
                "score": perf_score,
                "details": {
                    "avg_response_time_ms": self._get_avg_response_time(perf),
                    "success_rate": self._get_success_rate(perf),
                    "throughput_rps": self._get_throughput(perf)
                }
            }
            scores.append(perf_score)
        
        # Accuracy scores
        if "accuracy" in all_results:
            acc = all_results["accuracy"]
            acc_score = acc["metrics"].get("overall_scores", {}).get("mean", 0.0)
            summary["test_categories"]["accuracy"] = {
                "status": "completed",
                "score": acc_score,
                "details": {
                    "success_rate": acc["metrics"].get("success_rate", 0.0),
                    "keyword_coverage": acc["metrics"].get("component_scores", {}).get("keyword_coverage", {}).get("mean", 0.0),
                    "technical_accuracy": acc["metrics"].get("component_scores", {}).get("technical_accuracy", {}).get("mean", 0.0)
                }
            }
            scores.append(acc_score)
        
        # Response Quality scores
        if "response_quality" in all_results:
            qual = all_results["response_quality"]
            qual_score = qual["metrics"].get("overall_quality_scores", {}).get("mean", 0.0)
            summary["test_categories"]["response_quality"] = {
                "status": "completed",
                "score": qual_score,
                "details": {
                    "success_rate": qual["metrics"].get("success_rate", 0.0),
                    "coherence": qual["metrics"].get("component_scores", {}).get("coherence", {}).get("mean", 0.0),
                    "helpfulness": qual["metrics"].get("component_scores", {}).get("helpfulness", {}).get("mean", 0.0)
                }
            }
            scores.append(qual_score)
        
        # Tính điểm tổng thể
        if scores:
            summary["overall_score"] = sum(scores) / len(scores)
        
        # Tạo khuyến nghị
        summary["recommendations"] = self._generate_recommendations(summary)
        
        return summary
    
    def _calculate_performance_score(self, performance_results: Dict[str, Any]) -> float:
        """Tính điểm hiệu suất tổng thể"""
        scores = []
        
        # Điểm dựa trên response time (càng nhanh càng tốt)
        for test_type in ["single_request", "concurrent_requests", "load_test"]:
            if test_type in performance_results:
                avg_response_time = performance_results[test_type]["metrics"].get("response_time", {}).get("mean", 0)
                # Chuyển đổi response time thành điểm (dưới 2s = 1.0, trên 10s = 0.0)
                response_score = max(0, 1 - (avg_response_time - 2000) / 8000)
                scores.append(response_score)
        
        # Điểm dựa trên success rate
        for test_type in performance_results:
            success_rate = performance_results[test_type]["metrics"].get("success_rate", 0)
            scores.append(success_rate / 100)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _get_avg_response_time(self, performance_results: Dict[str, Any]) -> float:
        """Lấy thời gian phản hồi trung bình"""
        times = []
        for test_type in performance_results:
            response_time = performance_results[test_type]["metrics"].get("response_time", {}).get("mean", 0)
            if response_time > 0:
                times.append(response_time)
        return sum(times) / len(times) if times else 0.0
    
    def _get_success_rate(self, performance_results: Dict[str, Any]) -> float:
        """Lấy tỷ lệ thành công trung bình"""
        rates = []
        for test_type in performance_results:
            success_rate = performance_results[test_type]["metrics"].get("success_rate", 0)
            rates.append(success_rate)
        return sum(rates) / len(rates) if rates else 0.0
    
    def _get_throughput(self, performance_results: Dict[str, Any]) -> float:
        """Lấy throughput trung bình"""
        throughputs = []
        for test_type in performance_results:
            throughput = performance_results[test_type]["metrics"].get("throughput", {}).get("requests_per_second", 0)
            if throughput > 0:
                throughputs.append(throughput)
        return sum(throughputs) / len(throughputs) if throughputs else 0.0
    
    def _generate_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """Tạo các khuyến nghị cải thiện"""
        recommendations = []
        
        overall_score = summary.get("overall_score", 0.0)
        
        if overall_score < 0.6:
            recommendations.append("⚠️ Điểm tổng thể thấp - Cần cải thiện toàn diện hệ thống")
        elif overall_score < 0.8:
            recommendations.append("✅ Điểm tổng thể khá - Có thể cải thiện một số khía cạnh")
        else:
            recommendations.append("🎉 Điểm tổng thể tốt - Hệ thống hoạt động ổn định")
        
        # Khuyến nghị cụ thể cho từng loại test
        categories = summary.get("test_categories", {})
        
        if "performance" in categories:
            perf_details = categories["performance"]["details"]
            if perf_details["avg_response_time_ms"] > 5000:
                recommendations.append("🚀 Cần tối ưu hóa hiệu suất - thời gian phản hồi quá chậm")
            if perf_details["success_rate"] < 95:
                recommendations.append("🔧 Cần cải thiện độ ổn định - tỷ lệ thành công thấp")
        
        if "accuracy" in categories:
            acc_details = categories["accuracy"]["details"]
            if acc_details["keyword_coverage"] < 0.7:
                recommendations.append("🎯 Cần cải thiện độ chính xác - tỷ lệ bao phủ từ khóa thấp")
            if acc_details["technical_accuracy"] < 0.6:
                recommendations.append("📚 Cần cải thiện kiến thức kỹ thuật trong knowledge base")
        
        if "response_quality" in categories:
            qual_details = categories["response_quality"]["details"]
            if qual_details["coherence"] < 0.7:
                recommendations.append("📝 Cần cải thiện tính mạch lạc của câu trả lời")
            if qual_details["helpfulness"] < 0.6:
                recommendations.append("💡 Cần cải thiện tính hữu ích của câu trả lời")
        
        return recommendations
    
    def save_comprehensive_results(self, all_results: Dict[str, Any]):
        """Lưu kết quả tổng hợp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_test_results_{timestamp}.json"
        
        output = {
            "test_type": "comprehensive_testing",
            "timestamp": timestamp,
            "system_info": {
                "base_url": self.base_url,
                "test_duration_minutes": all_results.get("test_summary", {}).get("total_duration_minutes", 0)
            },
            "results": all_results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 Kết quả comprehensive test đã được lưu: {filename}")
        return filename
    
    def print_comprehensive_summary(self, all_results: Dict[str, Any]):
        """In tóm tắt tổng hợp"""
        print(f"\n{'='*80}")
        print(f"📊 BÁO CÁO TỔNG HỢP THỬ NGHIỆM HỆ THỐNG TRỢ LÝ ẢO AN TOÀN THÔNG TIN")
        print(f"{'='*80}")
        
        summary = all_results.get("test_summary", {})
        
        # Thông tin chung
        print(f"\n⏱️  Thông tin chung:")
        print(f"   • Thời gian bắt đầu: {summary.get('test_start_time', 'N/A')}")
        print(f"   • Thời gian kết thúc: {summary.get('test_end_time', 'N/A')}")
        print(f"   • Tổng thời gian: {summary.get('total_duration_minutes', 0):.2f} phút")
        print(f"   • Trạng thái: {summary.get('overall_status', 'unknown').upper()}")
        
        # Điểm tổng thể
        overall_score = summary.get("overall_score", 0.0)
        print(f"\n🏆 ĐIỂM TỔNG THỂ: {overall_score:.3f}/1.0")
        
        if overall_score >= 0.8:
            print("   🎉 XUẤT SẮC - Hệ thống hoạt động rất tốt")
        elif overall_score >= 0.6:
            print("   ✅ TỐT - Hệ thống hoạt động ổn định")
        elif overall_score >= 0.4:
            print("   ⚠️  TRUNG BÌNH - Cần cải thiện")
        else:
            print("   ❌ KÉM - Cần cải thiện đáng kể")
        
        # Chi tiết từng loại test
        categories = summary.get("test_categories", {})
        
        print(f"\n📊 CHI TIẾT TỪNG LOẠI THỬ NGHIỆM:")
        print("-" * 60)
        
        if "performance" in categories:
            perf = categories["performance"]
            print(f"\n🚀 HIỆU SUẤT:")
            print(f"   • Điểm: {perf['score']:.3f}/1.0")
            details = perf["details"]
            print(f"   • Thời gian phản hồi TB: {details['avg_response_time_ms']:.0f}ms")
            print(f"   • Tỷ lệ thành công: {details['success_rate']:.1f}%")
            print(f"   • Throughput: {details['throughput_rps']:.2f} req/s")
        
        if "accuracy" in categories:
            acc = categories["accuracy"]
            print(f"\n🎯 ĐỘ CHÍNH XÁC:")
            print(f"   • Điểm: {acc['score']:.3f}/1.0")
            details = acc["details"]
            print(f"   • Tỷ lệ thành công: {details['success_rate']:.1f}%")
            print(f"   • Bao phủ từ khóa: {details['keyword_coverage']:.3f}")
            print(f"   • Chính xác kỹ thuật: {details['technical_accuracy']:.3f}")
        
        if "response_quality" in categories:
            qual = categories["response_quality"]
            print(f"\n📝 CHẤT LƯỢNG PHẢN HỒI:")
            print(f"   • Điểm: {qual['score']:.3f}/1.0")
            details = qual["details"]
            print(f"   • Tỷ lệ thành công: {details['success_rate']:.1f}%")
            print(f"   • Tính mạch lạc: {details['coherence']:.3f}")
            print(f"   • Tính hữu ích: {details['helpfulness']:.3f}")
        
        # Khuyến nghị
        recommendations = summary.get("recommendations", [])
        if recommendations:
            print(f"\n💡 KHUYẾN NGHỊ CẢI THIỆN:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        print(f"\n{'='*80}")
        print("✅ HOÀN THÀNH THỬ NGHIỆM TOÀN DIỆN")
        print("="*80)

async def main():
    """Chạy comprehensive testing"""
    # Kiểm tra xem server có đang chạy không
    base_url = "http://localhost:8000"
    
    print("🔍 Kiểm tra kết nối đến server...")
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/health", timeout=5) as response:
                if response.status == 200:
                    print("✅ Server đang hoạt động")
                else:
                    print(f"⚠️ Server trả về status {response.status}")
    except Exception as e:
        print(f"❌ Không thể kết nối đến server: {e}")
        print("💡 Hãy đảm bảo backend server đang chạy trên http://localhost:8000")
        return
    
    # Chạy comprehensive test
    tester = ComprehensiveTester(base_url)
    
    try:
        all_results = await tester.run_all_tests()
        
        # In kết quả
        tester.print_comprehensive_summary(all_results)
        
        # Lưu kết quả
        filename = tester.save_comprehensive_results(all_results)
        
        print(f"\n📁 Tất cả kết quả chi tiết đã được lưu trong: {filename}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test bị dừng bởi người dùng")
    except Exception as e:
        logger.error(f"❌ Lỗi trong comprehensive test: {e}")
        print(f"❌ Có lỗi xảy ra: {e}")

if __name__ == "__main__":
    asyncio.run(main())
