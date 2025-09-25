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

**Metrics đánh giá chi tiết:**

**4.3.3.1 Thời gian phản hồi:**
- **Embedding Query**: Thời gian tạo embedding từ câu hỏi
- **Vector Search**: Thời gian tìm kiếm vector tương tự trong database
- **Context Retrieval**: Thời gian trích xuất ngữ cảnh từ tài liệu
- **LLM Generation**: Thời gian sinh câu trả lời bằng LLM
- **Total Response Time**: Tổng thời gian xử lý hoàn chỉnh

**Thống kê cho mỗi thành phần:**
- Thời gian trung bình (mean)
- Thời gian tối thiểu (min)
- Thời gian tối đa (max)
- Thời gian trung vị (median)
- Percentile 95 (P95)
- Percentile 99 (P99)

**4.3.3.2 Sử dụng tài nguyên:**
- **CPU Usage**: % sử dụng CPU (trung bình, tối đa)
- **RAM Usage**: % sử dụng RAM (trung bình, tối đa)
- **GPU Usage**: % sử dụng GPU (trung bình, tối đa) - nếu có

**Bảng kết quả CSV:**
- `response_time_table_TIMESTAMP.csv`: Bảng thời gian theo format yêu cầu
- `resource_usage_table_TIMESTAMP.csv`: Bảng tài nguyên theo format yêu cầu

#### 2. Thử nghiệm Độ chính xác (Theo yêu cầu 4.3.4.1, 4.3.4.2, 4.3.4.3)
```bash
python test_accuracy.py
```

**Các test bao gồm:**
- **4.3.4.1 Thử nghiệm độ chính xác câu trả lời**: 50 câu hỏi chuẩn về an toàn thông tin
- **4.3.4.2 Thử nghiệm độ chính xác tìm kiếm**: 30 câu hỏi với câu trả lời chuẩn đã biết
- **4.3.4.3 Thử nghiệm đa ngôn ngữ**: 40 câu hỏi (15 tiếng Việt, 15 tiếng Anh, 10 hỗn hợp)

**Metrics đánh giá chi tiết:**

**4.3.4.1 Đánh giá bởi chuyên gia (5 tiêu chí, thang điểm 1-5):**
- **Độ chính xác thông tin (Accuracy)**: Đánh giá tính chính xác của thông tin
- **Tính đầy đủ (Completeness)**: Đánh giá độ đầy đủ của câu trả lời
- **Tính liên quan (Relevance)**: Đánh giá mức độ liên quan đến câu hỏi
- **Tính dễ hiểu (Clarity)**: Đánh giá tính rõ ràng, dễ hiểu
- **Tính cập nhật (Currency)**: Đánh giá tính cập nhật của thông tin

**Thống kê cho mỗi tiêu chí:**
- Điểm trung bình (mean)
- Độ lệch chuẩn (standard deviation)
- Điểm tổng thể (overall score)

**4.3.4.2 Độ chính xác tìm kiếm:**
- **Precision**: Số câu trả lời chính xác / Tổng số câu trả lời
- **Recall**: Số thông tin chính xác được tìm thấy / Tổng số thông tin chính xác
- **F1-Score**: Harmonic mean của Precision và Recall

**Thống kê tổng hợp:**
- Precision trung bình
- Recall trung bình
- F1-Score trung bình

**4.3.4.3 Thử nghiệm đa ngôn ngữ:**
- **Tiếng Việt**: 15 câu hỏi, đánh giá độ chính xác và thời gian phản hồi
- **Tiếng Anh**: 15 câu hỏi, đánh giá độ chính xác và thời gian phản hồi
- **Hỗn hợp**: 10 câu hỏi, đánh giá khả năng xử lý đa ngôn ngữ

**Thống kê theo ngôn ngữ:**
- Số câu hỏi
- Độ chính xác trung bình
- Thời gian phản hồi trung bình (giây)

**Bảng kết quả CSV:**
- `expert_evaluation_table_TIMESTAMP.csv`: Bảng đánh giá chuyên gia theo format yêu cầu
- `search_accuracy_table_TIMESTAMP.csv`: Bảng metrics tìm kiếm theo format yêu cầu
- `multilingual_table_TIMESTAMP.csv`: Bảng kết quả đa ngôn ngữ theo format yêu cầu

