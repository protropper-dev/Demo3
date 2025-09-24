#!/usr/bin/env python3
"""
Chat Endpoints - Quản lý chat và lịch sử trò chuyện
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
from sqlalchemy.orm import Session

from app.services.chat_service_unified import get_chat_service_unified
from app.core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

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

class SourceInfo(BaseModel):
    """Thông tin nguồn tài liệu"""
    filename: str
    display_name: str
    category: str
    content_preview: str
    similarity_score: float
    content_length: int

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
    enhancement_applied: Optional[bool] = Field(default=False, description="Có áp dụng LLM enhancement không")
    original_response: Optional[str] = Field(default=None, description="Response gốc trước khi enhancement")
    method: Optional[str] = Field(default="unified", description="Phương pháp tạo response")

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

@router.post("/send", response_model=ChatResponse,
             summary="Gửi tin nhắn chat", 
             description="Gửi tin nhắn và nhận phản hồi từ RAG với lưu lịch sử")
async def send_message(request: ChatRequest, db: Session = Depends(get_db)):
    """
    **Gửi tin nhắn chat với lưu lịch sử**
    
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
            timestamp=result["rag_response"].get("timestamp", ""),
            enhancement_applied=result["rag_response"].get("enhancement_applied", False),
            original_response=result["rag_response"].get("original_response", None),
            method=result["rag_response"].get("method", "unified")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi chat: {str(e)}")

@router.get("/history", response_model=ChatHistoryResponse,
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

@router.get("/{chat_id}/messages", response_model=ChatMessagesResponse,
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

@router.get("/{chat_id}/analytics", response_model=ChatAnalyticsResponse,
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

@router.delete("/{chat_id}",
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

@router.put("/{chat_id}",
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
