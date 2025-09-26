#!/usr/bin/env python3
"""
Script demo xuất 100 câu hỏi thành file JSON và CSV (không cần API)
Chỉ tạo cấu trúc dữ liệu mẫu để demo format
"""

import json
import csv
from datetime import datetime
from typing import List, Dict, Any

def get_100_test_questions() -> List[str]:
    """Trích xuất 100 câu hỏi từ test_performance.py"""
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
    
    return questions[:100]

def create_demo_responses(questions: List[str]) -> List[Dict[str, str]]:
    """Tạo câu trả lời mẫu cho demo (không cần API)"""
    demo_responses = []
    
    for i, question in enumerate(questions, 1):
        # Tạo câu trả lời mẫu dựa trên loại câu hỏi
        if "là gì" in question.lower() or "what is" in question.lower():
            response = f"Đây là câu trả lời mẫu cho câu hỏi số {i}. Đây là định nghĩa cơ bản về chủ đề được hỏi trong câu hỏi."
        elif "luật" in question.lower() or "nghị định" in question.lower() or "thông tư" in question.lower():
            response = f"Đây là câu trả lời mẫu về luật pháp Việt Nam cho câu hỏi số {i}. Nội dung này liên quan đến các quy định pháp luật về an toàn thông tin."
        elif "iso" in question.lower() or "framework" in question.lower():
            response = f"Đây là câu trả lời mẫu về tiêu chuẩn quốc tế cho câu hỏi số {i}. Nội dung này liên quan đến các framework và tiêu chuẩn quốc tế về an toàn thông tin."
        elif "how to" in question.lower() or "như thế nào" in question.lower():
            response = f"Đây là câu trả lời mẫu về hướng dẫn thực hiện cho câu hỏi số {i}. Nội dung này cung cấp các bước thực hiện và phương pháp cụ thể."
        else:
            response = f"Đây là câu trả lời mẫu tổng quát cho câu hỏi số {i}. Nội dung này cung cấp thông tin chi tiết về chủ đề được hỏi."
        
        demo_responses.append({
            "query": question,
            "response": response
        })
    
    return demo_responses

def save_to_json(data: List[Dict[str, str]], filename: str = None) -> str:
    """Lưu dữ liệu vào file JSON"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"demo_questions_responses_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Đã lưu file JSON: {filename}")
    return filename

def save_to_csv(data: List[Dict[str, str]], filename: str = None) -> str:
    """Lưu dữ liệu vào file CSV"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"demo_questions_responses_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Header
        writer.writerow(['query', 'response'])
        
        # Dữ liệu
        for item in data:
            writer.writerow([
                item["query"],
                item["response"]
            ])
    
    print(f"✅ Đã lưu file CSV: {filename}")
    return filename

def print_sample_data(data: List[Dict[str, str]], num_samples: int = 3):
    """In mẫu dữ liệu"""
    print(f"\n📋 MẪU DỮ LIỆU (hiển thị {num_samples} mẫu đầu tiên):")
    print("-" * 80)
    
    for i, item in enumerate(data[:num_samples], 1):
        print(f"\n{i}. QUERY: {item['query']}")
        print(f"   RESPONSE: {item['response'][:100]}...")

def main():
    """Hàm chính để chạy script demo"""
    print("🚀 BẮT ĐẦU TẠO DỮ LIỆU DEMO")
    print("="*60)
    
    # Lấy 100 câu hỏi
    questions = get_100_test_questions()
    print(f"📝 Đã lấy {len(questions)} câu hỏi từ test_performance.py")
    
    # Tạo câu trả lời mẫu
    demo_data = create_demo_responses(questions)
    print(f"💡 Đã tạo {len(demo_data)} câu trả lời mẫu")
    
    # In mẫu dữ liệu
    print_sample_data(demo_data, 3)
    
    # Lưu vào JSON
    json_filename = save_to_json(demo_data)
    
    # Lưu vào CSV
    csv_filename = save_to_csv(demo_data)
    
    print(f"\n{'='*60}")
    print(f"✅ HOÀN THÀNH TẠO DỮ LIỆU DEMO")
    print(f"{'='*60}")
    print(f"📄 File JSON: {json_filename}")
    print(f"📄 File CSV: {csv_filename}")
    print(f"\n📋 Format dữ liệu:")
    print(f"   JSON: [{{query: '...', response: '...'}}, ...]")
    print(f"   CSV: query,response")
    print(f"\n💡 Lưu ý: Đây là dữ liệu mẫu. Để có câu trả lời thực từ API,")
    print(f"   hãy chạy script 'export_questions_responses.py' khi backend đang hoạt động.")

if __name__ == "__main__":
    main()
