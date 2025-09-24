# RAG System Backend - FastAPI

Hệ thống RAG (Retrieval-Augmented Generation) sử dụng FastAPI, tích hợp LLM và vector search để trả lời câu hỏi dựa trên tài liệu.

## 🎯 Tính năng chính

- **RAG System**: Hỏi đáp thông minh dựa trên tài liệu
- **Vector Search**: FAISS index cho tìm kiếm nhanh
- **LLM Integration**: VinALLaMA-2.7b-chat cho sinh câu trả lời
- **Document Processing**: OCR, chunking, embedding
- **Chat History**: Lưu trữ lịch sử hội thoại
- **File Management**: Upload, quản lý tài liệu
- **Admin Tools**: Monitoring, debug, system management

## 📁 Cấu trúc dự án

```
backend1/
├── app/                          # Package chính của ứng dụng
│   ├── api/                      # API endpoints
│   │   └── api_v1/              # API version 1
│   │       ├── api.py           # Router chính
│   │       └── endpoints/       # Các endpoint handlers
│   │           ├── rag_unified.py      # RAG core endpoints
│   │           ├── chat_endpoints.py   # Chat management
│   │           ├── file_management.py  # File operations
│   │           ├── admin_debug.py      # Admin & debug tools
│   │           ├── health.py           # Health checks
│   │           └── file_upload.py      # File upload (legacy)
│   ├── core/                    # Core functionality
│   │   ├── config.py           # Cấu hình ứng dụng
│   │   ├── database.py         # Database connection
│   │   ├── models.py           # Database models
│   │   └── paths.py            # Path management
│   ├── models/                  # Database models
│   │   ├── base.py             # Base model
│   │   └── chat.py             # Chat models
│   ├── schemas/                 # Pydantic schemas
│   │   ├── base.py             # Base schemas
│   │   └── chat.py             # Chat schemas
│   ├── services/                # Business logic
│   │   ├── rag_service_unified.py    # RAG service chính
│   │   ├── rag_service_fixed.py      # RAG service backup
│   │   ├── chat_service_unified.py   # Chat service
│   │   └── file_service.py           # File service
│   ├── utils/                   # Utility functions
│   │   ├── rag_utils.py        # RAG utilities
│   │   ├── model_utils.py      # Model utilities
│   │   └── helpers.py          # Helper functions
│   └── middleware/              # Custom middleware
│       ├── logging.py          # Logging middleware
│       └── security.py         # Security middleware
├── data/                        # Vector store & embeddings
│   ├── all_faiss.index         # FAISS index
│   ├── all_embeddings.pkl      # Embeddings data
│   └── embeddings/             # Individual embeddings
├── documents/                   # Document storage
│   ├── Luat/                   # Legal documents
│   ├── TaiLieuTiengAnh/        # English documents
│   ├── TaiLieuTiengViet/       # Vietnamese documents
│   └── uploads/                # Uploaded documents
├── models/                      # AI models (cần download)
│   ├── multilingual_e5_large/  # Embedding model
│   └── vinallama-2.7b-chat/    # LLM model
├── alembic/                     # Database migrations
├── main.py                     # Entry point
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
└── README.md                   # Documentation
```

## 🚀 Hướng dẫn cài đặt và chạy

### **Bước 1: Chuẩn bị môi trường**

```bash
# Tạo virtual environment (khuyến nghị sử dụng conda)
conda create -n rag-system python=3.11
conda activate rag-system

# Hoặc sử dụng venv
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### **Bước 2: Cài đặt dependencies**

```bash
# Cài đặt Python packages
pip install -r requirements.txt

# Cài đặt Tesseract OCR (Windows)
# Download từ: https://github.com/UB-Mannheim/tesseract/wiki
# Hoặc sử dụng chocolatey:
choco install tesseract

# Cài đặt Tesseract OCR (Ubuntu/Debian)
sudo apt-get install tesseract-ocr tesseract-ocr-vie
```

### **Bước 3: Tạo file cấu hình**

```bash
# Tạo file .env trong thư mục backend1/
touch .env
```

**Nội dung file `.env`:**
```env
# Database
DATABASE_URL=sqlite:///./app.db

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO

