# Hướng Dẫn Kết Nối Frontend1 với Backend1

## 🚀 Cách Khởi Chạy Hệ Thống

### 1. Khởi chạy Backend1

```bash
# Di chuyển vào thư mục backend1
cd backend1

# Kích hoạt virtual environment
conda activate vian

# Khởi chạy backend1
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend1 sẽ chạy tại: http://localhost:8000

### 2. Khởi chạy Frontend1

```bash
# Di chuyển vào thư mục frontend1
cd frontend1

# Cài đặt dependencies (nếu chưa có)
npm install

# Khởi chạy frontend1
npm run dev
```

Frontend1 sẽ chạy tại: http://localhost:5173

## 🔧 Cấu Hình Kết Nối

### Environment Variables

Tạo file `.env` trong thư mục frontend1:

```env
# Backend1 API URL
REACT_APP_API_URL=http://localhost:8000

# Timeout settings
REACT_APP_API_TIMEOUT=30000
REACT_APP_API_RETRY_ATTEMPTS=3
```

### API Endpoints

Frontend1 đã được cấu hình để kết nối với các endpoints sau của Backend1:

#### Health Check
- `GET /api/v1/health/` - Health check cơ bản
- `GET /api/v1/health/detailed` - Health check chi tiết
- `GET /api/v1/health/ready` - Readiness check
- `GET /api/v1/health/live` - Liveness check

#### Chatbot (Basic RAG)
- `POST /api/v1/chatbot/chat` - Chat với RAG system
- `POST /api/v1/chatbot/query` - Hỏi đáp với context
- `GET /api/v1/chatbot/stats` - Thống kê knowledge base
- `POST /api/v1/chatbot/build-knowledge-base` - Xây dựng KB
- `GET /api/v1/chatbot/categories` - Lấy danh sách categories

#### Enhanced Chatbot
- `POST /api/v1/chatbot/enhanced` - Chat với enhanced RAG
- `POST /api/v1/chatbot/enhanced/stream` - Streaming response
- `GET /api/v1/chatbot/status/enhanced` - Trạng thái hệ thống
- `GET /api/v1/chatbot/device/enhanced` - Thông tin thiết bị

## 🧪 Test Kết Nối

### 1. Kiểm tra Connection Status

Trong giao diện Frontend1, bạn sẽ thấy:
- **Connection Status**: Hiển thị trạng thái kết nối với Backend1
- **System Info**: Thông tin chi tiết về hệ thống Backend1
- **Real-time Updates**: Cập nhật trạng thái mỗi 30 giây

### 2. Test Chat Functionality

1. **Basic Chat**: Gửi tin nhắn thông thường
2. **Enhanced Chat**: Sử dụng streaming response
3. **RAG Mode**: Bật/tắt chế độ RAG
4. **Category Filter**: Lọc theo danh mục tài liệu

### 3. Test API Endpoints

Bạn có thể test trực tiếp các endpoints bằng cách truy cập:

- http://localhost:8000/docs - Swagger UI
- http://localhost:8000/redoc - ReDoc documentation
- http://localhost:8000/api/v1/health/ - Health check

## 🐛 Troubleshooting

### Lỗi Kết Nối

1. **Connection Refused**
   - Kiểm tra Backend1 có đang chạy không
   - Kiểm tra port 8000 có bị chiếm dụng không
   - Kiểm tra firewall settings

2. **CORS Error**
   - Backend1 đã được cấu hình CORS cho localhost:5173
   - Nếu vẫn lỗi, kiểm tra cấu hình CORS trong backend1/app/core/config.py

3. **Timeout Error**
   - Tăng timeout trong frontend1/src/utils/constants.jsx
   - Kiểm tra kết nối mạng

### Lỗi API

1. **404 Not Found**
   - Kiểm tra endpoint URL
   - Kiểm tra API version (/api/v1/)

2. **500 Internal Server Error**
   - Kiểm tra logs của Backend1
   - Kiểm tra models đã được load chưa

3. **Model Not Loaded**
   - Chạy initialization: `POST /api/v1/chatbot/initialize/enhanced`
   - Kiểm tra model paths trong config

## 📊 Monitoring

### Connection Status Panel

Frontend1 hiển thị:
- ✅ **Connected**: Kết nối thành công
- ❌ **Disconnected**: Mất kết nối
- 🔄 **Loading**: Đang kiểm tra kết nối
- 📋 **Details**: Thông tin chi tiết hệ thống

### System Information

- **Health Status**: Trạng thái sức khỏe Backend1
- **Database Status**: Trạng thái database
- **Model Status**: Trạng thái các models
- **Device Info**: Thông tin GPU/CPU
- **FAISS Status**: Trạng thái vector store

## 🔄 Auto-Reconnection

Frontend1 tự động:
- Kiểm tra kết nối mỗi 30 giây
- Hiển thị thông báo khi mất kết nối
- Cho phép retry manual
- Tự động kết nối lại khi Backend1 online

## 📝 Logs

### Backend1 Logs
```bash
# Xem logs trong terminal khi chạy uvicorn
# Hoặc kiểm tra file log nếu được cấu hình
```

### Frontend1 Logs
```bash
# Mở Developer Tools (F12)
# Xem Console tab để debug
# Network tab để kiểm tra API calls
```

## 🚀 Production Deployment

### Backend1
```bash
# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend1
```bash
# Build production
npm run build

# Serve static files
npm run preview
```

### Environment Variables
```env
# Production
REACT_APP_API_URL=https://your-backend-domain.com
```

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra logs của cả Frontend1 và Backend1
2. Đảm bảo cả hai service đều đang chạy
3. Kiểm tra network connectivity
4. Xem Connection Status panel trong Frontend1
