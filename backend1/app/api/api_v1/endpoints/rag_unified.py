#!/usr/bin/env python3
"""
RAG Unified API Endpoint - API duy nhất cho tất cả query/response
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import torch
from sqlalchemy.orm import Session

from app.services.rag_service_unified import get_rag_service_unified
from app.services.chat_service_unified import get_chat_service_unified
from app.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic Models
class UnifiedQueryRequest(BaseModel):
    """Request model cho unified query API"""
    question: str = Field(..., description="Câu hỏi cần trả lời", min_length=1, max_length=1000)
    top_k: Optional[int] = Field(default=5, description="Số lượng nguồn tài liệu tối đa", ge=1, le=20)
    filter_category: Optional[str] = Field(default=None, description="Lọc theo danh mục: 'luat', 'english', 'vietnamese', 'all'")
    include_sources: Optional[bool] = Field(default=True, description="Có bao gồm thông tin nguồn tài liệu không")
    similarity_threshold: Optional[float] = Field(default=None, description="Ngưỡng độ tương đồng tối thiểu", ge=0.0, le=1.0)

class SourceInfo(BaseModel):
    """Thông tin nguồn tài liệu"""
    filename: str
    display_name: str
    category: str
    content_preview: str
    similarity_score: float
    content_length: int

class UnifiedQueryResponse(BaseModel):
    """Response model cho unified query API"""
    question: str
    answer: str
    sources: List[SourceInfo]
    total_sources: int
    confidence: float = Field(..., description="Độ tin cậy của câu trả lời (0-1)")
    method: str = Field(..., description="Phương pháp tạo câu trả lời")
    processing_time_ms: int
    filter_category: str
    timestamp: str
    service_version: str

class ServiceStats(BaseModel):
    """Thống kê service"""
    service_name: str
    version: str
    status: str
    total_documents: int
    total_chunks: int
    categories: Dict[str, Any]
    device: str
    default_settings: Dict[str, Any]

# Chat-related models
class ChatRequest(BaseModel):
    """Request cho chat với lịch sử"""
    message: str = Field(..., description="Tin nhắn người dùng", min_length=1, max_length=2000)
    chat_id: Optional[int] = Field(None, description="ID cuộc trò chuyện hiện tại")
    user_id: Optional[int] = Field(None, description="ID người dùng")
    session_id: Optional[str] = Field(None, description="ID phiên trò chuyện")
    top_k: Optional[int] = Field(default=5, description="Số lượng nguồn tài liệu", ge=1, le=20)
    filter_category: Optional[str] = Field(default=None, description="Lọc theo danh mục")
    rag_settings: Optional[Dict[str, Any]] = Field(default=None, description="Cấu hình RAG tùy chỉnh")

class ChatResponse(BaseModel):
    """Response cho chat"""
    message_id: int
    chat_id: int
    user_message: str
    ai_response: str
    sources: List[SourceInfo]
    total_sources: int
    confidence: float
    processing_time_ms: int
    timestamp: str

class ChatHistoryResponse(BaseModel):
    """Response cho lịch sử chat"""
    chats: List[Dict[str, Any]]
    total: int
    page: int
    per_page: int
    filters: Dict[str, Any]

class ChatMessagesResponse(BaseModel):
    """Response cho tin nhắn chat"""
    messages: List[Dict[str, Any]]
    total: int
    page: int
    per_page: int

class ChatAnalyticsResponse(BaseModel):
    """Response cho analytics chat"""
    chat_id: int
    chat_info: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    sources_analysis: Dict[str, Any]
    timeline: List[Dict[str, Any]]

@router.post("/query", response_model=UnifiedQueryResponse, 
             summary="Query RAG Unified", 
             description="API duy nhất để hỏi đáp với toàn bộ tài liệu đã embedding")
async def unified_query(request: UnifiedQueryRequest):
    """
    **API Thống nhất cho Query/Response RAG**
    
    Đây là API duy nhất để:
    - Gửi câu hỏi và nhận câu trả lời từ toàn bộ knowledge base
    - Tìm kiếm trong tất cả tài liệu đã được embedding
    - Lọc theo danh mục tài liệu
    - Điều chỉnh độ chính xác và số lượng nguồn
    
    **Categories:**
    - `luat`: Tài liệu luật pháp Việt Nam
    - `english`: Tài liệu tiếng Anh (NIST, ISO)
    - `vietnamese`: Tài liệu tiếng Việt
    - `all` hoặc `null`: Tất cả tài liệu
    
    **Ví dụ câu hỏi:**
    - "An toàn thông tin là gì?"
    - "Luật An toàn thông tin quy định gì?"
    - "ISO 27001 có những yêu cầu nào?"
    - "Các biện pháp bảo mật cơ bản?"
    """
    try:
        logger.info(f"📝 Unified query: {request.question[:100]}...")
        
        # Get RAG service
        rag_service = await get_rag_service_unified()
        
        # Process query
        result = await rag_service.query(
            question=request.question,
            top_k=request.top_k,
            filter_category=request.filter_category,
            include_sources=request.include_sources,
            similarity_threshold=request.similarity_threshold
        )
        
        # Convert to response model
        sources = [SourceInfo(**source) for source in result.get('sources', [])]
        
        response = UnifiedQueryResponse(
            question=result['question'],
            answer=result['answer'],
            sources=sources,
            total_sources=result['total_sources'],
            confidence=result.get('confidence', 0.0),
            method=result.get('method', 'unified'),
            processing_time_ms=result.get('processing_time_ms', 0),
            filter_category=result.get('filter_category', 'all'),
            timestamp=result.get('timestamp', ''),
            service_version=result.get('service_version', '1.0.0')
        )
        
        logger.info(f"✅ Query processed: {response.total_sources} sources, {response.processing_time_ms}ms")
        return response
        
    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Lỗi dữ liệu đầu vào: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Unified query error: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý câu hỏi: {str(e)}")

@router.get("/stats", response_model=ServiceStats,
            summary="Service Statistics",
            description="Lấy thống kê chi tiết về RAG service")
async def get_service_stats():
    """
    **Thống kê RAG Service**
    
    Trả về thông tin chi tiết về:
    - Số lượng tài liệu và chunks
    - Phân bố theo danh mục
    - Cấu hình mặc định
    - Trạng thái service
    """
    try:
        rag_service = await get_rag_service_unified()
        stats = await rag_service.get_service_stats()
        
        return ServiceStats(
            service_name=stats['service_name'],
            version=stats['version'],
            status=stats['status'],
            total_documents=stats['total_documents'],
            total_chunks=stats['total_chunks'],
            categories=stats['categories'],
            device=stats['device'],
            default_settings=stats['default_settings']
        )
        
    except Exception as e:
        logger.error(f"❌ Stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi lấy thống kê: {str(e)}")

@router.get("/health",
            summary="Health Check",
            description="Kiểm tra trạng thái sức khỏe của RAG service")
async def health_check():
    """
    **Health Check**
    
    Kiểm tra:
    - Service có sẵn sàng không
    - Thời gian khởi tạo
    - Thông tin cơ bản
    """
    try:
        rag_service = await get_rag_service_unified()
        stats = await rag_service.get_service_stats()
        
        return {
            "status": "healthy",
            "service": "RAG Unified",
            "version": "1.0.0",
            "ready": stats.get('status') == 'ready',
            "total_documents": stats.get('total_documents', 0),
            "total_chunks": stats.get('total_chunks', 0),
            "initialization_time": stats.get('initialization_time', 0)
        }
        
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return {
            "status": "unhealthy",
            "service": "RAG Unified",
            "version": "1.0.0",
            "error": str(e)
        }

@router.get("/categories",
            summary="Available Categories",
            description="Lấy danh sách các danh mục tài liệu có sẵn")
async def get_categories():
    """
    **Danh mục tài liệu có sẵn**
    
    Trả về danh sách các category có thể sử dụng để filter
    """
    try:
        rag_service = await get_rag_service_unified()
        stats = await rag_service.get_service_stats()
        
        categories = []
        for cat_id, cat_info in stats.get('categories', {}).items():
            categories.append({
                'id': cat_id,
                'name': {
                    'luat': 'Luật pháp Việt Nam',
                    'english': 'Tài liệu tiếng Anh',
                    'vietnamese': 'Tài liệu tiếng Việt'
                }.get(cat_id, cat_id.title()),
                'chunks': cat_info.get('chunks', 0),
                'total_length': cat_info.get('total_length', 0)
            })
        
        return {
            'categories': categories,
            'total_categories': len(categories),
            'note': 'Sử dụng filter_category="all" để tìm trong tất cả danh mục'
        }
        
    except Exception as e:
        logger.error(f"❌ Categories error: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi lấy danh mục: {str(e)}")

# Compatibility endpoints (deprecated)
@router.post("/query/simple", 
             deprecated=True,
             summary="[DEPRECATED] Simple Query",
             description="Sử dụng /query thay thế")
async def simple_query_deprecated(question: str = Query(..., description="Câu hỏi")):
    """Endpoint tương thích ngược - khuyến nghị sử dụng /query"""
    request = UnifiedQueryRequest(question=question)
    return await unified_query(request)

@router.get("/info",
            summary="Service Information", 
            description="Thông tin tổng quan về RAG Unified API")
async def service_info():
    """
    **Thông tin RAG Unified API**
    
    API duy nhất để truy vấn toàn bộ knowledge base
    """
    return {
        "name": "RAG Unified API",
        "version": "1.0.0",
        "description": "API thống nhất cho query/response từ toàn bộ tài liệu đã embedding",
        "main_endpoint": "/api/v1/rag/query",
        "features": [
            "Tìm kiếm thông minh với embedding vectors",
            "Lọc theo danh mục tài liệu", 
            "Điều chỉnh độ chính xác và số lượng kết quả",
            "Trả về câu trả lời chi tiết với nguồn tham khảo",
            "Thống kê và monitoring"
        ],
        "supported_categories": ["luat", "english", "vietnamese", "all"],
        "example_questions": [
            "An toàn thông tin là gì?",
            "Luật An toàn thông tin quy định gì?", 
            "ISO 27001 có những yêu cầu nào?",
            "Các biện pháp bảo mật cơ bản?"
        ]
    }

# ===== CHAT HISTORY ENDPOINTS =====

@router.post("/chat", response_model=ChatResponse,
             summary="Chat với lịch sử", 
             description="Gửi tin nhắn và lưu lịch sử trò chuyện")
async def chat_with_history(request: ChatRequest, db: Session = Depends(get_db)):
    """
    **Chat với lưu lịch sử trò chuyện**
    
    Tính năng:
    - Gửi tin nhắn và nhận phản hồi từ RAG
    - Tự động lưu lịch sử trò chuyện
    - Theo dõi sources và confidence
    - Hỗ trợ session management
    
    **Workflow:**
    1. Tạo chat mới hoặc sử dụng chat hiện có
    2. Lưu tin nhắn người dùng
    3. Gọi RAG service để tạo phản hồi
    4. Lưu tin nhắn AI với metadata đầy đủ
    5. Trả về kết quả với thông tin chat
    """
    try:
        chat_service = get_chat_service_unified(db)
        
        # Xác định hoặc tạo chat
        if request.chat_id:
            chat_context = chat_service.get_chat_with_context(request.chat_id)
            if not chat_context:
                raise HTTPException(status_code=404, detail=f"Chat {request.chat_id} không tồn tại")
        else:
            # Tạo chat mới
            title = request.message[:50] + "..." if len(request.message) > 50 else request.message
            chat = chat_service.create_chat_with_rag_context(
                title=title,
                user_id=request.user_id,
                category_filter=request.filter_category,
                session_id=request.session_id,
                rag_settings=request.rag_settings
            )
            request.chat_id = chat.id
        
        # Gửi tin nhắn và nhận phản hồi
        result = await chat_service.send_message_with_rag(
            chat_id=request.chat_id,
            user_message=request.message,
            user_id=request.user_id,
            override_settings=request.rag_settings
        )
        
        # Chuẩn bị response
        sources = [SourceInfo(**source) for source in result["rag_response"].get("sources", [])]
        
        return ChatResponse(
            message_id=result["ai_message"].id,
            chat_id=request.chat_id,
            user_message=request.message,
            ai_response=result["rag_response"]["answer"],
            sources=sources,
            total_sources=result["rag_response"]["total_sources"],
            confidence=result["rag_response"].get("confidence", 0.0),
            processing_time_ms=result["rag_response"].get("processing_time_ms", 0),
            timestamp=result["rag_response"].get("timestamp", "")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi chat: {str(e)}")

@router.get("/chats", response_model=ChatHistoryResponse,
            summary="Lấy lịch sử chat",
            description="Lấy danh sách các cuộc trò chuyện với thống kê")
async def get_chat_history(
    page: int = Query(default=1, ge=1, description="Số trang"),
    per_page: int = Query(default=10, ge=1, le=100, description="Số item per trang"),
    user_id: Optional[int] = Query(default=None, description="ID người dùng"),
    category_filter: Optional[str] = Query(default=None, description="Lọc theo danh mục"),
    db: Session = Depends(get_db)
):
    """
    **Lấy lịch sử trò chuyện**
    
    Trả về:
    - Danh sách các cuộc trò chuyện
    - Thống kê tin nhắn, sources, confidence
    - Thông tin phân trang
    - Bộ lọc đã áp dụng
    """
    try:
        chat_service = get_chat_service_unified(db)
        result = chat_service.get_chats_with_stats(
            user_id=user_id,
            page=page,
            per_page=per_page,
            category_filter=category_filter
        )
        
        return ChatHistoryResponse(
            chats=result["chats"],
            total=result["total"],
            page=result["page"],
            per_page=result["per_page"],
            filters=result["filters"]
        )
        
    except Exception as e:
        logger.error(f"❌ Get chat history error: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi lấy lịch sử: {str(e)}")

@router.get("/chats/{chat_id}/messages", response_model=ChatMessagesResponse,
            summary="Lấy tin nhắn trong chat",
            description="Lấy danh sách tin nhắn trong một cuộc trò chuyện")
async def get_chat_messages(
    chat_id: int,
    page: int = Query(default=1, ge=1, description="Số trang"),
    per_page: int = Query(default=50, ge=1, le=100, description="Số item per trang"),
    db: Session = Depends(get_db)
):
    """
    **Lấy tin nhắn trong chat**
    
    Trả về:
    - Danh sách tin nhắn với đầy đủ metadata
    - Thông tin sources cho tin nhắn AI
    - Performance metrics
    - Phân trang
    """
    try:
        chat_service = get_chat_service_unified(db)
        
        # Kiểm tra chat tồn tại
        chat_context = chat_service.get_chat_with_context(chat_id)
        if not chat_context:
            raise HTTPException(status_code=404, detail=f"Chat {chat_id} không tồn tại")
        
        result = chat_service.get_chat_messages_with_sources(
            chat_id=chat_id,
            page=page,
            per_page=per_page
        )
        
        return ChatMessagesResponse(
            messages=result["messages"],
            total=result["total"],
            page=result["page"],
            per_page=result["per_page"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get chat messages error: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi lấy tin nhắn: {str(e)}")

@router.get("/chats/{chat_id}/analytics", response_model=ChatAnalyticsResponse,
            summary="Analytics cho chat",
            description="Lấy thống kê chi tiết và phân tích cho một cuộc trò chuyện")
async def get_chat_analytics(chat_id: int, db: Session = Depends(get_db)):
    """
    **Analytics chi tiết cho chat**
    
    Phân tích:
    - Performance metrics (confidence, processing time)
    - Sources analysis (tần suất sử dụng, điểm số)
    - Timeline của cuộc trò chuyện
    - Thống kê tổng quan
    """
    try:
        chat_service = get_chat_service_unified(db)
        result = chat_service.get_chat_analytics(chat_id)
        
        if "error" in result:
            if result["error"] == "Chat không tồn tại":
                raise HTTPException(status_code=404, detail="Chat không tồn tại")
            else:
                raise HTTPException(status_code=500, detail=result["error"])
        
        return ChatAnalyticsResponse(
            chat_id=result["chat_id"],
            chat_info=result["chat_info"],
            performance_metrics=result["performance_metrics"],
            sources_analysis=result["sources_analysis"],
            timeline=result["timeline"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get chat analytics error: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi analytics: {str(e)}")

@router.delete("/chats/{chat_id}",
               summary="Xóa chat",
               description="Xóa một cuộc trò chuyện (soft delete)")
async def delete_chat(chat_id: int, db: Session = Depends(get_db)):
    """
    **Xóa cuộc trò chuyện**
    
    - Soft delete: chat vẫn tồn tại trong DB nhưng bị đánh dấu xóa
    - Tất cả tin nhắn cũng bị ẩn
    - Không thể khôi phục qua API
    """
    try:
        chat_service = get_chat_service_unified(db)
        
        # Sử dụng method từ parent class
        success = chat_service.delete_chat(chat_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Chat {chat_id} không tồn tại")
        
        return {"message": f"Đã xóa chat {chat_id}", "success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Delete chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi xóa chat: {str(e)}")

@router.put("/chats/{chat_id}",
            summary="Cập nhật chat",
            description="Cập nhật thông tin cuộc trò chuyện")
async def update_chat(
    chat_id: int,
    title: Optional[str] = Query(default=None, description="Tiêu đề mới"),
    is_active: Optional[bool] = Query(default=None, description="Trạng thái hoạt động"),
    db: Session = Depends(get_db)
):
    """
    **Cập nhật cuộc trò chuyện**
    
    Có thể cập nhật:
    - Tiêu đề chat
    - Trạng thái hoạt động
    - Metadata (trong tương lai)
    """
    try:
        chat_service = get_chat_service_unified(db)
        
        # Chuẩn bị data cập nhật
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if is_active is not None:
            update_data["is_active"] = is_active
        
        if not update_data:
            raise HTTPException(status_code=400, detail="Không có dữ liệu để cập nhật")
        
        # Sử dụng method từ parent class
        updated_chat = chat_service.update_chat(chat_id, **update_data)
        
        if not updated_chat:
            raise HTTPException(status_code=404, detail=f"Chat {chat_id} không tồn tại")
        
        return {
            "message": f"Đã cập nhật chat {chat_id}",
            "chat": {
                "id": updated_chat.id,
                "title": updated_chat.title,
                "is_active": updated_chat.is_active,
                "updated_at": updated_chat.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Update chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi cập nhật chat: {str(e)}")

# ===== FILES MANAGEMENT =====

@router.get("/files/uploaded",
            summary="Lấy danh sách files đã upload",
            description="Lấy danh sách các file trong thư mục documents/upload")
async def get_uploaded_files():
    """
    **Lấy danh sách files đã upload**
    
    Trả về danh sách các file trong thư mục upload
    để hiển thị trong sidebar hoặc file manager
    """
    try:
        import os
        
        upload_dir = "documents/upload"
        
        # Kiểm tra thư mục có tồn tại không
        if not os.path.exists(upload_dir):
            return {
                "files": [],
                "total": 0,
                "message": "Thư mục upload chưa tồn tại"
            }
        
        # Lấy danh sách file trong thư mục
        files = []
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                # Lấy thông tin file
                stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "extension": filename.split('.')[-1].lower() if '.' in filename else ''
                })
        
        # Sắp xếp theo thời gian modified
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return {
            "files": files,
            "total": len(files),
            "upload_dir": upload_dir
        }
        
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách file upload: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi lấy files: {str(e)}")

# ===== DEBUG & ADMIN ENDPOINTS =====

@router.post("/debug/reload-llm",
             summary="Reload LLM Service",
             description="Force reload LLM service for debugging")
async def reload_llm_service():
    """
    **Force Reload LLM Service**
    
    Debug endpoint để reload LLM service
    Useful khi LLM không hoạt động
    """
    try:
        from app.services.rag_service_unified import _rag_service_unified
        
        if _rag_service_unified:
            # Reset LLM service
            _rag_service_unified.llm_service = None
            _rag_service_unified.use_llm_generation = True
            
            # Reinitialize
            await _rag_service_unified.initialize()
            
            # Check status
            llm_status = "available" if _rag_service_unified.llm_service else "not_available"
            
            return {
                "message": "LLM service reload attempted",
                "llm_status": llm_status,
                "use_llm_generation": _rag_service_unified.use_llm_generation
            }
        else:
            return {
                "message": "RAG service not initialized yet",
                "llm_status": "unknown"
            }
            
    except Exception as e:
        logger.error(f"❌ Reload LLM error: {e}")
        return {
            "message": f"Reload failed: {str(e)}",
            "llm_status": "error"
        }

@router.get("/debug/llm-status",
            summary="Check LLM Status",
            description="Kiểm tra trạng thái LLM service")
async def check_llm_status():
    """
    **Check LLM Service Status**
    
    Debug endpoint để kiểm tra:
    - LLM service có được load không
    - Memory usage
    - Configuration
    """
    try:
        from app.services.rag_service_unified import _rag_service_unified
        
        if not _rag_service_unified:
            return {
                "status": "rag_service_not_initialized",
                "llm_available": False
            }
        
        # Check LLM service
        llm_available = _rag_service_unified.llm_service is not None
        use_llm = _rag_service_unified.use_llm_generation
        
        # GPU info
        gpu_info = {}
        if torch.cuda.is_available():
            device = torch.cuda.current_device()
            total_memory = torch.cuda.get_device_properties(device).total_memory / 1024**3
            allocated_memory = torch.cuda.memory_allocated(device) / 1024**3
            
            gpu_info = {
                "gpu_name": torch.cuda.get_device_name(device),
                "total_memory_gb": round(total_memory, 2),
                "allocated_memory_gb": round(allocated_memory, 2),
                "free_memory_gb": round(total_memory - allocated_memory, 2)
            }
        
        return {
            "status": "initialized",
            "llm_available": llm_available,
            "use_llm_generation": use_llm,
            "gpu_info": gpu_info,
            "model_path": "D:/Vian/MODELS/vinallama-2.7b-chat"
        }
        
    except Exception as e:
        logger.error(f"❌ LLM status check error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
