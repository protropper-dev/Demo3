# Hệ thống Thử nghiệm Toàn diện cho Trợ lý Ảo An toàn Thông tin

## Tổng quan

Đây là bộ công cụ thử nghiệm toàn diện để đánh giá hệ thống trợ lý ảo về an toàn thông tin theo 3 tiêu chí chính:

1. **Thử nghiệm Hiệu suất (Performance Testing)**
2. **Thử nghiệm Độ chính xác (Accuracy Testing)** 
3. **Thử nghiệm Chất lượng Phản hồi (Response Quality Testing)**

## Cấu trúc Files

```
├── test_performance.py          # Script thử nghiệm hiệu suất
├── test_accuracy.py            # Script thử nghiệm độ chính xác
├── test_response_quality.py    # Script thử nghiệm chất lượng phản hồi
├── test_comprehensive.py       # Script tổng hợp chạy tất cả tests
├── requirements_testing.txt    # Dependencies cần thiết
└── README_TESTING.md          # Hướng dẫn này
```

## Cài đặt

### 1. Cài đặt Dependencies

```bash
pip install -r requirements_testing.txt
```

### 2. Đảm bảo Backend Server đang chạy

```bash
cd backend1
python main.py
```

Server sẽ chạy trên `http://localhost:8000`

## Sử dụng

### Chạy Tất cả Thử nghiệm (Khuyến nghị)

```bash
python test_comprehensive.py
```

Script này sẽ:
- Kiểm tra kết nối đến server
- Chạy tất cả 3 loại thử nghiệm
- Tạo báo cáo tổng hợp
- Lưu kết quả chi tiết

### Chạy Từng Loại Thử nghiệm Riêng lẻ

#### 1. Thử nghiệm Hiệu suất (Theo yêu cầu 4.3.3.1 và 4.3.3.2)
```bash
python test_performance.py
```

**Các test bao gồm:**
- **4.3.3.1 Thử nghiệm thời gian phản hồi**: 100 câu hỏi mẫu với độ dài khác nhau
- **4.3.3.2 Thử nghiệm sử dụng tài nguyên**: Monitor CPU, RAM, GPU

**Metrics đánh giá:**
- **Thời gian từng thành phần**: Embedding Query, Vector Search, Context Retrieval, LLM Generation
- **Thời gian tổng**: Min, max, mean cho từng thành phần
- **Tài nguyên hệ thống**: CPU %, RAM %, GPU % (trung bình và tối đa)
- **Bảng kết quả**: Xuất ra file CSV theo format yêu cầu

#### 2. Thử nghiệm Độ chính xác
```bash
python test_accuracy.py
```

**Test cases bao gồm:**
- 12 câu hỏi đa dạng về an toàn thông tin
- Phân loại theo độ khó: easy, medium, hard
- Phân loại theo domain: luat, english, vietnamese, technical

**Metrics đánh giá:**
- Keyword Coverage (tỷ lệ từ khóa quan trọng được đề cập)
- Length Appropriateness (độ dài phù hợp)
- Source Relevance (liên quan nguồn tài liệu)
- Completeness (tính đầy đủ)
- Technical Accuracy (chính xác kỹ thuật)

#### 3. Thử nghiệm Chất lượng Phản hồi
```bash
python test_response_quality.py
```

**Test cases bao gồm:**
- 12 câu hỏi cho các loại người dùng khác nhau
- Phân loại theo user type: beginner, expert, administrator, student
- Phân loại theo complexity: basic, intermediate, advanced

**Metrics đánh giá:**
- Coherence (tính mạch lạc)
- Relevance (liên quan đến câu hỏi)
- Helpfulness (tính hữu ích)
- Clarity (rõ ràng, dễ hiểu)
- Completeness (đầy đủ)
- Tone Appropriateness (giọng điệu phù hợp)
- Source Quality (chất lượng nguồn)
- Structure (cấu trúc)

## Kết quả và Báo cáo

### Files Kết quả

Mỗi lần chạy test sẽ tạo các files:

