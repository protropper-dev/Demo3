# app/models/chat.py
# Database models cho chức năng chat và lịch sử trò chuyện

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel

class Chat(BaseModel):
    """Model cho cuộc trò chuyện"""
    __tablename__ = "chats"
    
    title = Column(String(255), nullable=False, comment="Tiêu đề cuộc trò chuyện")
    user_id = Column(Integer, nullable=True, comment="ID người dùng (có thể null cho anonymous)")
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="SET NULL"), nullable=True, comment="ID phiên trò chuyện")
    category_filter = Column(String(100), nullable=True, comment="Bộ lọc danh mục được sử dụng")
    is_active = Column(Boolean, default=True, nullable=False, comment="Trạng thái hoạt động")
    metadata_json = Column(JSON, nullable=True, comment="Thông tin metadata bổ sung")
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="chat", cascade="all, delete-orphan")
    session = relationship("ChatSession", back_populates="chats")
    
    def __repr__(self):
        return f"<Chat(id={self.id}, title='{self.title}', user_id={self.user_id})>"

class ChatMessage(BaseModel):
    """Model cho tin nhắn trong cuộc trò chuyện"""
    __tablename__ = "chat_messages"
    
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, comment="ID cuộc trò chuyện")
    role = Column(String(20), nullable=False, comment="Vai trò: user, assistant, system")
    content = Column(Text, nullable=False, comment="Nội dung tin nhắn")
    message_type = Column(String(50), default="text", nullable=False, comment="Loại tin nhắn: text, image, file")
    
    # Thông tin về response từ AI
    response_metadata = Column(JSON, nullable=True, comment="Metadata của response AI (sources, tokens, etc.)")
    processing_time = Column(Integer, nullable=True, comment="Thời gian xử lý (ms)")
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, chat_id={self.chat_id}, role='{self.role}')>"

class ChatSession(BaseModel):
    """Model cho phiên trò chuyện (session)"""
    __tablename__ = "chat_sessions"
    
    session_id = Column(String(255), unique=True, nullable=False, comment="ID phiên trò chuyện")
    user_id = Column(Integer, nullable=True, comment="ID người dùng")
    ip_address = Column(String(45), nullable=True, comment="Địa chỉ IP")
    user_agent = Column(Text, nullable=True, comment="User Agent string")
    is_active = Column(Boolean, default=True, nullable=False, comment="Trạng thái phiên")
    expires_at = Column(DateTime(timezone=True), nullable=True, comment="Thời gian hết hạn phiên")
    
    # Relationships
    chats = relationship("Chat", back_populates="session")
    
    def __repr__(self):
        return f"<ChatSession(id={self.id}, session_id='{self.session_id}', user_id={self.user_id})>"
