# app/services/chat_service.py
# Service để quản lý chức năng chat và lịch sử trò chuyện

from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.models.chat import Chat, ChatMessage, ChatSession
from app.schemas.chat import (
    ChatCreate, ChatUpdate, ChatResponse,
    ChatMessageCreate, ChatMessageUpdate, ChatMessageResponse,
    ChatSessionCreate, ChatSessionResponse
)

logger = logging.getLogger(__name__)

class ChatService:
    """Service để quản lý chức năng chat"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ===== Chat Session Management =====
    
    def create_session(self, user_id: Optional[int] = None, ip_address: Optional[str] = None, 
                      user_agent: Optional[str] = None) -> ChatSession:
        """Tạo phiên trò chuyện mới"""
        try:
            session_id = str(uuid.uuid4())
            expires_at = datetime.utcnow() + timedelta(hours=24)  # Hết hạn sau 24h
            
            session = ChatSession(
                session_id=session_id,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=expires_at
            )
            
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            
            logger.info(f"Tạo session mới: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo session: {e}")
            self.db.rollback()
            raise
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Lấy session theo ID"""
        try:
            return self.db.query(ChatSession).filter(
                and_(
                    ChatSession.session_id == session_id,
                    ChatSession.is_active == True,
                    ChatSession.is_deleted == False
                )
            ).first()
        except Exception as e:
            logger.error(f"Lỗi khi lấy session {session_id}: {e}")
            return None
    
    # ===== Chat Management =====
    
    def create_chat(self, title: str, user_id: Optional[int] = None, 
                   category_filter: Optional[str] = None, 
                   session_id: Optional[str] = None) -> Chat:
        """Tạo cuộc trò chuyện mới"""
        try:
            chat = Chat(
                title=title,
                user_id=user_id,
                category_filter=category_filter
            )
            
            self.db.add(chat)
            self.db.commit()
            self.db.refresh(chat)
            
            logger.info(f"Tạo chat mới: {chat.id} - {title}")
            return chat
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo chat: {e}")
            self.db.rollback()
            raise
    
    def get_chat(self, chat_id: int) -> Optional[Chat]:
        """Lấy chat theo ID"""
        try:
            return self.db.query(Chat).filter(
                and_(
                    Chat.id == chat_id,
                    Chat.is_deleted == False
                )
            ).first()
        except Exception as e:
            logger.error(f"Lỗi khi lấy chat {chat_id}: {e}")
            return None
    
    def get_chats(self, user_id: Optional[int] = None, page: int = 1, 
                  per_page: int = 10, is_active: Optional[bool] = None) -> Dict[str, Any]:
        """Lấy danh sách chats với phân trang"""
        try:
            query = self.db.query(Chat).filter(Chat.is_deleted == False)
            
            # Lọc theo user_id
            if user_id is not None:
                query = query.filter(Chat.user_id == user_id)
            
            # Lọc theo trạng thái active
            if is_active is not None:
                query = query.filter(Chat.is_active == is_active)
            
            # Đếm tổng số
            total = query.count()
            
            # Phân trang
            offset = (page - 1) * per_page
            chats = query.order_by(desc(Chat.updated_at)).offset(offset).limit(per_page).all()
            
            # Thêm thông tin bổ sung cho mỗi chat
            chat_responses = []
            for chat in chats:
                # Đếm số tin nhắn
                message_count = self.db.query(ChatMessage).filter(
                    and_(
                        ChatMessage.chat_id == chat.id,
                        ChatMessage.is_deleted == False
                    )
                ).count()
                
                # Lấy tin nhắn cuối
                last_message = self.db.query(ChatMessage).filter(
                    and_(
                        ChatMessage.chat_id == chat.id,
                        ChatMessage.is_deleted == False
                    )
                ).order_by(desc(ChatMessage.created_at)).first()
                
                chat_dict = {
                    "id": chat.id,
                    "title": chat.title,
                    "user_id": chat.user_id,
                    "category_filter": chat.category_filter,
                    "is_active": chat.is_active,
                    "metadata_json": chat.metadata_json,
                    "created_at": chat.created_at,
                    "updated_at": chat.updated_at,
                    "message_count": message_count,
                    "last_message_at": last_message.created_at if last_message else None
                }
                chat_responses.append(chat_dict)
            
            return {
                "chats": chat_responses,
                "total": total,
                "page": page,
                "per_page": per_page
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy danh sách chats: {e}")
            raise
    
    def update_chat(self, chat_id: int, **kwargs) -> Optional[Chat]:
        """Cập nhật chat"""
        try:
            chat = self.get_chat(chat_id)
            if not chat:
                return None
            
            for key, value in kwargs.items():
                if hasattr(chat, key):
                    setattr(chat, key, value)
            
            self.db.commit()
            self.db.refresh(chat)
            
            logger.info(f"Cập nhật chat {chat_id}")
            return chat
            
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật chat {chat_id}: {e}")
            self.db.rollback()
            raise
    
    def delete_chat(self, chat_id: int) -> bool:
        """Xóa chat (soft delete)"""
        try:
            chat = self.get_chat(chat_id)
            if not chat:
                return False
            
            chat.is_deleted = True
            self.db.commit()
            
            logger.info(f"Xóa chat {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi xóa chat {chat_id}: {e}")
            self.db.rollback()
            return False
    
    # ===== Chat Message Management =====
    
    def create_message(self, chat_id: int, role: str, content: str, 
                      message_type: str = "text", response_metadata: Optional[Dict] = None,
                      processing_time: Optional[int] = None) -> ChatMessage:
        """Tạo tin nhắn mới"""
        try:
            message = ChatMessage(
                chat_id=chat_id,
                role=role,
                content=content,
                message_type=message_type,
                response_metadata=response_metadata,
                processing_time=processing_time
            )
            
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            
            logger.info(f"Tạo tin nhắn mới: {message.id} trong chat {chat_id}")
            return message
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo tin nhắn: {e}")
            self.db.rollback()
            raise
    
    def get_messages(self, chat_id: int, page: int = 1, per_page: int = 50) -> Dict[str, Any]:
        """Lấy danh sách tin nhắn trong chat"""
        try:
            query = self.db.query(ChatMessage).filter(
                and_(
                    ChatMessage.chat_id == chat_id,
                    ChatMessage.is_deleted == False
                )
            )
            
            # Đếm tổng số
            total = query.count()
            
            # Phân trang
            offset = (page - 1) * per_page
            messages = query.order_by(ChatMessage.created_at).offset(offset).limit(per_page).all()
            
            return {
                "messages": messages,
                "total": total,
                "page": page,
                "per_page": per_page
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy tin nhắn chat {chat_id}: {e}")
            raise
    
    def get_recent_messages(self, chat_id: int, limit: int = 10) -> List[ChatMessage]:
        """Lấy tin nhắn gần nhất trong chat"""
        try:
            return self.db.query(ChatMessage).filter(
                and_(
                    ChatMessage.chat_id == chat_id,
                    ChatMessage.is_deleted == False
                )
            ).order_by(desc(ChatMessage.created_at)).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy tin nhắn gần nhất chat {chat_id}: {e}")
            return []
    
    def format_chat_history(self, messages: List[ChatMessage]) -> List[Dict[str, str]]:
        """Chuyển đổi tin nhắn thành format chat history cho LLM"""
        try:
            history = []
            for message in messages:
                history.append({
                    "role": message.role,
                    "content": message.content
                })
            return history
            
        except Exception as e:
            logger.error(f"Lỗi khi format chat history: {e}")
            return []
    
    # ===== Utility Methods =====
    
    def get_or_create_chat(self, title: str, user_id: Optional[int] = None,
                          category_filter: Optional[str] = None) -> Chat:
        """Lấy hoặc tạo chat mới nếu chưa có"""
        try:
            # Tìm chat active gần nhất của user
            recent_chat = self.db.query(Chat).filter(
                and_(
                    Chat.user_id == user_id,
                    Chat.is_active == True,
                    Chat.is_deleted == False
                )
            ).order_by(desc(Chat.updated_at)).first()
            
            # Nếu có chat gần nhất và chưa có tin nhắn nào, dùng lại
            if recent_chat:
                message_count = self.db.query(ChatMessage).filter(
                    and_(
                        ChatMessage.chat_id == recent_chat.id,
                        ChatMessage.is_deleted == False
                    )
                ).count()
                
                if message_count == 0:
                    # Cập nhật tiêu đề nếu cần
                    if recent_chat.title != title:
                        recent_chat.title = title
                        self.db.commit()
                    return recent_chat
            
            # Tạo chat mới
            return self.create_chat(title, user_id, category_filter)
            
        except Exception as e:
            logger.error(f"Lỗi trong get_or_create_chat: {e}")
            raise