```
├── response_time_test_TIMESTAMP.json          # Kết quả thời gian phản hồi (4.3.3.1)
├── response_time_table_TIMESTAMP.csv          # Bảng thời gian phản hồi (CSV)
├── resource_usage_test_TIMESTAMP.json         # Kết quả sử dụng tài nguyên (4.3.3.2)
├── resource_usage_table_TIMESTAMP.csv         # Bảng sử dụng tài nguyên (CSV)
├── accuracy_test_results_TIMESTAMP.log  
├── response_quality_test_results_TIMESTAMP.log
├── comprehensive_test_results_TIMESTAMP.log
└── comprehensive_test_results_TIMESTAMP.json
```

### Format Báo cáo

#### Báo cáo Tổng hợp (Comprehensive)
- **Điểm tổng thể**: 0.0 - 1.0
- **Chi tiết từng loại test**: Performance, Accuracy, Quality
- **Khuyến nghị cải thiện**: Dựa trên kết quả
- **Thống kê thời gian**: Thời gian chạy test

#### Báo cáo Chi tiết (JSON)
- Metrics chi tiết cho từng test case
- Kết quả raw data
- Phân tích theo độ khó và domain
- Timestamps và metadata

#### Báo cáo CSV (Theo yêu cầu 4.3.3.1 và 4.3.3.2)
- **response_time_table_TIMESTAMP.csv**: Bảng thời gian phản hồi theo format yêu cầu
- **resource_usage_table_TIMESTAMP.csv**: Bảng sử dụng tài nguyên theo format yêu cầu

## Cấu hình

### Thay đổi Base URL

Mặc định: `http://localhost:8000`

Để thay đổi, sửa trong các script:

```python
tester = PerformanceTester(base_url="http://your-server:port")
```

### Điều chỉnh Test Parameters

#### Performance Testing (4.3.3.1 và 4.3.3.2)
```python
# Thay đổi số lượng câu hỏi test (mặc định 100)
tester.test_questions = tester._generate_100_test_questions()[:50]  # chỉ test 50 câu

# Thay đổi interval monitor tài nguyên (mặc định 0.5s)
# Trong ResourceMonitor._monitor_loop()
time.sleep(1.0)  # monitor mỗi 1 giây thay vì 0.5 giây
```

#### Accuracy Testing
- Thêm test cases mới trong `_create_test_cases()`
- Điều chỉnh expected keywords và categories

#### Response Quality Testing  
- Thêm test cases mới trong `_create_quality_test_cases()`
- Điều chỉnh expected tone và response type

## Troubleshooting

### Lỗi Kết nối

```
❌ Không thể kết nối đến server: Connection refused
```

**Giải pháp:**
1. Đảm bảo backend server đang chạy
2. Kiểm tra URL trong script
3. Kiểm tra firewall/network

### Lỗi Import Module

```
ModuleNotFoundError: No module named 'aiohttp'
```

**Giải pháp:**
```bash
pip install -r requirements_testing.txt
```

### Lỗi Timeout

```
asyncio.TimeoutError
```

**Giải pháp:**
1. Tăng timeout trong script
2. Giảm số lượng concurrent requests
3. Kiểm tra hiệu suất server

## Tùy chỉnh và Mở rộng

### Thêm Test Cases Mới

#### Accuracy Testing
```python
TestCase(
    question="Câu hỏi mới của bạn?",
    expected_keywords=["từ", "khóa", "quan", "trọng"],
    expected_category="luat",  # hoặc "english", "vietnamese", "all"
    difficulty="medium",       # "easy", "medium", "hard"
    domain="technical",        # "luat", "english", "vietnamese", "technical", "general"
    expected_answer_length=(100, 500)  # (min, max)
)
```

#### Response Quality Testing
```python
QualityTestCase(
    question="Câu hỏi mới?",
    context="Mô tả ngữ cảnh",
    expected_response_type="explanatory",  # "factual", "procedural", "comparative", "explanatory"
    expected_tone="professional",          # "professional", "educational", "technical", "friendly"
    complexity_level="intermediate",       # "basic", "intermediate", "advanced"
    user_type="administrator"             # "beginner", "expert", "administrator", "student"
)
```

### Thêm Metrics Mới

Mở rộng các hàm đánh giá trong từng script để thêm metrics mới.

## Liên hệ và Hỗ trợ

Nếu có vấn đề hoặc cần hỗ trợ, vui lòng tạo issue hoặc liên hệ team phát triển.

---

**Lưu ý**: Đảm bảo chạy tests trên môi trường phù hợp và không ảnh hưởng đến hệ thống production.