# Model paths (cần download models)
EMBEDDING_MODEL_PATH=models/multilingual_e5_large
LLM_MODEL_PATH=models/vinallama-2.7b-chat

# Document paths
DOCUMENTS_PATH=../documents
DOCUMENTS_UPLOAD_DIR=documents/upload

# Vector store
FAISS_PATH=data/all_faiss.index
PICKLE_PATH=data/all_embeddings.pkl

# OCR
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe

# RAG settings
TOP_K_RESULTS=10
SIMILARITY_THRESHOLD=0.3
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Model settings
USE_QUANTIZATION=false
MAX_MEMORY=90%
DEVICE=cuda:0
GPU_MEMORY_FRACTION=0.8

# Generation settings
LLM_MAX_TOKENS=512
LLM_TEMPERATURE=0.7
```

### **Bước 4: Tạo thư mục cần thiết**

```bash
# Tạo các thư mục hệ thống
mkdir logs
mkdir temp
mkdir cache
mkdir documents\upload

# Tạo thư mục models (sẽ download models vào đây)
mkdir models
```

### **Bước 5: Khởi tạo database**

```bash
# Chạy migration để tạo database
alembic upgrade head

# Hoặc reset database nếu cần
python reset_db.py
```

### **Bước 6: Download AI Models**

**⚠️ QUAN TRỌNG: Cần download 2 models chính**

#### **6.1. Embedding Model (multilingual_e5_large)**
```bash
# Sử dụng Hugging Face
pip install transformers torch
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('intfloat/multilingual-e5-large')
model.save('models/multilingual_e5_large')
"
```

#### **6.2. LLM Model (vinallama-2.7b-chat)**
```bash
# Download từ Hugging Face
git lfs install
git clone https://huggingface.co/nguyenvulebinh/vinallama-2.7b-chat models/vinallama-2.7b-chat
```

### **Bước 7: Khởi tạo Knowledge Base**

```bash
# Chạy script khởi tạo knowledge base
python init_knowledge_base_standalone.py
```

### **Bước 8: Chạy ứng dụng**

```bash
# Development mode (với auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000

# Với workers (production)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### **Bước 9: Kiểm tra hệ thống**

```bash
# Kiểm tra health
curl http://localhost:8000/api/v1/health/

# Kiểm tra system info
curl http://localhost:8000/api/v1/admin/system-info

# Kiểm tra LLM status
curl http://localhost:8000/api/v1/admin/llm-status
```

## 📚 API Documentation

Sau khi chạy ứng dụng, truy cập:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 API Endpoints

### **RAG System**
- `POST /api/v1/rag/query` - Hỏi đáp với RAG system
- `GET /api/v1/rag/health` - Kiểm tra trạng thái RAG
- `GET /api/v1/rag/stats` - Thống kê RAG service
- `GET /api/v1/rag/categories` - Danh sách categories

### **Chat Management**
- `POST /api/v1/chat/send` - Gửi tin nhắn chat
- `GET /api/v1/chat/history` - Lấy lịch sử chat
- `GET /api/v1/chat/{chat_id}/messages` - Lấy tin nhắn trong chat
- `GET /api/v1/chat/{chat_id}/analytics` - Phân tích chat
- `PUT /api/v1/chat/{chat_id}` - Cập nhật chat
- `DELETE /api/v1/chat/{chat_id}` - Xóa chat

### **File Management**
- `GET /api/v1/files/uploaded` - Danh sách files đã upload
- `POST /api/v1/files/upload` - Upload file mới
- `DELETE /api/v1/files/{file_id}` - Xóa file
- `GET /api/v1/files/{file_id}` - Thông tin file
- `GET /api/v1/files/stats` - Thống kê files

### **Admin & Debug**
- `GET /api/v1/admin/system-info` - Thông tin hệ thống
- `GET /api/v1/admin/llm-status` - Trạng thái LLM
- `POST /api/v1/admin/reload-llm` - Reload LLM service
- `POST /api/v1/admin/rebuild-index` - Rebuild FAISS index
- `GET /api/v1/admin/memory-usage` - Memory usage
- `GET /api/v1/admin/config` - Cấu hình hệ thống