#### 3. Thử nghiệm Chất lượng Phản hồi
```bash
python test_response_quality.py
```

**Test cases bao gồm:**
- 12 câu hỏi cho các loại người dùng khác nhau
- Phân loại theo user type: beginner, expert, administrator, student
- Phân loại theo complexity: basic, intermediate, advanced

**Metrics đánh giá chi tiết:**

**Các tiêu chí đánh giá (thang điểm 1-5):**
- **Coherence (Tính mạch lạc)**: Đánh giá tính logic và kết nối giữa các ý
- **Relevance (Liên quan)**: Đánh giá mức độ liên quan đến câu hỏi
- **Helpfulness (Tính hữu ích)**: Đánh giá mức độ hữu ích của câu trả lời
- **Clarity (Rõ ràng)**: Đánh giá tính rõ ràng, dễ hiểu
- **Completeness (Đầy đủ)**: Đánh giá độ đầy đủ của thông tin
- **Tone Appropriateness (Giọng điệu phù hợp)**: Đánh giá tính phù hợp của giọng điệu
- **Source Quality (Chất lượng nguồn)**: Đánh giá chất lượng nguồn tài liệu
- **Structure (Cấu trúc)**: Đánh giá cấu trúc và tổ chức của câu trả lời

**Thống kê cho mỗi tiêu chí:**
- Điểm trung bình (mean)
- Độ lệch chuẩn (standard deviation)
- Phân tích theo user type
- Phân tích theo complexity level

**Phân tích theo đối tượng người dùng:**
- Beginner: Đánh giá tính dễ hiểu và hướng dẫn cơ bản
- Expert: Đánh giá độ chuyên sâu và tính kỹ thuật
- Administrator: Đánh giá tính thực tiễn và khả thi
- Student: Đánh giá tính giáo dục và học tập

**Phân tích theo độ phức tạp:**
- Basic: Câu hỏi cơ bản, đánh giá khả năng giải thích đơn giản
- Intermediate: Câu hỏi trung bình, đánh giá khả năng phân tích
- Advanced: Câu hỏi nâng cao, đánh giá khả năng chuyên sâu

**Bảng kết quả CSV:**
- `response_quality_table_TIMESTAMP.csv`: Bảng đánh giá chất lượng phản hồi

## Tóm tắt Thông số Đánh giá

### test_performance.py
**Mục đích**: Đánh giá hiệu suất hệ thống theo yêu cầu 4.3.3.1 và 4.3.3.2

**Thông số đánh giá chính:**
- **Thời gian phản hồi**: 5 thành phần (Embedding, Vector Search, Context Retrieval, LLM Generation, Total)
- **Sử dụng tài nguyên**: CPU %, RAM %, GPU % (trung bình và tối đa)
- **Thống kê**: Mean, Min, Max, Median, P95, P99 cho mỗi thông số
- **Số lượng test**: 100 câu hỏi đa dạng
- **Output**: JSON chi tiết + CSV bảng kết quả

### test_accuracy.py
**Mục đích**: Đánh giá độ chính xác theo yêu cầu 4.3.4.1, 4.3.4.2, 4.3.4.3

**Thông số đánh giá chính:**

**4.3.4.1 Đánh giá chuyên gia:**
- **5 tiêu chí**: Accuracy, Completeness, Relevance, Clarity, Currency (thang 1-5)
- **Thống kê**: Mean, Standard Deviation cho mỗi tiêu chí
- **Số lượng test**: 50 câu hỏi chuẩn

**4.3.4.2 Độ chính xác tìm kiếm:**
- **3 metrics**: Precision, Recall, F1-Score
- **Thống kê**: Mean cho mỗi metric
- **Số lượng test**: 30 câu hỏi với đáp án chuẩn

**4.3.4.3 Đa ngôn ngữ:**
- **3 ngôn ngữ**: Tiếng Việt (15), Tiếng Anh (15), Hỗn hợp (10)
- **Thông số**: Độ chính xác, Thời gian phản hồi
- **Thống kê**: Count, Avg Accuracy, Avg Response Time

**Output**: JSON chi tiết + 3 file CSV bảng kết quả

