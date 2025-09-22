# app/schemas/chat.py
# Pydantic schemas cho chức năng chat và lịch sử trò chuyện

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.schemas.base import BaseSchema, TimestampSchema

# ===== Chat Schemas =====

class ChatBase(BaseSchema):
    """Base schema cho Chat"""
    title: str = Field(..., max_length=255, description="Tiêu đề cuộc trò chuyện")
    user_id: Optional[int] = Field(None, description="ID người dùng")
    category_filter: Optional[str] = Field(None, max_length=100, description="Bộ lọc danh mục")
    is_active: bool = Field(True, description="Trạng thái hoạt động")
    metadata_json: Optional[Dict[str, Any]] = Field(None, description="Metadata bổ sung")

class ChatCreate(ChatBase):
    """Schema để tạo Chat mới"""
    pass

class ChatUpdate(BaseSchema):
    """Schema để cập nhật Chat"""
    title: Optional[str] = Field(None, max_length=255, description="Tiêu đề cuộc trò chuyện")
    is_active: Optional[bool] = Field(None, description="Trạng thái hoạt động")
    metadata_json: Optional[Dict[str, Any]] = Field(None, description="Metadata bổ sung")

class ChatResponse(ChatBase, TimestampSchema):
    """Schema response cho Chat"""
    id: int = Field(..., description="ID cuộc trò chuyện")
    message_count: Optional[int] = Field(None, description="Số lượng tin nhắn")
    last_message_at: Optional[datetime] = Field(None, description="Thời gian tin nhắn cuối")

    class Config:
        from_attributes = True

class ChatListResponse(BaseSchema):
    """Schema response cho danh sách Chat"""
    chats: List[ChatResponse] = Field(..., description="Danh sách cuộc trò chuyện")
    total: int = Field(..., description="Tổng số cuộc trò chuyện")
    page: int = Field(..., description="Trang hiện tại")
    per_page: int = Field(..., description="Số item per trang")

# ===== ChatMessage Schemas =====

class ChatMessageBase(BaseSchema):
    """Base schema cho ChatMessage"""
    role: str = Field(..., max_length=20, description="Vai trò: user, assistant, system")
    content: str = Field(..., description="Nội dung tin nhắn")
    message_type: str = Field("text", max_length=50, description="Loại tin nhắn")
    response_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata của response AI")
    processing_time: Optional[int] = Field(None, description="Thời gian xử lý (ms)")

class ChatMessageCreate(ChatMessageBase):
    """Schema để tạo ChatMessage mới"""
    chat_id: int = Field(..., description="ID cuộc trò chuyện")

class ChatMessageUpdate(BaseSchema):
    """Schema để cập nhật ChatMessage"""
    content: Optional[str] = Field(None, description="Nội dung tin nhắn")
    response_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata của response AI")

class ChatMessageResponse(ChatMessageBase, TimestampSchema):
    """Schema response cho ChatMessage"""
    id: int = Field(..., description="ID tin nhắn")
    chat_id: int = Field(..., description="ID cuộc trò chuyện")

    class Config:
        from_attributes = True

class ChatMessageListResponse(BaseSchema):
    """Schema response cho danh sách ChatMessage"""
    messages: List[ChatMessageResponse] = Field(..., description="Danh sách tin nhắn")
    total: int = Field(..., description="Tổng số tin nhắn")
    page: int = Field(..., description="Trang hiện tại")
    per_page: int = Field(..., description="Số item per trang")

# ===== Chat Session Schemas =====

class ChatSessionBase(BaseSchema):
    """Base schema cho ChatSession"""
    session_id: str = Field(..., max_length=255, description="ID phiên trò chuyện")
    user_id: Optional[int] = Field(None, description="ID người dùng")
    ip_address: Optional[str] = Field(None, max_length=45, description="Địa chỉ IP")
    user_agent: Optional[str] = Field(None, description="User Agent string")
    is_active: bool = Field(True, description="Trạng thái phiên")
    expires_at: Optional[datetime] = Field(None, description="Thời gian hết hạn phiên")

class ChatSessionCreate(ChatSessionBase):
    """Schema để tạo ChatSession mới"""
    pass

class ChatSessionResponse(ChatSessionBase, TimestampSchema):
    """Schema response cho ChatSession"""
    id: int = Field(..., description="ID phiên")

    class Config:
        from_attributes = True

# ===== Request/Response Schemas cho API =====

class ChatRequest(BaseSchema):
    """Schema cho request chat"""
    message: str = Field(..., description="Tin nhắn người dùng")
    chat_history: Optional[List[Dict[str, str]]] = Field(None, description="Lịch sử trò chuyện")
    filter_category: Optional[str] = Field(None, description="Bộ lọc danh mục")
    chat_id: Optional[int] = Field(None, description="ID cuộc trò chuyện hiện tại")

class ChatResponseWithSources(BaseSchema):
    """Schema cho response chat với sources"""
    response: str = Field(..., description="Câu trả lời từ AI")
    sources: List[Dict[str, Any]] = Field(..., description="Nguồn tham khảo")
    total_sources: int = Field(..., description="Tổng số nguồn")
    query: str = Field(..., description="Câu hỏi gốc")
    chat_id: Optional[int] = Field(None, description="ID cuộc trò chuyện")
    message_id: Optional[int] = Field(None, description="ID tin nhắn AI")
    processing_time: Optional[int] = Field(None, description="Thời gian xử lý (ms)")

class ChatHistoryRequest(BaseSchema):
    """Schema cho request lấy lịch sử chat"""
    page: int = Field(1, ge=1, description="Số trang")
    per_page: int = Field(10, ge=1, le=100, description="Số item per trang")
    user_id: Optional[int] = Field(None, description="ID người dùng")
    is_active: Optional[bool] = Field(None, description="Lọc theo trạng thái hoạt động")

class ChatTitleUpdateRequest(BaseSchema):
    """Schema cho request cập nhật tiêu đề chat"""
    title: str = Field(..., max_length=255, description="Tiêu đề mới")

# ===== Stream Response Schemas =====

class StreamToken(BaseSchema):
    """Schema cho streaming token"""
    type: str = Field(..., description="Loại token: start, token, end, error")
    content: Optional[str] = Field(None, description="Nội dung token")
    message: Optional[str] = Field(None, description="Thông báo")
    response_length: Optional[int] = Field(None, description="Độ dài response")
    chat_id: Optional[int] = Field(None, description="ID cuộc trò chuyện")
