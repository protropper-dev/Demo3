#!/usr/bin/env python3
"""
Accuracy Testing Script cho He thong Tro ly Ảo An toan Thong tin
Danh gia do chinh xac theo yeu cau 4.3.4.1, 4.3.4.2, 4.3.4.3
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

# Cau hinh logging
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
    """Test case cho danh gia boi chuyen gia (4.3.4.1)"""
    question: str
    language: str  # "vietnamese", "english", "mixed"
    category: str  # luat, english, vietnamese, technical
    expected_keywords: List[str]
    expert_notes: str

@dataclass
class SearchAccuracyCase:
    """Test case cho danh gia do chinh xac tim kiem (4.3.4.2)"""
    question: str
    expected_answer: str
    expected_sources: List[str]  # Cac nguon tai lieu mong doi
    language: str
    category: str

@dataclass
class MultilingualCase:
    """Test case cho thu nghiem da ngon ngu (4.3.4.3)"""
    question: str
    language: str  # "vietnamese", "english", "mixed"
    expected_response_language: str
    category: str

class AccuracyTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/api/v1/rag/query"
        self.session = None
        
        # Tao bo test cases cho tung loai danh gia
        self.expert_evaluation_cases = self._create_expert_evaluation_cases()
        self.search_accuracy_cases = self._create_search_accuracy_cases()
        self.multilingual_cases = self._create_multilingual_cases()
    
    def _create_expert_evaluation_cases(self) -> List[ExpertEvaluationCase]:
        """Tao 50 cau hoi chuan cho danh gia boi chuyen gia (4.3.4.1)"""
        return [
            # Cau hoi co ban ve an toan thong tin (10 cau)
            ExpertEvaluationCase(
                question="An toan thong tin la gi?",
                language="vietnamese",
                category="general",
                expected_keywords=["an toan", "thong tin", "bao ve", "bi mat", "toan ven", "san sang"],
                expert_notes="Cau hoi co ban, can giai thich khai niem CIA triad"
            ),
            ExpertEvaluationCase(
                question="Cac nguyen tac co ban cua an toan thong tin?",
                language="vietnamese",
                category="general",
                expected_keywords=["nguyen tac", "bao mat", "toan ven", "san sang", "xac thuc", "phan quyen"],
                expert_notes="Can de cap den cac nguyen tac cot loi"
            ),
            ExpertEvaluationCase(
                question="What is information security?",
                language="english",
                category="general",
                expected_keywords=["information", "security", "protection", "confidentiality", "integrity", "availability"],
                expert_notes="Basic concept in English, should explain CIA triad"
            ),
            ExpertEvaluationCase(
                question="Phan loai cac moi de doa an toan thong tin?",
                language="vietnamese",
                category="technical",
                expected_keywords=["moi de doa", "phan loai", "malware", "phishing", "hack", "noi bo", "ben ngoai"],
                expert_notes="Can phan loai ro rang cac loai moi de doa"
            ),
            ExpertEvaluationCase(
                question="Mat khau manh co dac diem gi?",
                language="vietnamese",
                category="technical",
                expected_keywords=["mat khau", "manh", "do dai", "ky tu", "phuc tap", "bao mat"],
                expert_notes="Can dua ra tieu chi cu the cho mat khau manh"
            ),
            ExpertEvaluationCase(
                question="Firewall la gi va hoat dong nhu the nao?",
                language="vietnamese",
                category="technical",
                expected_keywords=["firewall", "tuong lua", "loc", "goi tin", "port", "protocol"],
                expert_notes="Can giai thich co che hoat dong cua firewall"
            ),
            ExpertEvaluationCase(
                question="Phishing la gi va cach phong chong?",
                language="vietnamese",
                category="technical",
                expected_keywords=["phishing", "lua dao", "email", "website", "gia mao", "phong chong"],
                expert_notes="Can dua ra cac bien phap phong chong cu the"
            ),
            ExpertEvaluationCase(
                question="Ransomware la gi?",
                language="vietnamese",
                category="technical",
                expected_keywords=["ransomware", "ma doc", "ma hoa", "tong tien", "khoi phuc", "sao luu"],
                expert_notes="Can giai thich co che hoat dong va tac hai"
            ),
            ExpertEvaluationCase(
                question="VPN la gi va tai sao can su dung?",
                language="vietnamese",
                category="technical",
                expected_keywords=["VPN", "mang rieng ao", "ma hoa", "tunnel", "bao mat", "truy cap"],
                expert_notes="Can giai thich loi ich bao mat cua VPN"
            ),
            ExpertEvaluationCase(
                question="Two-factor authentication la gi?",
                language="english",
                category="technical",
                expected_keywords=["two-factor", "authentication", "2FA", "verification", "security", "login"],
                expert_notes="Should explain the concept and benefits of 2FA"
            ),
            
            # Cau hoi ve luat phap Viet Nam (15 cau)
            ExpertEvaluationCase(
                question="Luat An toan thong tin so 86/2015/QH13 quy dinh gi?",
                language="vietnamese",
                category="luat",
                expected_keywords=["86/2015", "luat", "an toan thong tin", "quy dinh", "co quan", "to chuc"],
                expert_notes="Can de cap den cac quy dinh chinh cua luat"
            ),
            ExpertEvaluationCase(
                question="Nghi dinh 53/2022/ND-CP ve an toan thong tin co noi dung gi?",
                language="vietnamese",
                category="luat",
                expected_keywords=["53/2022", "nghi dinh", "an toan thong tin", "quy dinh", "thuc hien"],
                expert_notes="Can tom tat noi dung chinh cua nghi dinh"
            ),
            ExpertEvaluationCase(
                question="Cac quyen va nghia vu cua co quan, to chuc trong an toan thong tin?",
                language="vietnamese",
                category="luat",
                expected_keywords=["quyen", "nghia vu", "co quan", "to chuc", "an toan thong tin", "luat"],
                expert_notes="Can liet ke cu the quyen va nghia vu"
            ),
            ExpertEvaluationCase(
                question="Quy dinh ve bao cao su co an toan thong tin theo luat Viet Nam?",
                language="vietnamese",
                category="luat",
                expected_keywords=["bao cao", "su co", "an toan thong tin", "thoi han", "co quan", "quy dinh"],
                expert_notes="Can neu ro quy trinh va thoi han bao cao"
            ),
            ExpertEvaluationCase(
                question="Xu phat vi pham an toan thong tin theo luat hien hanh?",
                language="vietnamese",
                category="luat",
                expected_keywords=["xu phat", "vi pham", "an toan thong tin", "muc phat", "hinh thuc"],
                expert_notes="Can neu cac muc phat va hinh thuc xu ly"
            ),
            ExpertEvaluationCase(
                question="Thong tu 20/2017/TT-BTTTT quy dinh gi ve an toan thong tin?",
                language="vietnamese",
                category="luat",
                expected_keywords=["20/2017", "thong tu", "BTTTT", "an toan thong tin", "quy dinh"],
                expert_notes="Can tom tat noi dung thong tu"
            ),
            ExpertEvaluationCase(
                question="Quy dinh ve phan loai thong tin mat theo luat Viet Nam?",
                language="vietnamese",
                category="luat",
                expected_keywords=["phan loai", "thong tin mat", "muc do", "bi mat", "quoc gia"],
                expert_notes="Can neu cac muc do phan loai thong tin"
            ),
            ExpertEvaluationCase(
                question="Nghi dinh 142/2016/ND-CP ve an toan thong tin?",
                language="vietnamese",
                category="luat",
                expected_keywords=["142/2016", "nghi dinh", "an toan thong tin", "quy dinh"],
                expert_notes="Can tom tat noi dung nghi dinh"
            ),
            ExpertEvaluationCase(
                question="Quy dinh ve danh gia rui ro an toan thong tin?",
                language="vietnamese",
                category="luat",
                expected_keywords=["danh gia", "rui ro", "an toan thong tin", "quy trinh", "phuong phap"],
                expert_notes="Can neu quy trinh danh gia rui ro"
            ),
            ExpertEvaluationCase(
                question="Quy dinh ve chung nhan an toan thong tin?",
                language="vietnamese",
                category="luat",
                expected_keywords=["chung nhan", "an toan thong tin", "tieu chuan", "co quan", "tham quyen"],
                expert_notes="Can neu quy trinh va co quan co tham quyen"
            ),
            ExpertEvaluationCase(
                question="Luat Mang luoi thong tin quoc gia co quy dinh gi ve an toan?",
                language="vietnamese",
                category="luat",
                expected_keywords=["luat", "mang luoi", "thong tin quoc gia", "an toan", "quy dinh"],
                expert_notes="Can tom tat cac quy dinh ve an toan"
            ),
            ExpertEvaluationCase(
                question="Quy dinh ve bao ve du lieu ca nhan theo luat Viet Nam?",
                language="vietnamese",
                category="luat",
                expected_keywords=["bao ve", "du lieu ca nhan", "quyen rieng tu", "xu ly", "luu tru"],
                expert_notes="Can neu cac quy dinh bao ve du lieu ca nhan"
            ),
            ExpertEvaluationCase(
                question="Quy dinh ve giam sat an toan thong tin?",
                language="vietnamese",
                category="luat",
                expected_keywords=["giam sat", "an toan thong tin", "theo doi", "kiem tra", "danh gia"],
                expert_notes="Can neu cac hoat dong giam sat"
            ),
            ExpertEvaluationCase(
                question="Quy dinh ve dao tao nhan thuc an toan thong tin?",
                language="vietnamese",
                category="luat",
                expected_keywords=["dao tao", "nhan thuc", "an toan thong tin", "can bo", "nhan vien"],
                expert_notes="Can neu quy dinh ve dao tao nhan thuc"
            ),
            ExpertEvaluationCase(
                question="Quy dinh ve ung pho su co an toan thong tin?",
                language="vietnamese",
                category="luat",
                expected_keywords=["ung pho", "su co", "an toan thong tin", "ke hoach", "xu ly"],
                expert_notes="Can neu quy trinh ung pho su co"
            ),
            
            # Cau hoi ve tieu chuan quoc te (15 cau)
            ExpertEvaluationCase(
                question="ISO 27001 co nhung yeu cau nao?",
                language="vietnamese",
                category="english",
                expected_keywords=["ISO", "27001", "yeu cau", "quan ly", "an toan thong tin", "chinh sach"],
                expert_notes="Can liet ke cac yeu cau chinh cua ISO 27001"
            ),
            ExpertEvaluationCase(
                question="What are the core functions of NIST Framework?",
                language="english",
                category="english",
                expected_keywords=["NIST", "framework", "identify", "protect", "detect", "respond", "recover"],
                expert_notes="Should list all 5 core functions"
            ),
            ExpertEvaluationCase(
                question="ISO 27002 co nhung bien phap bao mat nao?",
                language="vietnamese",
                category="english",
                expected_keywords=["ISO", "27002", "bien phap", "bao mat", "kiem soat", "thuc hien"],
                expert_notes="Can neu cac nhom bien phap bao mat chinh"
            ),
            ExpertEvaluationCase(
                question="COBIT framework la gi?",
                language="english",
                category="english",
                expected_keywords=["COBIT", "framework", "governance", "management", "IT", "control"],
                expert_notes="Should explain COBIT framework concept"
            ),
            ExpertEvaluationCase(
                question="PCI DSS co nhung yeu cau gi?",
                language="vietnamese",
                category="english",
                expected_keywords=["PCI", "DSS", "thanh toan", "the", "bao mat", "yeu cau"],
                expert_notes="Can neu cac yeu cau chinh cua PCI DSS"
            ),
            ExpertEvaluationCase(
                question="GDPR co nhung nguyen tac nao?",
                language="vietnamese",
                category="english",
                expected_keywords=["GDPR", "du lieu ca nhan", "nguyen tac", "quyen", "bao ve"],
                expert_notes="Can neu cac nguyen tac chinh cua GDPR"
            ),
            ExpertEvaluationCase(
                question="What is OWASP Top 10?",
                language="english",
                category="english",
                expected_keywords=["OWASP", "top 10", "vulnerabilities", "web", "application", "security"],
                expert_notes="Should list the main vulnerabilities"
            ),
            ExpertEvaluationCase(
                question="ISO 22301 ve quan ly khung hoang co noi dung gi?",
                language="vietnamese",
                category="english",
                expected_keywords=["ISO", "22301", "quan ly", "khung hoang", "ke hoach", "phuc hoi"],
                expert_notes="Can tom tat noi dung chinh cua ISO 22301"
            ),
            ExpertEvaluationCase(
                question="What is SOC 2 compliance?",
                language="english",
                category="english",
                expected_keywords=["SOC", "2", "compliance", "audit", "security", "availability"],
                expert_notes="Should explain SOC 2 requirements"
            ),
            ExpertEvaluationCase(
                question="ITIL co nhung quy trinh nao ve an toan thong tin?",
                language="vietnamese",
                category="english",
                expected_keywords=["ITIL", "quy trinh", "an toan thong tin", "quan ly", "dich vu"],
                expert_notes="Can neu cac quy trinh lien quan den an toan"
            ),
            ExpertEvaluationCase(
                question="ISO 31000 ve quan ly rui ro co noi dung gi?",
                language="vietnamese",
                category="english",
                expected_keywords=["ISO", "31000", "quan ly", "rui ro", "nguyen tac", "khung"],
                expert_notes="Can tom tat noi dung ISO 31000"
            ),
            ExpertEvaluationCase(
                question="What are the key principles of CIS Controls?",
                language="english",
                category="english",
                expected_keywords=["CIS", "controls", "cybersecurity", "principles", "implementation"],
                expert_notes="Should list key CIS Controls principles"
            ),
            ExpertEvaluationCase(
                question="ISO 27035 ve quan ly su co an toan thong tin?",
                language="vietnamese",
                category="english",
                expected_keywords=["ISO", "27035", "quan ly", "su co", "an toan thong tin", "quy trinh"],
                expert_notes="Can tom tat noi dung ISO 27035"
            ),
            ExpertEvaluationCase(
                question="What is the difference between ISO 27001 and ISO 27002?",
                language="english",
                category="english",
                expected_keywords=["ISO", "27001", "27002", "difference", "management", "controls"],
                expert_notes="Should clearly explain the differences"
            ),
            ExpertEvaluationCase(
                question="ISO 27017 ve an toan dam may co noi dung gi?",
                language="vietnamese",
                category="english",
                expected_keywords=["ISO", "27017", "an toan", "dam may", "cloud", "bao mat"],
                expert_notes="Can tom tat noi dung ISO 27017"
            ),
            
            # Cau hoi ky thuat phuc tap (10 cau)
            ExpertEvaluationCase(
                question="Phan biet giua ma hoa doi xung va ma hoa bat doi xung?",
                language="vietnamese",
                category="technical",
                expected_keywords=["ma hoa", "doi xung", "bat doi xung", "khoa", "AES", "RSA", "khac nhau"],
                expert_notes="Can so sanh chi tiet hai loai ma hoa"
            ),
            ExpertEvaluationCase(
                question="Quy trinh xu ly su co an toan thong tin bao gom nhung buoc nao?",
                language="vietnamese",
                category="technical",
                expected_keywords=["quy trinh", "xu ly", "su co", "buoc", "phat hien", "phan tich", "khac phuc"],
                expert_notes="Can neu cac buoc cu the trong quy trinh"
            ),
            ExpertEvaluationCase(
                question="How does blockchain technology enhance security?",
                language="english",
                category="technical",
                expected_keywords=["blockchain", "technology", "security", "cryptography", "decentralized", "immutable"],
                expert_notes="Should explain blockchain security benefits"
            ),
            ExpertEvaluationCase(
                question="Zero Trust Architecture hoat dong nhu the nao?",
                language="vietnamese",
                category="technical",
                expected_keywords=["zero trust", "kien truc", "khong tin tuong", "xac thuc", "phan quyen", "mang"],
                expert_notes="Can giai thich nguyen ly va cach hoat dong"
            ),
            ExpertEvaluationCase(
                question="Machine Learning trong phat hien moi de doa an toan thong tin?",
                language="vietnamese",
                category="technical",
                expected_keywords=["machine learning", "phat hien", "moi de doa", "AI", "thuat toan", "phan tich"],
                expert_notes="Can neu ung dung va loi ich cua ML"
            ),
            ExpertEvaluationCase(
                question="What is the difference between IDS and IPS?",
                language="english",
                category="technical",
                expected_keywords=["IDS", "IPS", "intrusion", "detection", "prevention", "system"],
                expert_notes="Should clearly differentiate IDS and IPS"
            ),
            ExpertEvaluationCase(
                question="Quan ly khoa mat ma trong he thong lon nhu the nao?",
                language="vietnamese",
                category="technical",
                expected_keywords=["quan ly", "khoa", "mat ma", "he thong", "PKI", "HSM", "luu tru"],
                expert_notes="Can neu cac phuong phap quan ly khoa"
            ),
            ExpertEvaluationCase(
                question="Container security co nhung thach thuc gi?",
                language="vietnamese",
                category="technical",
                expected_keywords=["container", "security", "bao mat", "Docker", "Kubernetes", "thach thuc"],
                expert_notes="Can neu cac van de bao mat cua container"
            ),
            ExpertEvaluationCase(
                question="How to implement secure coding practices?",
                language="english",
                category="technical",
                expected_keywords=["secure", "coding", "practices", "development", "vulnerabilities", "prevention"],
                expert_notes="Should list key secure coding practices"
            ),
            ExpertEvaluationCase(
                question="Danh gia rui ro an toan thong tin su dung phuong phap nao?",
                language="vietnamese",
                category="technical",
                expected_keywords=["danh gia", "rui ro", "an toan thong tin", "phuong phap", "OCTAVE", "FAIR"],
                expert_notes="Can neu cac phuong phap danh gia rui ro"
            )
        ]
    
    def _create_search_accuracy_cases(self) -> List[SearchAccuracyCase]:
        """Tao 30 cau hoi voi cau tra loi chuan da biet (4.3.4.2)"""
        return [
            SearchAccuracyCase(
                question="Luat An toan thong tin so 86/2015/QH13 co hieu luc tu khi nao?",
                expected_answer="Luat An toan thong tin so 86/2015/QH13 co hieu luc tu ngay 01/7/2016",
                expected_sources=["Luat-86-2015-QH13.pdf"],
                language="vietnamese",
                category="luat"
            ),
            SearchAccuracyCase(
                question="NIST Framework co bao nhieu chuc nang cot loi?",
                expected_answer="NIST Framework co 5 chuc nang cot loi: Identify, Protect, Detect, Respond, Recover",
                expected_sources=["NIST.SP.800-53r5.pdf"],
                language="english",
                category="english"
            ),
            SearchAccuracyCase(
                question="ISO 27001 duoc ban hanh lan dau vao nam nao?",
                expected_answer="ISO 27001 duoc ban hanh lan dau vao nam 2005",
                expected_sources=["ISOIEC_27001_2022.pdf"],
                language="english",
                category="english"
            ),
            SearchAccuracyCase(
                question="TCVN 10541:2014 quy dinh gi?",
                expected_answer="TCVN 10541:2014 quy dinh ve quan ly rui ro an toan thong tin",
                expected_sources=["Tieu_chuan_Viet_Nam-TCVN_10541_2014.pdf"],
                language="vietnamese",
                category="vietnamese"
            ),
            SearchAccuracyCase(
                question="Nghi dinh 53/2022/ND-CP co hieu luc tu khi nao?",
                expected_answer="Nghi dinh 53/2022/ND-CP co hieu luc tu ngay 01/8/2022",
                expected_sources=["Nghi_dinh-53-2022-ND-CP.pdf"],
                language="vietnamese",
                category="luat"
            ),
            SearchAccuracyCase(
                question="What are the three pillars of information security?",
                expected_answer="The three pillars of information security are Confidentiality, Integrity, and Availability (CIA triad)",
                expected_sources=["ISOIEC_27001_2022.pdf", "NIST.SP.800-53r5.pdf"],
                language="english",
                category="general"
            ),
            SearchAccuracyCase(
                question="AES-256 su dung khoa co do dai bao nhieu bit?",
                expected_answer="AES-256 su dung khoa co do dai 256 bit",
                expected_sources=["Cryptography & Network Security 8th Ed.pdf"],
                language="vietnamese",
                category="technical"
            ),
            SearchAccuracyCase(
                question="Thong tu 20/2017/TT-BTTTT quy dinh gi?",
                expected_answer="Thong tu 20/2017/TT-BTTTT quy dinh ve an toan thong tin trong cac co quan nha nuoc",
                expected_sources=["Thong_tu-20-2017-TT-BTTTT.pdf"],
                language="vietnamese",
                category="luat"
            ),
            SearchAccuracyCase(
                question="OWASP Top 10 2021 bao gom nhung lo hong nao?",
                expected_answer="OWASP Top 10 2021 bao gom: Broken Access Control, Cryptographic Failures, Injection, Insecure Design, Security Misconfiguration, Vulnerable Components, Authentication Failures, Software and Data Integrity Failures, Security Logging Failures, Server-Side Request Forgery",
                expected_sources=["OWASP", "web security"],
                language="english",
                category="technical"
            ),
            SearchAccuracyCase(
                question="PCI DSS co bao nhieu yeu cau chinh?",
                expected_answer="PCI DSS co 12 yeu cau chinh duoc chia thanh 6 muc tieu",
                expected_sources=["PCI DSS", "payment security"],
                language="english",
                category="english"
            ),
            SearchAccuracyCase(
                question="Quyet dinh 1118/QD-BTTTT quy dinh gi?",
                expected_answer="Quyet dinh 1118/QD-BTTTT quy dinh ve tieu chuan ky thuat an toan thong tin",
                expected_sources=["Quyet_dinh-1118-QD-BTTTT.pdf"],
                language="vietnamese",
                category="luat"
            ),
            SearchAccuracyCase(
                question="ISO 27002:2022 co bao nhieu nhom kiem soat?",
                expected_answer="ISO 27002:2022 co 4 nhom kiem soat: Organizational, People, Physical, Technological",
                expected_sources=["Tieu_chuan_Viet_Nam-TCVN_ISO-IEC_27002_2020.pdf"],
                language="english",
                category="english"
            ),
            SearchAccuracyCase(
                question="Nghi dinh 142/2016/ND-CP ve gi?",
                expected_answer="Nghi dinh 142/2016/ND-CP ve quy dinh chi tiet thi hanh Luat An toan thong tin",
                expected_sources=["Nghi_dinh-142-2016-ND-CP.pdf"],
                language="vietnamese",
                category="luat"
            ),
            SearchAccuracyCase(
                question="What is the purpose of SOC 2?",
                expected_answer="SOC 2 is designed for service organizations to demonstrate their security controls and compliance with security, availability, processing integrity, confidentiality, and privacy principles",
                expected_sources=["SOC 2", "compliance"],
                language="english",
                category="english"
            ),
            SearchAccuracyCase(
                question="TCVN 12197:2024 quy dinh gi?",
                expected_answer="TCVN 12197:2024 quy dinh ve quan ly su co an toan thong tin",
                expected_sources=["Tieu_chuan_Viet_Nam-TCVN_12197_2024.pdf"],
                language="vietnamese",
                category="vietnamese"
            ),
            SearchAccuracyCase(
                question="Zero Trust Architecture dua tren nguyen tac gi?",
                expected_answer="Zero Trust Architecture dua tren nguyen tac 'Never trust, always verify'",
                expected_sources=["NIST.SP.800-150.pdf"],
                language="vietnamese",
                category="technical"
            ),
            SearchAccuracyCase(
                question="ISO 27035-1:2023 quy dinh gi?",
                expected_answer="ISO 27035-1:2023 quy dinh ve quan ly su co an toan thong tin - Phan 1: Nguyen tac quan ly su co",
                expected_sources=["ISO 27035", "incident management"],
                language="english",
                category="english"
            ),
            SearchAccuracyCase(
                question="Thong tu 12/2019/TT-BTTTT ve gi?",
                expected_answer="Thong tu 12/2019/TT-BTTTT ve quy dinh chi tiet ve an toan thong tin trong cac he thong thong tin",
                expected_sources=["Thong_tu-12-2019-TT-BTTTT.pdf"],
                language="vietnamese",
                category="luat"
            ),
            SearchAccuracyCase(
                question="What is the difference between symmetric and asymmetric encryption?",
                expected_answer="Symmetric encryption uses the same key for encryption and decryption, while asymmetric encryption uses different keys (public and private) for encryption and decryption",
                expected_sources=["Cryptography & Network Security 8th Ed.pdf"],
                language="english",
                category="technical"
            ),
            SearchAccuracyCase(
                question="Nghi dinh 179/2025/ND-CP co hieu luc tu khi nao?",
                expected_answer="Nghi dinh 179/2025/ND-CP co hieu luc tu ngay 01/1/2025",
                expected_sources=["Nghi_dinh-179-2025-ND-CP.pdf"],
                language="vietnamese",
                category="luat"
            ),
            SearchAccuracyCase(
                question="ISO 27017:2015 quy dinh gi?",
                expected_answer="ISO 27017:2015 quy dinh ve kiem soat an toan thong tin cho dich vu dam may",
                expected_sources=["ISO 27017", "cloud security"],
                language="english",
                category="english"
            ),
            SearchAccuracyCase(
                question="Quyet dinh 1603/QD-BHXH quy dinh gi?",
                expected_answer="Quyet dinh 1603/QD-BHXH quy dinh ve quy trinh ung pho su co an toan thong tin",
                expected_sources=["Quyet_dinh-1603-QD-BHXH.pdf"],
                language="vietnamese",
                category="luat"
            ),
            SearchAccuracyCase(
                question="What is the purpose of penetration testing?",
                expected_answer="Penetration testing is conducted to identify security vulnerabilities in systems, networks, or applications by simulating real-world attacks",
                expected_sources=["NIST.SP.800-150.pdf"],
                language="english",
                category="technical"
            ),
            SearchAccuracyCase(
                question="TCVN 14190-1:2024 quy dinh gi?",
                expected_answer="TCVN 14190-1:2024 quy dinh ve quan ly rui ro an toan thong tin - Phan 1: Khung quan ly rui ro",
                expected_sources=["Tieu_chuan_Viet_Nam-TCVN_14190-1_2024.pdf"],
                language="vietnamese",
                category="vietnamese"
            ),
            SearchAccuracyCase(
                question="ISO 31000:2018 quy dinh gi?",
                expected_answer="ISO 31000:2018 quy dinh ve quan ly rui ro - Nguyen tac va huong dan",
                expected_sources=["ISO 31000", "risk management"],
                language="english",
                category="english"
            ),
            SearchAccuracyCase(
                question="Thong tu 12/2022/TT-BTTTT co hieu luc tu khi nao?",
                expected_answer="Thong tu 12/2022/TT-BTTTT co hieu luc tu ngay 01/3/2023",
                expected_sources=["Thong_tu-12-2022-TT-BTTTT.pdf"],
                language="vietnamese",
                category="luat"
            ),
            SearchAccuracyCase(
                question="What is the difference between IDS and IPS?",
                expected_answer="IDS (Intrusion Detection System) detects intrusions and alerts administrators, while IPS (Intrusion Prevention System) detects and actively blocks intrusions",
                expected_sources=["NIST.SP.800-150.pdf"],
                language="english",
                category="technical"
            ),
            SearchAccuracyCase(
                question="Quyet dinh 1760/QD-BKHCN quy dinh gi?",
                expected_answer="Quyet dinh 1760/QD-BKHCN quy dinh ve tieu chuan ky thuat cho cac he thong thong tin",
                expected_sources=["Quyet_dinh-1760-QD-BKHCN.pdf"],
                language="vietnamese",
                category="luat"
            ),
            SearchAccuracyCase(
                question="What is the purpose of SIEM?",
                expected_answer="SIEM (Security Information and Event Management) collects, analyzes, and correlates security events from various sources to detect and respond to security incidents",
                expected_sources=["SIEM", "security monitoring"],
                language="english",
                category="technical"
            )
        ]
    
    def _create_multilingual_cases(self) -> List[MultilingualCase]:
        """Tao test cases cho thu nghiem da ngon ngu (4.3.4.3)"""
        return [
            # Cau hoi tieng Viet (15 cau)
            MultilingualCase(
                question="An toan thong tin la gi?",
                language="vietnamese",
                expected_response_language="vietnamese",
                category="general"
            ),
            MultilingualCase(
                question="Luat An toan thong tin quy dinh gi?",
                language="vietnamese",
                expected_response_language="vietnamese",
                category="luat"
            ),
            MultilingualCase(
                question="Cac bien phap bao mat co ban la gi?",
                language="vietnamese",
                expected_response_language="vietnamese",
                category="technical"
            ),
            MultilingualCase(
                question="Nghi dinh 53/2022/ND-CP co noi dung gi?",
                language="vietnamese",
                expected_response_language="vietnamese",
                category="luat"
            ),
            MultilingualCase(
                question="Firewall hoat dong nhu the nao?",
                language="vietnamese",
                expected_response_language="vietnamese",
                category="technical"
            ),
            MultilingualCase(
                question="TCVN 10541:2014 quy dinh gi ve quan ly rui ro?",
                language="vietnamese",
                expected_response_language="vietnamese",
                category="vietnamese"
            ),
            MultilingualCase(
                question="Phan biet giua ma hoa doi xung va bat doi xung?",
                language="vietnamese",
                expected_response_language="vietnamese",
                category="technical"
            ),
            MultilingualCase(
                question="Quy trinh xu ly su co an toan thong tin?",
                language="vietnamese",
                expected_response_language="vietnamese",
                category="technical"
            ),
            MultilingualCase(
                question="Danh gia rui ro an toan thong tin nhu the nao?",
                language="vietnamese",
                expected_response_language="vietnamese",
                category="technical"
            ),
            MultilingualCase(
                question="Cac nguyen tac co ban cua an toan thong tin?",
                language="vietnamese",
                expected_response_language="vietnamese",
                category="general"
            ),
            MultilingualCase(
                question="Mat khau manh co dac diem gi?",
                language="vietnamese",
                expected_response_language="vietnamese",
                category="technical"
            ),
            MultilingualCase(
                question="VPN la gi va tai sao can su dung?",
                language="vietnamese",
                expected_response_language="vietnamese",
                category="technical"
            ),
            MultilingualCase(
                question="Phishing la gi va cach phong chong?",
                language="vietnamese",
                expected_response_language="vietnamese",
                category="technical"
            ),
            MultilingualCase(
                question="Ransomware la gi?",
                language="vietnamese",
                expected_response_language="vietnamese",
                category="technical"
            ),
            MultilingualCase(
                question="Zero Trust Architecture hoat dong nhu the nao?",
                language="vietnamese",
                expected_response_language="vietnamese",
                category="technical"
            ),
            
            # Cau hoi tieng Anh (15 cau)
            MultilingualCase(
                question="What is information security?",
                language="english",
                expected_response_language="english",
                category="general"
            ),
            MultilingualCase(
                question="What are the core functions of NIST Framework?",
                language="english",
                expected_response_language="english",
                category="english"
            ),
            MultilingualCase(
                question="What are the requirements of ISO 27001?",
                language="english",
                expected_response_language="english",
                category="english"
            ),
            MultilingualCase(
                question="What is the difference between symmetric and asymmetric encryption?",
                language="english",
                expected_response_language="english",
                category="technical"
            ),
            MultilingualCase(
                question="What is OWASP Top 10?",
                language="english",
                expected_response_language="english",
                category="technical"
            ),
            MultilingualCase(
                question="What is SOC 2 compliance?",
                language="english",
                expected_response_language="english",
                category="english"
            ),
            MultilingualCase(
                question="What are the key principles of CIS Controls?",
                language="english",
                expected_response_language="english",
                category="english"
            ),
            MultilingualCase(
                question="What is the purpose of SIEM?",
                language="english",
                expected_response_language="english",
                category="technical"
            ),
            MultilingualCase(
                question="How does blockchain technology enhance security?",
                language="english",
                expected_response_language="english",
                category="technical"
            ),
            MultilingualCase(
                question="What is the difference between IDS and IPS?",
                language="english",
                expected_response_language="english",
                category="technical"
            ),
            MultilingualCase(
                question="What is Zero Trust Architecture?",
                language="english",
                expected_response_language="english",
                category="technical"
            ),
            MultilingualCase(
                question="What is PCI DSS?",
                language="english",
                expected_response_language="english",
                category="english"
            ),
            MultilingualCase(
                question="What is GDPR?",
                language="english",
                expected_response_language="english",
                category="english"
            ),
            MultilingualCase(
                question="What is COBIT framework?",
                language="english",
                expected_response_language="english",
                category="english"
            ),
            MultilingualCase(
                question="How to implement secure coding practices?",
                language="english",
                expected_response_language="english",
                category="technical"
            ),
            
            # Cau hoi hon hop (10 cau)
            MultilingualCase(
                question="ISO 27001 co nhung yeu cau gi ve information security management?",
                language="mixed",
                expected_response_language="vietnamese",
                category="english"
            ),
            MultilingualCase(
                question="Luat 86/2015/QH13 quy dinh gi ve information security?",
                language="mixed",
                expected_response_language="vietnamese",
                category="luat"
            ),
            MultilingualCase(
                question="NIST Framework co nhung core functions nao?",
                language="mixed",
                expected_response_language="vietnamese",
                category="english"
            ),
            MultilingualCase(
                question="An toan thong tin theo ISO 27001 co nhung gi?",
                language="mixed",
                expected_response_language="vietnamese",
                category="english"
            ),
            MultilingualCase(
                question="OWASP Top 10 co nhung vulnerabilities nao?",
                language="mixed",
                expected_response_language="vietnamese",
                category="technical"
            ),
            MultilingualCase(
                question="GDPR co nhung principles nao ve data protection?",
                language="mixed",
                expected_response_language="vietnamese",
                category="english"
            ),
            MultilingualCase(
                question="Zero Trust Architecture hoat dong theo principles nao?",
                language="mixed",
                expected_response_language="vietnamese",
                category="technical"
            ),
            MultilingualCase(
                question="SOC 2 compliance yeu cau nhung gi ve security?",
                language="mixed",
                expected_response_language="vietnamese",
                category="english"
            ),
            MultilingualCase(
                question="PCI DSS co nhung requirements nao cho payment security?",
                language="mixed",
                expected_response_language="vietnamese",
                category="english"
            ),
            MultilingualCase(
                question="CIS Controls co nhung principles nao ve cybersecurity?",
                language="mixed",
                expected_response_language="vietnamese",
                category="english"
            )
        ]
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def run_expert_evaluation_test(self) -> Dict[str, Any]:
        """Thuc hien thu nghiem danh gia boi chuyen gia (4.3.4.1)"""
        logger.info("Bat dau thu nghiem danh gia boi chuyen gia voi 50 cau hoi...")
        
        all_results = []
        successful_results = []
        
        for i, test_case in enumerate(self.expert_evaluation_cases, 1):
            logger.info(f"Test cau hoi {i}/50: {test_case.question[:50]}...")
            
            payload = {
                "question": test_case.question,
                "top_k": 5,
                "include_sources": True,
                "use_enhancement": True
            }
            
            try:
                async with self.session.post(self.api_endpoint, json=payload) as response:
                    if response.status != 200:
                        result = {
                            "test_case": test_case.question,
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "expert_evaluation": {}
                        }
                        all_results.append(result)
                        continue
                    
                    response_data = await response.json()
                    answer = response_data.get("answer", "")
                    sources = response_data.get("sources", [])
                    
                    # Danh gia theo 5 tieu chi (thang diem 1-5)
                    expert_evaluation = self._evaluate_by_expert_criteria(test_case, answer, sources)
                    
                    result = {
                        "test_case": test_case.question,
                        "language": test_case.language,
                        "category": test_case.category,
                        "success": True,
                        "answer": answer,
                        "sources": sources,
                        "expert_evaluation": expert_evaluation,
                        "expert_notes": test_case.expert_notes
                    }
                    
                    all_results.append(result)
                    successful_results.append(result)
                    
                    await asyncio.sleep(0.2)  # Nghi ngan giua cac requests
                    
            except Exception as e:
                logger.error(f"Test case failed: {test_case.question} - {e}")
                result = {
                    "test_case": test_case.question,
                    "success": False,
                    "error": str(e),
                    "expert_evaluation": {}
                }
                all_results.append(result)
        
        # Tinh toan thong ke
        if successful_results:
            stats = self._calculate_expert_evaluation_stats(successful_results)
            return {
                "total_questions": len(self.expert_evaluation_cases),
                "successful_questions": len(successful_results),
                "failed_questions": len(all_results) - len(successful_results),
                "success_rate": len(successful_results) / len(self.expert_evaluation_cases) * 100,
                "expert_evaluation_stats": stats,
                "all_results": all_results
            }
        else:
            return {
                "total_questions": len(self.expert_evaluation_cases),
                "successful_questions": 0,
                "failed_questions": len(all_results),
                "success_rate": 0,
                "error": "Khong co cau hoi nao thanh cong"
            }
    
    async def run_search_accuracy_test(self) -> Dict[str, Any]:
        """Thuc hien thu nghiem do chinh xac tim kiem (4.3.4.2)"""
        logger.info("Bat dau thu nghiem do chinh xac tim kiem voi 30 cau hoi...")
        
        all_results = []
        successful_results = []
        
        for i, test_case in enumerate(self.search_accuracy_cases, 1):
            logger.info(f"Test cau hoi {i}/30: {test_case.question[:50]}...")
            
            payload = {
                "question": test_case.question,
                "top_k": 5,
                "include_sources": True,
                "use_enhancement": True
            }
            
            try:
                async with self.session.post(self.api_endpoint, json=payload) as response:
                    if response.status != 200:
                        result = {
                            "test_case": test_case.question,
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "search_metrics": {}
                        }
                        all_results.append(result)
                        continue
                    
                    response_data = await response.json()
                    answer = response_data.get("answer", "")
                    sources = response_data.get("sources", [])
                    
                    # Tinh toan Precision, Recall, F1-Score
                    search_metrics = self._calculate_search_metrics(test_case, answer, sources)
                    
                    result = {
                        "test_case": test_case.question,
                        "expected_answer": test_case.expected_answer,
                        "actual_answer": answer,
                        "language": test_case.language,
                        "category": test_case.category,
                        "success": True,
                        "sources": sources,
                        "search_metrics": search_metrics
                    }
                    
                    all_results.append(result)
                    successful_results.append(result)
                    
                    await asyncio.sleep(0.2)
                    
            except Exception as e:
                logger.error(f"Search test case failed: {test_case.question} - {e}")
                result = {
                    "test_case": test_case.question,
                    "success": False,
                    "error": str(e),
                    "search_metrics": {}
                }
                all_results.append(result)
        
        # Tinh toan thong ke tong hop
        if successful_results:
            overall_metrics = self._calculate_overall_search_metrics(successful_results)
            return {
                "total_questions": len(self.search_accuracy_cases),
                "successful_questions": len(successful_results),
                "failed_questions": len(all_results) - len(successful_results),
                "success_rate": len(successful_results) / len(self.search_accuracy_cases) * 100,
                "overall_search_metrics": overall_metrics,
                "all_results": all_results
            }
        else:
            return {
                "total_questions": len(self.search_accuracy_cases),
                "successful_questions": 0,
                "failed_questions": len(all_results),
                "success_rate": 0,
                "error": "Khong co cau hoi nao thanh cong"
            }
    
    async def run_multilingual_test(self) -> Dict[str, Any]:
        """Thuc hien thu nghiem da ngon ngu (4.3.4.3)"""
        logger.info("Bat dau thu nghiem da ngon ngu voi 40 cau hoi...")
        
        all_results = []
        successful_results = []
        
        # Phan loai theo ngon ngu
        vietnamese_results = []
        english_results = []
        mixed_results = []
        
        for i, test_case in enumerate(self.multilingual_cases, 1):
            logger.info(f"Test cau hoi {i}/40 ({test_case.language}): {test_case.question[:50]}...")
            
            payload = {
                "question": test_case.question,
                "top_k": 5,
                "include_sources": True,
                "use_enhancement": True
            }
            
            start_time = time.time()
            
            try:
                async with self.session.post(self.api_endpoint, json=payload) as response:
                    response_time = (time.time() - start_time) * 1000  # ms
                    
                    if response.status != 200:
                        result = {
                            "test_case": test_case.question,
                            "language": test_case.language,
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "response_time_ms": response_time,
                            "accuracy": 0
                        }
                        all_results.append(result)
                        continue
                    
                    response_data = await response.json()
                    answer = response_data.get("answer", "")
                    
                    # Danh gia do chinh xac va ngon ngu phan hoi
                    accuracy = self._evaluate_multilingual_accuracy(test_case, answer)
                    
                    result = {
                        "test_case": test_case.question,
                        "language": test_case.language,
                        "expected_language": test_case.expected_response_language,
                        "category": test_case.category,
                        "success": True,
                        "answer": answer,
                        "response_time_ms": response_time,
                        "accuracy": accuracy
                    }
                    
                    all_results.append(result)
                    successful_results.append(result)
                    
                    # Phan loai theo ngon ngu
                    if test_case.language == "vietnamese":
                        vietnamese_results.append(result)
                    elif test_case.language == "english":
                        english_results.append(result)
                    elif test_case.language == "mixed":
                        mixed_results.append(result)
                    
                    await asyncio.sleep(0.2)
                    
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                logger.error(f"Multilingual test case failed: {test_case.question} - {e}")
                result = {
                    "test_case": test_case.question,
                    "language": test_case.language,
                    "success": False,
                    "error": str(e),
                    "response_time_ms": response_time,
                    "accuracy": 0
                }
                all_results.append(result)
        
        # Tinh toan thong ke theo ngon ngu
        multilingual_stats = self._calculate_multilingual_stats(vietnamese_results, english_results, mixed_results)
        
        return {
            "total_questions": len(self.multilingual_cases),
            "successful_questions": len(successful_results),
            "failed_questions": len(all_results) - len(successful_results),
            "success_rate": len(successful_results) / len(self.multilingual_cases) * 100,
            "multilingual_stats": multilingual_stats,
            "all_results": all_results
        }
    
    def _evaluate_by_expert_criteria(self, test_case: ExpertEvaluationCase, answer: str, sources: List[Dict]) -> Dict[str, Any]:
        """Danh gia theo 5 tieu chi chuyen gia (thang diem 1-5)"""
        # 1. Do chinh xac thong tin (Accuracy) - 1-5
        accuracy_score = self._calculate_accuracy_score(test_case, answer)
        
        # 2. Tinh day du (Completeness) - 1-5
        completeness_score = self._calculate_completeness_score(test_case, answer)
        
        # 3. Tinh lien quan (Relevance) - 1-5
        relevance_score = self._calculate_relevance_score(test_case, answer)
        
        # 4. Tinh de hieu (Clarity) - 1-5
        clarity_score = self._calculate_clarity_score(answer, test_case.language)
        
        # 5. Tinh cap nhat (Currency) - 1-5
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
        """Tinh diem do chinh xac thong tin"""
        answer_lower = answer.lower()
        
        # Kiem tra tu khoa quan trong
        keyword_count = 0
        for keyword in test_case.expected_keywords:
            if keyword.lower() in answer_lower:
                keyword_count += 1
        
        keyword_score = keyword_count / len(test_case.expected_keywords) if test_case.expected_keywords else 0
        
        # Chuyen doi thanh thang diem 1-5
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
        """Tinh diem tinh day du"""
        answer_length = len(answer)
        
        # Dieu chinh theo loai cau hoi
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
        """Tinh diem tinh lien quan"""
        answer_lower = answer.lower()
        question_lower = test_case.question.lower()
        
        # Trich xuat tu khoa tu cau hoi
        question_words = set(re.findall(r'\b\w+\b', question_lower))
        answer_words = set(re.findall(r'\b\w+\b', answer_lower))
        
        # Tinh do trung lap
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
        """Tinh diem tinh de hieu"""
        if not answer:
            return 1.0
        
        # Kiem tra cau truc cau
        sentences = re.split(r'[.!?]+', answer)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 2.0
        
        # Kiem tra do dai cau trung binh
        avg_sentence_length = sum(len(s) for s in sentences) / len(sentences)
        
        # Dieu chinh theo ngon ngu
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
        """Tinh diem tinh cap nhat"""
        if not sources:
            return 2.0
        
        # Kiem tra nguon tai lieu co gan day khong
        recent_sources = 0
        for source in sources:
            filename = source.get("filename", "").lower()
            # Kiem tra nam trong ten file
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
        """Tinh toan Precision, Recall, F1-Score"""
        # Precision: So cau tra loi chinh xac / Tong so cau tra loi
        precision = self._calculate_precision(test_case, answer)
        
        # Recall: So thong tin chinh xac duoc tim thay / Tong so thong tin chinh xac
        recall = self._calculate_recall(test_case, answer)
        
        # F1-Score: Harmonic mean cua Precision va Recall
        f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score
        }
    
    def _calculate_precision(self, test_case: SearchAccuracyCase, answer: str) -> float:
        """Tinh Precision"""
        # Don gian hoa: kiem tra xem cau tra loi co chua thong tin chinh xac khong
        expected_lower = test_case.expected_answer.lower()
        answer_lower = answer.lower()
        
        # Tach tu va so sanh
        expected_words = set(re.findall(r'\b\w+\b', expected_lower))
        answer_words = set(re.findall(r'\b\w+\b', answer_lower))
        
        # Dem tu khoa chinh
        key_words = {"luat", "nghi dinh", "thong tu", "quyet dinh", "iso", "nist", "tcvn", "ngay", "thang", "nam"}
        expected_key_words = expected_words & key_words
        answer_key_words = answer_words & key_words
        
        if not expected_key_words:
            return 1.0
        
        precision = len(expected_key_words & answer_key_words) / len(expected_key_words)
        return precision
    
    def _calculate_recall(self, test_case: SearchAccuracyCase, answer: str) -> float:
        """Tinh Recall"""
        expected_lower = test_case.expected_answer.lower()
        answer_lower = answer.lower()
        
        # Tach tu va so sanh
        expected_words = set(re.findall(r'\b\w+\b', expected_lower))
        answer_words = set(re.findall(r'\b\w+\b', answer_lower))
        
        if not expected_words:
            return 1.0
        
        # Tinh ty le tu khoa duoc tim thay
        recall = len(expected_words & answer_words) / len(expected_words)
        return recall
    
    def _evaluate_multilingual_accuracy(self, test_case: MultilingualCase, answer: str) -> float:
        """Danh gia do chinh xac cho thu nghiem da ngon ngu"""
        # Kiem tra ngon ngu phan hoi co phu hop khong
        language_match = self._check_language_match(test_case.expected_response_language, answer)
        
        # Kiem tra chat luong noi dung
        content_quality = self._check_content_quality(answer)
        
        return (language_match + content_quality) / 2
    
    def _check_language_match(self, expected_language: str, answer: str) -> float:
        """Kiem tra ngon ngu phan hoi co phu hop khong"""
        if expected_language == "vietnamese":
            # Kiem tra tu tieng Viet
            vietnamese_words = ["la", "cua", "va", "voi", "trong", "cho", "den", "tu", "co", "duoc", "nay", "do", "cac", "mot", "nhu", "ve", "se", "da", "dang", "bi"]
            vietnamese_count = sum(1 for word in vietnamese_words if word in answer.lower())
            return min(vietnamese_count / 5, 1.0)
        elif expected_language == "english":
            # Kiem tra tu tieng Anh
            english_words = ["the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had"]
            english_count = sum(1 for word in english_words if word.lower() in answer.lower())
            return min(english_count / 5, 1.0)
        else:
            return 0.5
    
    def _check_content_quality(self, answer: str) -> float:
        """Kiem tra chat luong noi dung"""
        if len(answer) < 50:
            return 0.3
        elif len(answer) < 100:
            return 0.6
        elif len(answer) < 200:
            return 0.8
        else:
            return 1.0
    
    def _calculate_expert_evaluation_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tinh toan thong ke danh gia chuyen gia"""
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
        """Tinh toan thong ke tim kiem tong hop"""
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
        """Tinh toan thong ke da ngon ngu"""
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
        """Luu ket qua danh gia chuyen gia"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"expert_evaluation_test_{timestamp}.json"
        
        output = {
            "test_type": "expert_evaluation_4_3_4_1",
            "timestamp": timestamp,
            "results": results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        # Tao CSV cho bang ket qua
        csv_filename = f"expert_evaluation_table_{timestamp}.csv"
        self._create_expert_evaluation_table_csv(results, csv_filename)
        
        logger.info(f"[DATA] Ket qua danh gia chuyen gia da duoc luu: {filename}")
        logger.info(f"[DATA] Bang ket qua CSV da duoc luu: {csv_filename}")
        return filename, csv_filename
    
    def save_search_accuracy_results(self, results: Dict[str, Any]):
        """Luu ket qua do chinh xac tim kiem"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"search_accuracy_test_{timestamp}.json"
        
        output = {
            "test_type": "search_accuracy_4_3_4_2",
            "timestamp": timestamp,
            "results": results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        # Tao CSV cho bang ket qua
        csv_filename = f"search_accuracy_table_{timestamp}.csv"
        self._create_search_accuracy_table_csv(results, csv_filename)
        
        logger.info(f"[DATA] Ket qua do chinh xac tim kiem da duoc luu: {filename}")
        logger.info(f"[DATA] Bang ket qua CSV da duoc luu: {csv_filename}")
        return filename, csv_filename
    
    def save_multilingual_results(self, results: Dict[str, Any]):
        """Luu ket qua thu nghiem da ngon ngu"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"multilingual_test_{timestamp}.json"
        
        output = {
            "test_type": "multilingual_4_3_4_3",
            "timestamp": timestamp,
            "results": results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        # Tao CSV cho bang ket qua
        csv_filename = f"multilingual_table_{timestamp}.csv"
        self._create_multilingual_table_csv(results, csv_filename)
        
        logger.info(f"[DATA] Ket qua thu nghiem da ngon ngu da duoc luu: {filename}")
        logger.info(f"[DATA] Bang ket qua CSV da duoc luu: {csv_filename}")
        return filename, csv_filename
    
    def _create_expert_evaluation_table_csv(self, results: Dict[str, Any], filename: str):
        """Tao bang CSV cho ket qua danh gia chuyen gia"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['Tieu chi', 'Diem trung binh', 'Do lech chuan', 'Ghi chu'])
            
            if 'expert_evaluation_stats' in results:
                stats = results['expert_evaluation_stats']
                
                writer.writerow([
                    'Do chinh xac thong tin (Accuracy)',
                    f"{stats['accuracy']['mean']:.2f}",
                    f"{stats['accuracy']['std_dev']:.2f}",
                    'Thang diem 1-5'
                ])
                
                writer.writerow([
                    'Tinh day du (Completeness)',
                    f"{stats['completeness']['mean']:.2f}",
                    f"{stats['completeness']['std_dev']:.2f}",
                    'Thang diem 1-5'
                ])
                
                writer.writerow([
                    'Tinh lien quan (Relevance)',
                    f"{stats['relevance']['mean']:.2f}",
                    f"{stats['relevance']['std_dev']:.2f}",
                    'Thang diem 1-5'
                ])
                
                writer.writerow([
                    'Tinh de hieu (Clarity)',
                    f"{stats['clarity']['mean']:.2f}",
                    f"{stats['clarity']['std_dev']:.2f}",
                    'Thang diem 1-5'
                ])
                
                writer.writerow([
                    'Tinh cap nhat (Currency)',
                    f"{stats['currency']['mean']:.2f}",
                    f"{stats['currency']['std_dev']:.2f}",
                    'Thang diem 1-5'
                ])
    
    def _create_search_accuracy_table_csv(self, results: Dict[str, Any], filename: str):
        """Tao bang CSV cho ket qua do chinh xac tim kiem"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['Metric', 'Gia tri', 'Ghi chu'])
            
            if 'overall_search_metrics' in results:
                metrics = results['overall_search_metrics']
                
                writer.writerow([
                    'Precision',
                    f"{metrics['precision']['mean']:.3f}",
                    'Do chinh xac tim kiem'
                ])
                
                writer.writerow([
                    'Recall',
                    f"{metrics['recall']['mean']:.3f}",
                    'Do bao phu tim kiem'
                ])
                
                writer.writerow([
                    'F1-Score',
                    f"{metrics['f1_score']['mean']:.3f}",
                    'Trung binh dieu hoa cua Precision va Recall'
                ])
    
    def _create_multilingual_table_csv(self, results: Dict[str, Any], filename: str):
        """Tao bang CSV cho ket qua thu nghiem da ngon ngu"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['Ngon ngu', 'So cau hoi', 'Do chinh xac', 'Thoi gian phan hoi (s)'])
            
            if 'multilingual_stats' in results:
                stats = results['multilingual_stats']
                
                writer.writerow([
                    'Tieng Viet',
                    stats['vietnamese']['count'],
                    f"{stats['vietnamese']['avg_accuracy']:.3f}",
                    f"{stats['vietnamese']['avg_response_time']/1000:.3f}"
                ])
                
                writer.writerow([
                    'Tieng Anh',
                    stats['english']['count'],
                    f"{stats['english']['avg_accuracy']:.3f}",
                    f"{stats['english']['avg_response_time']/1000:.3f}"
                ])
                
                writer.writerow([
                    'Hon hop',
                    stats['mixed']['count'],
                    f"{stats['mixed']['avg_accuracy']:.3f}",
                    f"{stats['mixed']['avg_response_time']/1000:.3f}"
                ])
    
    def print_expert_evaluation_summary(self, results: Dict[str, Any]):
        """In tom tat ket qua danh gia chuyen gia"""
        print(f"\n{'='*80}")
        print(f"[TARGET] KẾT QUẢ THỬ NGHIỆM DỘ CHÍNH XÁC CÂU TRẢ LỜI (4.3.4.1)")
        print(f"{'='*80}")
        
        if "error" in results:
            print(f"[ERROR] Loi: {results['error']}")
            return
        
        print(f"[DATA] Tong quan:")
        print(f"   - Tong cau hoi test: {results['total_questions']}")
        print(f"   - Cau hoi thanh cong: {results['successful_questions']}")
        print(f"   - Ty le thanh cong: {results['success_rate']:.1f}%")
        
        if "expert_evaluation_stats" in results:
            stats = results["expert_evaluation_stats"]
            print(f"\n[TARGET] DÁNH GIÁ THEO 5 TIÊU CHÍ (Thang diem 1-5):")
            print("-" * 60)
            
            criteria = [
                ("Do chinh xac thong tin (Accuracy)", stats["accuracy"]),
                ("Tinh day du (Completeness)", stats["completeness"]),
                ("Tinh lien quan (Relevance)", stats["relevance"]),
                ("Tinh de hieu (Clarity)", stats["clarity"]),
                ("Tinh cap nhat (Currency)", stats["currency"])
            ]
            
            for criterion_name, criterion_stats in criteria:
                print(f"{criterion_name:30} | TB: {criterion_stats['mean']:4.2f} | DLC: {criterion_stats['std_dev']:4.2f}")
            
            print(f"\n[DATA] Diem tong the: {stats['overall']['mean']:.2f}/5.0 (DLC: {stats['overall']['std_dev']:.2f})")
    
    def print_search_accuracy_summary(self, results: Dict[str, Any]):
        """In tom tat ket qua do chinh xac tim kiem"""
        print(f"\n{'='*80}")
        print(f"[SEARCH] KẾT QUẢ THỬ NGHIỆM DỘ CHÍNH XÁC TÌM KIẾM (4.3.4.2)")
        print(f"{'='*80}")
        
        if "error" in results:
            print(f"[ERROR] Loi: {results['error']}")
            return
        
        print(f"[DATA] Tong quan:")
        print(f"   - Tong cau hoi test: {results['total_questions']}")
        print(f"   - Cau hoi thanh cong: {results['successful_questions']}")
        print(f"   - Ty le thanh cong: {results['success_rate']:.1f}%")
        
        if "overall_search_metrics" in results:
            metrics = results["overall_search_metrics"]
            print(f"\n[SEARCH] METRIC TÌM KIẾM:")
            print("-" * 60)
            
            print(f"Precision{'':15} | {metrics['precision']['mean']:6.3f} | Do chinh xac tim kiem")
            print(f"Recall{'':18} | {metrics['recall']['mean']:6.3f} | Do bao phu tim kiem")
            print(f"F1-Score{'':16} | {metrics['f1_score']['mean']:6.3f} | Trung binh dieu hoa")
    
    def print_multilingual_summary(self, results: Dict[str, Any]):
        """In tom tat ket qua thu nghiem da ngon ngu"""
        print(f"\n{'='*80}")
        print(f"[WEB] KẾT QUẢ THỬ NGHIỆM DA NGÔN NGỮ (4.3.4.3)")
        print(f"{'='*80}")
        
        if "error" in results:
            print(f"[ERROR] Loi: {results['error']}")
            return
        
        print(f"[DATA] Tong quan:")
        print(f"   - Tong cau hoi test: {results['total_questions']}")
        print(f"   - Cau hoi thanh cong: {results['successful_questions']}")
        print(f"   - Ty le thanh cong: {results['success_rate']:.1f}%")
        
        if "multilingual_stats" in results:
            stats = results["multilingual_stats"]
            print(f"\n[WEB] KẾT QUẢ THEO NGÔN NGỮ:")
            print("-" * 60)
            
            languages = [
                ("Tieng Viet", stats["vietnamese"]),
                ("Tieng Anh", stats["english"]),
                ("Hon hop", stats["mixed"])
            ]
            
            for lang_name, lang_stats in languages:
                print(f"{lang_name:15} | So cau: {lang_stats['count']:2d} | Do chinh xac: {lang_stats['avg_accuracy']:5.3f} | Thoi gian: {lang_stats['avg_response_time']/1000:6.3f}s")

async def main():
    """Chay tat ca cac test do chinh xac theo yeu cau 4.3.4.1, 4.3.4.2, 4.3.4.3"""
    async with AccuracyTester() as tester:
        print("[TARGET] BẮT DẦU THỬ NGHIỆM DỘ CHÍNH XÁC HỆ THỐNG TRỢ LÝ ẢO AN TOÀN THÔNG TIN")
        print("Theo yeu cau 4.3.4.1, 4.3.4.2, 4.3.4.3")
        print("="*80)
        
        # Test 1: Danh gia boi chuyen gia (4.3.4.1)
        print("\n[TEST] Test 1: Thu nghiem do chinh xac cau tra loi (50 cau hoi chuan)")
        expert_results = await tester.run_expert_evaluation_test()
        tester.print_expert_evaluation_summary(expert_results)
        tester.save_expert_evaluation_results(expert_results)
        
        # Test 2: Do chinh xac tim kiem (4.3.4.2)
        print("\n[TEST] Test 2: Thu nghiem do chinh xac tim kiem (30 cau hoi)")
        search_results = await tester.run_search_accuracy_test()
        tester.print_search_accuracy_summary(search_results)
        tester.save_search_accuracy_results(search_results)
        
        # Test 3: Thu nghiem da ngon ngu (4.3.4.3)
        print("\n[TEST] Test 3: Thu nghiem da ngon ngu (40 cau hoi)")
        multilingual_results = await tester.run_multilingual_test()
        tester.print_multilingual_summary(multilingual_results)
        tester.save_multilingual_results(multilingual_results)
        
        print(f"\n[OK] HOÀN THÀNH THỬ NGHIỆM DỘ CHÍNH XÁC")
        print("[FILE] Cac files ket qua da duoc tao:")
        print("   - JSON: expert_evaluation_test_TIMESTAMP.json")
        print("   - CSV: expert_evaluation_table_TIMESTAMP.csv")
        print("   - JSON: search_accuracy_test_TIMESTAMP.json")
        print("   - CSV: search_accuracy_table_TIMESTAMP.csv")
        print("   - JSON: multilingual_test_TIMESTAMP.json")
        print("   - CSV: multilingual_table_TIMESTAMP.csv")
        print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