### test_response_quality.py
**Mục đích**: Đánh giá chất lượng phản hồi của hệ thống

**Thông số đánh giá chính:**
- **8 tiêu chí**: Coherence, Relevance, Helpfulness, Clarity, Completeness, Tone, Source Quality, Structure (thang 1-5)
- **Phân loại**: 4 user types (beginner, expert, administrator, student)
- **Độ phức tạp**: 3 levels (basic, intermediate, advanced)
- **Số lượng test**: 12 câu hỏi đa dạng
- **Thống kê**: Mean, Standard Deviation, phân tích theo user type và complexity
- **Output**: JSON chi tiết + CSV bảng kết quả

### test_comprehensive.py
**Mục đích**: Chạy tất cả các test và tạo báo cáo tổng hợp

**Thông số đánh giá chính:**
- **Điểm tổng thể**: 0.0 - 1.0 (tổng hợp từ 3 loại test)
- **Chi tiết từng loại**: Performance Score, Accuracy Score, Quality Score
- **Khuyến nghị**: Dựa trên kết quả để cải thiện hệ thống
- **Thống kê thời gian**: Thời gian chạy từng test và tổng thời gian
- **Output**: Log file + JSON báo cáo tổng hợp

## Kết quả và Báo cáo

### Files Kết quả

Mỗi lần chạy test sẽ tạo các files:

**Performance Testing (test_performance.py):**
```
├── response_time_test_TIMESTAMP.json          # Kết quả thời gian phản hồi (4.3.3.1)
├── response_time_table_TIMESTAMP.csv          # Bảng thời gian phản hồi (CSV)
├── resource_usage_test_TIMESTAMP.json         # Kết quả sử dụng tài nguyên (4.3.3.2)
└── resource_usage_table_TIMESTAMP.csv         # Bảng sử dụng tài nguyên (CSV)
```

**Accuracy Testing (test_accuracy.py):**
```
├── expert_evaluation_test_TIMESTAMP.json      # Kết quả đánh giá chuyên gia (4.3.4.1)
├── expert_evaluation_table_TIMESTAMP.csv      # Bảng đánh giá chuyên gia (CSV)
├── search_accuracy_test_TIMESTAMP.json        # Kết quả độ chính xác tìm kiếm (4.3.4.2)
├── search_accuracy_table_TIMESTAMP.csv        # Bảng metrics tìm kiếm (CSV)
├── multilingual_test_TIMESTAMP.json           # Kết quả đa ngôn ngữ (4.3.4.3)
└── multilingual_table_TIMESTAMP.csv           # Bảng kết quả đa ngôn ngữ (CSV)
```

**Response Quality Testing (test_response_quality.py):**
```
├── response_quality_test_TIMESTAMP.json       # Kết quả chất lượng phản hồi
├── response_quality_table_TIMESTAMP.csv       # Bảng đánh giá chất lượng (CSV)
└── response_quality_test_results_TIMESTAMP.log # Log file chi tiết
```

**Comprehensive Testing (test_comprehensive.py):**
```
├── comprehensive_test_results_TIMESTAMP.log   # Log tổng hợp
└── comprehensive_test_results_TIMESTAMP.json  # JSON báo cáo tổng hợp
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

#### Báo cáo CSV (Theo yêu cầu 4.3.3.1, 4.3.3.2, 4.3.4.1, 4.3.4.2, 4.3.4.3)

**Performance Testing:**
- **response_time_table_TIMESTAMP.csv**: Bảng thời gian phản hồi theo format yêu cầu 4.3.3.1
- **resource_usage_table_TIMESTAMP.csv**: Bảng sử dụng tài nguyên theo format yêu cầu 4.3.3.2

**Accuracy Testing:**
- **expert_evaluation_table_TIMESTAMP.csv**: Bảng đánh giá chuyên gia theo format yêu cầu 4.3.4.1
- **search_accuracy_table_TIMESTAMP.csv**: Bảng metrics tìm kiếm theo format yêu cầu 4.3.4.2
- **multilingual_table_TIMESTAMP.csv**: Bảng kết quả đa ngôn ngữ theo format yêu cầu 4.3.4.3

**Response Quality Testing:**
- **response_quality_table_TIMESTAMP.csv**: Bảng đánh giá chất lượng phản hồi

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
