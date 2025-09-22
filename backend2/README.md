# Backend2 - Chatbot Security API

API backend cho chatbot an toàn thông tin, được xây dựng dựa trên dự án tham khảo và tối ưu cho cấu hình máy hiện tại.

## 🚀 Tính năng

- **Chat API**: Trả lời câu hỏi về an toàn thông tin dựa trên RAG (Retrieval-Augmented Generation)
- **Streaming Response**: Hỗ trợ streaming response cho trải nghiệm người dùng tốt hơn
- **File Upload**: Upload và quản lý tài liệu
- **System Status**: Kiểm tra trạng thái hệ thống và mô hình
- **Auto Device Detection**: Tự động phát hiện và sử dụng GPU/CPU phù hợp

## 📁 Cấu trúc thư mục

```
backend2/
├── main.py                 # Entry point chính
├── settings.py            # Cấu hình ứng dụng
├── consts.py              # Khởi tạo mô hình và constants
├── requirements.txt       # Dependencies
├── start_server.py        # Script khởi động server
├── models/                # Pydantic models
│   ├── __init__.py
│   └── chat.py
├── routes/                # API routes
│   ├── __init__.py
│   ├── chat.py           # Chat endpoints
│   ├── system.py         # System status
│   ├── file.py           # File management
│   └── embedding.py      # Embedding utilities
└── utils/                 # Utility functions
    ├── __init__.py
    ├── chat.py           # Chat logic và RAG
    ├── embedding.py      # PDF processing
    └── file.py           # File operations
```

## 🛠️ Cài đặt

### 1. Cài đặt dependencies

```bash
cd backend2
pip install -r requirements.txt
```

### 2. Cấu hình

Chỉnh sửa file `settings.py` để phù hợp với cấu hình máy của bạn:

```python
# Đường dẫn đến mô hình và dữ liệu
LLM_MODEL_FOLDER = ROOT_PROJECT / "backend" / "models"
EMBEDDING_FOLDER = ROOT_PROJECT / "backend" / "vector_store" / "embeddings"

# Cấu hình server
API_HOST = "0.0.0.0"
API_PORT = 8001
```

### 3. Khởi động server

```bash
python start_server.py
```

Hoặc:

```bash
python main.py
```

## 📡 API Endpoints

### Chat
- `POST /api/v1/chat` - Chat thông thường
- `POST /api/v1/chat/stream` - Chat với streaming

### System
- `GET /api/v1/status` - Kiểm tra trạng thái hệ thống
- `GET /api/v1/device` - Thông tin thiết bị

### File Management
- `POST /api/v1/upload` - Upload file
- `GET /api/v1/files` - Liệt kê files
- `DELETE /api/v1/files/{filename}` - Xóa file

### Embedding
- `GET /api/v1/embedding` - Kiểm tra embedding file
- `POST /api/v1/embedding/process` - Xử lý embedding

## 🔧 Cấu hình tối ưu

### GPU vs CPU
Backend tự động phát hiện và cấu hình:
- **GPU**: Sử dụng quantization 4-bit với BitsAndBytesConfig
- **CPU**: Sử dụng float32 với low_cpu_mem_usage

### Memory Optimization
- Sử dụng `low_cpu_mem_usage=True` cho CPU
- Quantization 4-bit cho GPU
- Efficient tokenization và chunking

## 📊 Monitoring

### System Status
```bash
curl http://localhost:8001/api/v1/status
```

### Health Check
```bash
curl http://localhost:8001/health
```

## 🐛 Troubleshooting

### Lỗi load model
1. Kiểm tra đường dẫn model trong `settings.py`
2. Đảm bảo model files tồn tại
3. Kiểm tra memory available

### Lỗi embedding
1. Kiểm tra file FAISS và pickle tồn tại
2. Đảm bảo embedding model được load thành công
3. Kiểm tra format của dữ liệu embedding

### Lỗi GPU
1. Kiểm tra CUDA installation
2. Kiểm tra GPU memory available
3. Fallback về CPU nếu cần

## 🔄 Migration từ Backend cũ

Backend2 được thiết kế để tương thích với:
- Dữ liệu embedding từ backend cũ
- Cấu trúc thư mục documents hiện tại
- Mô hình LLM đã có

Chỉ cần điều chỉnh đường dẫn trong `settings.py` để trỏ đến dữ liệu hiện tại.

## 📝 Notes

- Server chạy trên port 8001 để tránh conflict với backend cũ (port 8000)
- API documentation có sẵn tại `/docs`
- Hỗ trợ CORS cho frontend development
- Logging chi tiết cho debugging
