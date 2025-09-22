# API Structure - Clean Version

## 🎯 Active APIs

Sau khi dọn dẹp, hệ thống chỉ giữ lại các API hoạt động và cần thiết:

### 1. **RAG Unified API** - `/api/v1/rag/` ⭐ MAIN API
**Mục đích**: API duy nhất để query/response từ toàn bộ knowledge base

**Endpoints:**
- `POST /api/v1/rag/query` - Query chính
- `GET /api/v1/rag/stats` - Thống kê service
- `GET /api/v1/rag/health` - Health check
- `GET /api/v1/rag/categories` - Danh sách categories
- `GET /api/v1/rag/info` - Thông tin service

**Features:**
- ✅ Tìm kiếm thông minh với FAISS embedding
- ✅ Filter theo category (luat, english, vietnamese, all)
- ✅ Confidence scoring
- ✅ Comprehensive response với sources
- ✅ Performance metrics

### 2. **Health API** - `/api/v1/health/`
**Mục đích**: Health checks cho monitoring

**Endpoints:**
- `GET /api/v1/health/` - Basic health
- `GET /api/v1/health/detailed` - Detailed health
- `GET /api/v1/health/ready` - Readiness probe
- `GET /api/v1/health/live` - Liveness probe

### 3. **Chatbot Fixed API** - `/api/v1/chatbot/` (Backup)
**Mục đích**: Backup API, tương thích với legacy

**Endpoints:**
- `POST /api/v1/chatbot/query/fixed` - Fixed query endpoint
- `GET /api/v1/chatbot/health/fixed` - Health check

## 🗑️ Removed APIs

Các API sau đã được xóa do không hoạt động:

### ❌ Items API (Deleted)
- **Lý do**: Chỉ là example endpoint, không cần thiết
- **Files removed**: `endpoints/items.py`

### ❌ Chatbot API (Deleted)
- **Lý do**: Không hoạt động (total_sources: 0, vector store issues)
- **Files removed**: `endpoints/chatbot.py`, `services/rag_service.py`

### ❌ Chatbot Enhanced API (Deleted)
- **Lý do**: Models không sẵn sàng, lỗi 4-bit/8-bit models
- **Files removed**: `endpoints/chatbot_enhanced.py`, `services/rag_service_enhanced.py`

## 🚀 Recommended Usage

### Primary API
```bash
curl -X POST "http://localhost:8000/api/v1/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "An toàn thông tin là gì?",
    "top_k": 5,
    "filter_category": "all",
    "include_sources": true
  }'
```

### Health Check
```bash
curl http://localhost:8000/api/v1/rag/health
```

### Service Stats
```bash
curl http://localhost:8000/api/v1/rag/stats
```

## 📊 API Comparison

| Feature | RAG Unified | Chatbot Fixed | Health |
|---------|-------------|---------------|--------|
| Status | ✅ Active | ⚠️ Backup | ✅ Active |
| Query Support | ✅ Full | ✅ Basic | ❌ N/A |
| Sources | ✅ Detailed | ✅ Basic | ❌ N/A |
| Filtering | ✅ Advanced | ⚠️ Limited | ❌ N/A |
| Performance | ✅ Optimized | ⚠️ Basic | ✅ Fast |
| Documentation | ✅ Complete | ⚠️ Limited | ✅ Complete |

## 🔧 Development Notes

- **Main development**: Focus on RAG Unified API
- **Testing**: Use `test_unified_api.py`
- **Monitoring**: Use health endpoints
- **Legacy support**: Chatbot Fixed available if needed

## 📈 Performance

After cleanup:
- **Reduced complexity**: 3 active APIs vs 6 previous
- **Better maintainability**: Only working code remains
- **Clear responsibility**: Each API has specific purpose
- **Improved documentation**: Focus on what works
