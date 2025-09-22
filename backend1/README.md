# FastAPI Backend

Dự án backend sử dụng FastAPI với cấu trúc chuẩn và đơn giản, không có hệ thống user account.

## Cấu trúc dự án

```
backend/
├── app/                          # Package chính của ứng dụng
│   ├── __init__.py
│   ├── api/                      # API endpoints
│   │   ├── __init__.py
│   │   └── api_v1/              # API version 1
│   │       ├── __init__.py
│   │       ├── api.py           # Router chính
│   │       └── endpoints/       # Các endpoint handlers
│   │           ├── __init__.py
│   │           ├── health.py    # Health check endpoints
│   │           └── items.py     # Items management endpoints (ví dụ)
│   ├── core/                    # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py           # Cấu hình ứng dụng
│   │   └── database.py         # Database connection
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   └── base.py             # Base model và mixins
│   ├── schemas/                 # Pydantic schemas
│   │   ├── __init__.py
│   │   └── base.py             # Base schemas
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   ├── helpers.py          # Helper functions
│   │   └── validators.py       # Validation functions
│   └── middleware/              # Custom middleware
│       ├── __init__.py
│       ├── logging.py          # Logging middleware
│       └── security.py         # Security middleware
├── alembic/                     # Database migrations
│   ├── versions/               # Migration files
│   ├── env.py                  # Alembic environment
│   └── script.py.mako          # Migration template
├── tests/                       # Test files
│   ├── __init__.py
│   ├── conftest.py             # Pytest configuration
│   └── test_items.py           # Items tests
├── main.py                     # Entry point
├── requirements.txt            # Python dependencies
├── env.example                 # Environment variables template
├── alembic.ini                 # Alembic configuration
└── README.md                   # Documentation
```

## Cài đặt và chạy

### 1. Tạo virtual environment

```bash
# Sử dụng conda (khuyến nghị)
conda create -n vian python=3.11
conda activate vian

# Hoặc sử dụng venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình environment

```bash
# Copy file mẫu
cp env.example .env

# Chỉnh sửa file .env với thông tin thực tế
```

### 4. Khởi tạo database

```bash
# Tạo migration đầu tiên
alembic revision --autogenerate -m "Initial migration"

# Chạy migration
alembic upgrade head
```

### 5. Chạy ứng dụng

```bash
# Development mode
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Sau khi chạy ứng dụng, truy cập:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Chạy tất cả tests
pytest

# Chạy tests với coverage
pytest --cov=app

# Chạy tests cụ thể
pytest tests/test_auth.py
```

## Database Migrations

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

## Tính năng chính

- ✅ FastAPI framework
- ✅ SQLAlchemy ORM với Alembic migrations
- ✅ CORS middleware
- ✅ Request/Response logging
- ✅ Security headers
- ✅ Rate limiting
- ✅ Input validation với Pydantic
- ✅ Comprehensive testing
- ✅ API documentation tự động
- ✅ Health check endpoints
- ✅ Error handling
- ✅ Environment configuration
- ✅ File upload support
- ✅ Utility functions và validators

## Cấu trúc API

### Health Check
- `GET /api/v1/health/` - Health check cơ bản
- `GET /api/v1/health/detailed` - Health check chi tiết
- `GET /api/v1/health/ready` - Readiness check
- `GET /api/v1/health/live` - Liveness check

### Items (Ví dụ)
- `GET /api/v1/items/` - Lấy danh sách items
- `GET /api/v1/items/{item_id}` - Lấy thông tin item theo ID
- `POST /api/v1/items/` - Tạo item mới
- `PUT /api/v1/items/{item_id}` - Cập nhật thông tin item
- `DELETE /api/v1/items/{item_id}` - Xóa item

## Mở rộng

Để thêm tính năng mới:

1. Tạo model trong `app/models/` (nếu cần database)
2. Tạo schema trong `app/schemas/`
3. Tạo endpoint trong `app/api/api_v1/endpoints/`
4. Thêm router vào `app/api/api_v1/api.py`
5. Tạo migration nếu cần: `alembic revision --autogenerate -m "Add new feature"`
6. Viết tests trong `tests/`

## Lưu ý

- Dự án này không có hệ thống authentication/user management
- Có thể dễ dàng thêm authentication sau nếu cần
- Tất cả endpoints hiện tại đều public (không cần xác thực)
- Items endpoint chỉ là ví dụ, có thể thay thế bằng logic nghiệp vụ thực tế