### **Health Checks**
- `GET /api/v1/health/` - Health check cơ bản
- `GET /api/v1/health/detailed` - Health check chi tiết
- `GET /api/v1/health/ready` - Readiness check
- `GET /api/v1/health/live` - Liveness check

## 🧪 Testing

```bash
# Chạy tất cả tests
pytest

# Chạy tests với coverage
pytest --cov=app

# Chạy tests cụ thể
pytest tests/test_rag.py
pytest tests/test_chat.py
```

## 🗄️ Database Migrations

```bash
# Tạo migration mới
alembic revision --autogenerate -m "Description of changes"

# Chạy migration
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Xem lịch sử migration
alembic history
```

## ⚙️ Troubleshooting

### **Lỗi thường gặp:**

#### **1. Models không load được**
```bash
# Kiểm tra LLM status
curl http://localhost:8000/api/v1/admin/llm-status

# Reload LLM service
curl -X POST http://localhost:8000/api/v1/admin/reload-llm
```

#### **2. FAISS index bị lỗi**
```bash
# Rebuild index
curl -X POST http://localhost:8000/api/v1/admin/rebuild-index
```

#### **3. Memory issues**
```bash
# Kiểm tra memory usage
curl http://localhost:8000/api/v1/admin/memory-usage

# Giảm GPU memory fraction trong .env
GPU_MEMORY_FRACTION=0.6
```

#### **4. OCR không hoạt động**
```bash
# Kiểm tra Tesseract path trong .env
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe

# Test Tesseract
tesseract --version
```

### **Performance Tuning:**

#### **1. GPU Memory**
```env
# Giảm memory usage
GPU_MEMORY_FRACTION=0.7
MAX_MEMORY=80%
USE_QUANTIZATION=true
```

#### **2. RAG Settings**
```env
# Tối ưu performance
TOP_K_RESULTS=5
CHUNK_SIZE=800
CHUNK_OVERLAP=100
SIMILARITY_THRESHOLD=0.4
```

## 🔄 Development Workflow

### **Thêm tính năng mới:**

1. **Tạo model** trong `app/models/` (nếu cần database)
2. **Tạo schema** trong `app/schemas/`
3. **Tạo service** trong `app/services/`
4. **Tạo endpoint** trong `app/api/api_v1/endpoints/`
5. **Thêm router** vào `app/api/api_v1/api.py`
6. **Tạo migration**: `alembic revision --autogenerate -m "Add new feature"`
7. **Viết tests** trong `tests/`

### **Debug workflow:**

1. **Kiểm tra logs**: `tail -f logs/app.log`
2. **Monitor system**: `GET /api/v1/admin/system-info`
3. **Check LLM**: `GET /api/v1/admin/llm-status`
4. **Memory usage**: `GET /api/v1/admin/memory-usage`
5. **Reload service**: `POST /api/v1/admin/reload-llm`

## 📊 System Requirements

### **Minimum:**
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 20GB free space
- **GPU**: NVIDIA GTX 1060 (6GB VRAM)

### **Recommended:**
- **CPU**: 8 cores
- **RAM**: 16GB
- **Storage**: 50GB free space
- **GPU**: NVIDIA RTX 3080 (10GB VRAM) hoặc cao hơn

### **Software:**
- **Python**: 3.11+
- **CUDA**: 11.8+ (nếu sử dụng GPU)
- **Tesseract OCR**: 5.0+
- **Git LFS**: Để download models

## 🚀 Production Deployment

### **Docker (Recommended):**
```bash
# Build image
docker build -t rag-system .

# Run container
docker run -p 8000:8000 --gpus all rag-system
```

### **Systemd Service:**
```bash
# Tạo service file
sudo nano /etc/systemd/system/rag-system.service

# Enable và start
sudo systemctl enable rag-system
sudo systemctl start rag-system
```

### **Nginx Reverse Proxy:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📝 Lưu ý quan trọng

- **Models**: Cần download 2 models chính (embedding + LLM)
- **GPU**: Khuyến nghị sử dụng GPU để tăng tốc độ
- **Memory**: Monitor memory usage, đặc biệt với LLM
- **Security**: Trong production, cần thêm authentication
- **Backup**: Backup database và vector store định kỳ
- **Monitoring**: Sử dụng admin endpoints để monitor hệ thống
