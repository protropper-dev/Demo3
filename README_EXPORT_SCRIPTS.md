# Hướng Dẫn Xuất Dữ Liệu Câu Hỏi và Câu Trả Lời

## Tổng Quan

Có 2 script Python được tạo để xuất 100 câu hỏi từ file `test_performance.py` thành các file JSON và CSV với format `{query: ..., response: ...}`:

1. **`export_questions_responses.py`** - Script chính kết nối với API để lấy câu trả lời thực
2. **`demo_export_questions.py`** - Script demo tạo dữ liệu mẫu (không cần API)

## Cấu Trúc Dữ Liệu

### Format JSON
```json
[
  {
    "query": "An toàn thông tin là gì?",
    "response": "An toàn thông tin là việc bảo vệ thông tin và hệ thống thông tin khỏi các mối đe dọa..."
  },
  {
    "query": "Firewall là gì?",
    "response": "Firewall là một hệ thống bảo mật mạng được thiết kế để kiểm soát và giám sát..."
  }
]
```

### Format CSV
```csv
query,response
"An toàn thông tin là gì?","An toàn thông tin là việc bảo vệ thông tin và hệ thống thông tin khỏi các mối đe dọa..."
"Firewall là gì?","Firewall là một hệ thống bảo mật mạng được thiết kế để kiểm soát và giám sát..."
```

## 100 Câu Hỏi Được Trích Xuất

Script trích xuất 100 câu hỏi từ hàm `_generate_100_test_questions()` trong file `test_performance.py`, bao gồm:

- **Câu hỏi cơ bản (1-20)**: Các khái niệm cơ bản về an toàn thông tin
- **Câu hỏi về luật pháp Việt Nam (21-40)**: Luật, nghị định, thông tư về an toàn thông tin
- **Câu hỏi về tiêu chuẩn quốc tế (41-60)**: ISO, NIST, OWASP, etc.
- **Câu hỏi kỹ thuật phức tạp (61-80)**: Blockchain, Zero Trust, AI, etc.
- **Câu hỏi chuyên sâu (81-100)**: So sánh, phân tích, triển khai, etc.

## Cách Sử Dụng

### 1. Script Demo (Không cần API)

```bash
python demo_export_questions.py
```

**Kết quả:**
- Tạo file JSON và CSV với dữ liệu mẫu
- Không cần backend đang chạy
- Dùng để test format và cấu trúc dữ liệu

### 2. Script Chính (Cần API)

```bash
python export_questions_responses.py
```

**Yêu cầu:**
- Backend API phải đang chạy tại `http://localhost:8000`
- Endpoint `/api/v1/rag/query` phải hoạt động

**Kết quả:**
- Tạo file JSON và CSV với câu trả lời thực từ AI
- Thời gian chạy: ~2-3 phút (do có delay giữa các requests)
- Hiển thị tóm tắt kết quả và tỷ lệ thành công

## Cấu Hình

### Thay Đổi URL API

Trong file `export_questions_responses.py`, bạn có thể thay đổi URL API:

```python
exporter = QuestionResponseExporter(base_url="http://your-api-url:port")
```

### Thay Đổi Tên File Output

```python
# JSON
json_filename = exporter.save_to_json(data, "my_custom_name.json")

# CSV  
csv_filename = exporter.save_to_csv(data, "my_custom_name.csv")
```

## Kết Quả Mong Đợi

### File JSON
- Tên file: `questions_responses_YYYYMMDD_HHMMSS.json`
- Format: Array of objects với `query` và `response`
- Encoding: UTF-8

### File CSV
- Tên file: `questions_responses_YYYYMMDD_HHMMSS.csv`
- Header: `query,response`
- Encoding: UTF-8

### Log Output
```
BẮT ĐẦU XUẤT 100 CÂU HỎI VÀ CÂU TRẢ LỜI
============================================================
Đang xử lý câu hỏi 1/100: An toàn thông tin là gì?...
Đang xử lý câu hỏi 2/100: Mật khẩu mạnh có đặc điểm gì?...
...
============================================================
TÓM TẮT KẾT QUẢ XUẤT DỮ LIỆU
============================================================
Tổng số câu hỏi: 100
Thành công: 95
Thất bại: 5
Tỷ lệ thành công: 95.0%
```

## Xử Lý Lỗi

### Lỗi Kết Nối API
- Kiểm tra backend có đang chạy không
- Kiểm tra URL API có đúng không
- Kiểm tra firewall và network

### Lỗi Timeout
- Tăng thời gian timeout trong aiohttp
- Giảm delay giữa các requests
- Chạy từng batch nhỏ

### Lỗi Encoding
- Đảm bảo file được lưu với encoding UTF-8
- Kiểm tra ký tự đặc biệt trong câu hỏi/câu trả lời

## Ví Dụ Sử Dụng Dữ Liệu

### Đọc File JSON
```python
import json

with open('questions_responses_20241201_143022.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    print(f"Q: {item['query']}")
    print(f"A: {item['response']}")
    print("-" * 50)
```

### Đọc File CSV
```python
import csv

with open('questions_responses_20241201_143022.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"Q: {row['query']}")
        print(f"A: {row['response']}")
        print("-" * 50)
```

## Lưu Ý

1. **Thời gian chạy**: Script chính cần 2-3 phút do có delay giữa các requests
2. **Tài nguyên**: Mỗi request sử dụng tài nguyên API, tránh chạy đồng thời nhiều script
3. **Dữ liệu**: Câu trả lời phụ thuộc vào chất lượng knowledge base và model AI
4. **Backup**: Nên backup dữ liệu gốc trước khi chạy script
5. **Testing**: Nên chạy script demo trước để kiểm tra format

## Hỗ Trợ

Nếu gặp vấn đề:
1. Kiểm tra log output để xem lỗi cụ thể
2. Chạy script demo trước để test
3. Kiểm tra kết nối API
4. Xem file README chính của project
