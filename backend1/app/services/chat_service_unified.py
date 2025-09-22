#!/usr/bin/env python3
"""
Chat Service Unified - Tích hợp với RAG Unified API
Quản lý lịch sử trò chuyện với RAG system
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import uuid
import json

from app.core.database import get_db
from app.models.chat import Chat, ChatMessage, ChatSession
from app.schemas.chat import (
    ChatCreate, ChatUpdate, ChatResponse,
    ChatMessageCreate, ChatMessageUpdate, ChatMessageResponse,
    ChatSessionCreate, ChatSessionResponse
)
from app.services.rag_service_unified import get_rag_service_unified

logger = logging.getLogger(__name__)

class ChatServiceUnified:
    """Chat Service tích hợp với RAG Unified"""
    
    def __init__(self, db: Session):
        self.db = db
        self.rag_service = None
    
    async def get_rag_service(self):
        """Lấy RAG service instance"""
        if self.rag_service is None:
            self.rag_service = await get_rag_service_unified()
        return self.rag_service
    
    # ===== Chat Session Management =====
    
    def create_session(self, user_id: Optional[int] = None, ip_address: Optional[str] = None, 
                      user_agent: Optional[str] = None, metadata: Optional[Dict] = None) -> ChatSession:
        """Tạo phiên trò chuyện mới với metadata mở rộng"""
        try:
            session_id = str(uuid.uuid4())
            expires_at = datetime.utcnow() + timedelta(hours=24)  # Hết hạn sau 24h
            
            # Metadata mặc định
            default_metadata = {
                "created_by": "chat_service_unified",
                "version": "1.0.0",
                "features": ["rag_unified", "chat_history", "sources_tracking"]
            }
            
            if metadata:
                default_metadata.update(metadata)
            
            session = ChatSession(
                session_id=session_id,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=expires_at,
                metadata_json=default_metadata
            )
            
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            
            logger.info(f"Tạo session unified: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo session unified: {e}")
            self.db.rollback()
            raise
    
    def get_active_session(self, session_id: str) -> Optional[ChatSession]:
        """Lấy session active và chưa hết hạn"""
        try:
            return self.db.query(ChatSession).filter(
                and_(
                    ChatSession.session_id == session_id,
                    ChatSession.is_active == True,
                    ChatSession.is_deleted == False,
                    ChatSession.expires_at > datetime.utcnow()
                )
            ).first()
        except Exception as e:
            logger.error(f"Lỗi khi lấy session {session_id}: {e}")
            return None
    
    # ===== Enhanced Chat Management =====
    
    def create_chat_with_rag_context(self, title: str, user_id: Optional[int] = None, 
                                   category_filter: Optional[str] = None, 
                                   session_id: Optional[str] = None,
                                   rag_settings: Optional[Dict] = None) -> Chat:
        """Tạo chat mới với cấu hình RAG"""
        try:
            # Metadata cho chat với RAG context
            metadata = {
                "rag_settings": rag_settings or {
                    "top_k": 5,
                    "similarity_threshold": 0.3,
                    "include_sources": True
                },
                "category_filter": category_filter,
                "session_id": session_id,
                "chat_type": "rag_unified",
                "created_at": datetime.utcnow().isoformat()
            }
            
            chat = Chat(
                title=title,
                user_id=user_id,
                category_filter=category_filter,
                metadata_json=metadata
            )
            
            self.db.add(chat)
            self.db.commit()
            self.db.refresh(chat)
            
            logger.info(f"Tạo chat unified: {chat.id} - {title}")
            return chat
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo chat unified: {e}")
            self.db.rollback()
            raise
    
    def get_chat_with_context(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Lấy chat với đầy đủ context"""
        try:
            chat = self.db.query(Chat).filter(
                and_(
                    Chat.id == chat_id,
                    Chat.is_deleted == False
                )
            ).first()
            
            if not chat:
                return None
            
            # Đếm số tin nhắn
            message_count = self.db.query(ChatMessage).filter(
                and_(
                    ChatMessage.chat_id == chat_id,
                    ChatMessage.is_deleted == False
                )
            ).count()
            
            # Lấy tin nhắn cuối
            last_message = self.db.query(ChatMessage).filter(
                and_(
                    ChatMessage.chat_id == chat_id,
                    ChatMessage.is_deleted == False
                )
            ).order_by(desc(ChatMessage.created_at)).first()
            
            # Thống kê sources đã sử dụng
            sources_used = self.db.query(ChatMessage).filter(
                and_(
                    ChatMessage.chat_id == chat_id,
                    ChatMessage.role == "assistant",
                    ChatMessage.response_metadata.isnot(None),
                    ChatMessage.is_deleted == False
                )
            ).count()
            
            return {
                "chat": chat,
                "message_count": message_count,
                "last_message": last_message,
                "sources_used": sources_used,
                "rag_settings": chat.metadata_json.get("rag_settings", {}) if chat.metadata_json else {}
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy chat context {chat_id}: {e}")
            return None
    
    # ===== RAG-Enhanced Messaging =====
    
    async def send_message_with_rag(self, chat_id: int, user_message: str, 
                                  user_id: Optional[int] = None,
                                  override_settings: Optional[Dict] = None) -> Dict[str, Any]:
        """Gửi tin nhắn và nhận phản hồi từ RAG"""
        try:
            # Lấy chat context
            chat_context = self.get_chat_with_context(chat_id)
            if not chat_context:
                raise ValueError(f"Chat {chat_id} không tồn tại")
            
            chat = chat_context["chat"]
            rag_settings = chat_context["rag_settings"]
            
            # Override settings nếu có
            if override_settings:
                rag_settings.update(override_settings)
            
            # Lấy lịch sử chat gần nhất
            recent_messages = self.get_recent_messages_formatted(chat_id, limit=10)
            
            # Lưu tin nhắn user
            user_msg = self.create_message_enhanced(
                chat_id=chat_id,
                role="user",
                content=user_message,
                message_type="user_query",
                metadata={
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Gọi RAG service
            rag_service = await self.get_rag_service()
            
            rag_response = await rag_service.query(
                question=user_message,
                top_k=rag_settings.get("top_k", 5),
                filter_category=chat.category_filter,
                include_sources=rag_settings.get("include_sources", True),
                similarity_threshold=rag_settings.get("similarity_threshold", 0.3)
            )
            
            # Lưu tin nhắn AI với metadata đầy đủ
            ai_metadata = {
                "rag_response": {
                    "sources": rag_response.get("sources", []),
                    "total_sources": rag_response.get("total_sources", 0),
                    "confidence": rag_response.get("confidence", 0.0),
                    "method": rag_response.get("method", "unified"),
                    "filter_category": rag_response.get("filter_category", "all")
                },
                "processing_info": {
                    "processing_time_ms": rag_response.get("processing_time_ms", 0),
                    "timestamp": rag_response.get("timestamp", ""),
                    "service_version": rag_response.get("service_version", "1.0.0")
                }
            }
            
            ai_msg = self.create_message_enhanced(
                chat_id=chat_id,
                role="assistant",
                content=rag_response.get("answer", "Xin lỗi, không thể trả lời lúc này."),
                message_type="rag_response",
                metadata=ai_metadata,
                processing_time=rag_response.get("processing_time_ms", 0)
            )
            
            # Cập nhật chat timestamp
            chat.updated_at = datetime.utcnow()
            self.db.commit()
            
            return {
                "user_message": user_msg,
                "ai_message": ai_msg,
                "rag_response": rag_response,
                "chat_context": chat_context
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi gửi tin nhắn RAG: {e}")
            self.db.rollback()
            raise
    
    def create_message_enhanced(self, chat_id: int, role: str, content: str, 
                              message_type: str = "text", metadata: Optional[Dict] = None,
                              processing_time: Optional[int] = None) -> ChatMessage:
        """Tạo tin nhắn với metadata mở rộng"""
        try:
            message = ChatMessage(
                chat_id=chat_id,
                role=role,
                content=content,
                message_type=message_type,
                response_metadata=metadata,
                processing_time=processing_time
            )
            
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            
            logger.info(f"Tạo tin nhắn enhanced: {message.id} ({message_type})")
            return message
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo tin nhắn enhanced: {e}")
            self.db.rollback()
            raise
    
    def get_recent_messages_formatted(self, chat_id: int, limit: int = 10) -> List[Dict[str, str]]:
        """Lấy tin nhắn gần nhất với format cho RAG context"""
        try:
            messages = self.db.query(ChatMessage).filter(
                and_(
                    ChatMessage.chat_id == chat_id,
                    ChatMessage.is_deleted == False
                )
            ).order_by(desc(ChatMessage.created_at)).limit(limit).all()
            
            # Đảo ngược để có thứ tự chronological
            messages.reverse()
            
            formatted = []
            for msg in messages:
                formatted.append({
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat(),
                    "message_type": msg.message_type
                })
            
            return formatted
            
        except Exception as e:
            logger.error(f"Lỗi khi format tin nhắn: {e}")
            return []
    
    # ===== Enhanced Chat History =====
    
    def get_chats_with_stats(self, user_id: Optional[int] = None, page: int = 1, 
                           per_page: int = 10, category_filter: Optional[str] = None) -> Dict[str, Any]:
        """Lấy danh sách chat với thống kê RAG"""
        try:
            query = self.db.query(Chat).filter(Chat.is_deleted == False)
            
            # Lọc theo user_id
            if user_id is not None:
                query = query.filter(Chat.user_id == user_id)
            
            # Lọc theo category
            if category_filter:
                query = query.filter(Chat.category_filter == category_filter)
            
            # Đếm tổng số
            total = query.count()
            
            # Phân trang
            offset = (page - 1) * per_page
            chats = query.order_by(desc(Chat.updated_at)).offset(offset).limit(per_page).all()
            
            # Thêm thông tin thống kê cho mỗi chat
            chat_responses = []
            for chat in chats:
                # Thống kê tin nhắn
                message_stats = self.db.query(
                    ChatMessage.role,
                    func.count(ChatMessage.id).label('count')
                ).filter(
                    and_(
                        ChatMessage.chat_id == chat.id,
                        ChatMessage.is_deleted == False
                    )
                ).group_by(ChatMessage.role).all()
                
                # Thống kê sources
                sources_count = self.db.query(ChatMessage).filter(
                    and_(
                        ChatMessage.chat_id == chat.id,
                        ChatMessage.role == "assistant",
                        ChatMessage.response_metadata.isnot(None),
                        ChatMessage.is_deleted == False
                    )
                ).count()
                
                # Tin nhắn cuối
                last_message = self.db.query(ChatMessage).filter(
                    and_(
                        ChatMessage.chat_id == chat.id,
                        ChatMessage.is_deleted == False
                    )
                ).order_by(desc(ChatMessage.created_at)).first()
                
                # Tính average confidence nếu có
                avg_confidence = 0.0
                confidence_msgs = self.db.query(ChatMessage).filter(
                    and_(
                        ChatMessage.chat_id == chat.id,
                        ChatMessage.role == "assistant",
                        ChatMessage.response_metadata.isnot(None),
                        ChatMessage.is_deleted == False
                    )
                ).all()
                
                if confidence_msgs:
                    confidences = []
                    for msg in confidence_msgs:
                        if msg.response_metadata and 'rag_response' in msg.response_metadata:
                            conf = msg.response_metadata['rag_response'].get('confidence', 0.0)
                            confidences.append(conf)
                    
                    if confidences:
                        avg_confidence = sum(confidences) / len(confidences)
                
                chat_dict = {
                    "id": chat.id,
                    "title": chat.title,
                    "user_id": chat.user_id,
                    "category_filter": chat.category_filter,
                    "is_active": chat.is_active,
                    "metadata_json": chat.metadata_json,
                    "created_at": chat.created_at,
                    "updated_at": chat.updated_at,
                    "stats": {
                        "message_stats": {stat.role: stat.count for stat in message_stats},
                        "sources_used": sources_count,
                        "avg_confidence": round(avg_confidence, 3),
                        "last_message_at": last_message.created_at if last_message else None
                    }
                }
                chat_responses.append(chat_dict)
            
            return {
                "chats": chat_responses,
                "total": total,
                "page": page,
                "per_page": per_page,
                "filters": {
                    "user_id": user_id,
                    "category_filter": category_filter
                }
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy danh sách chats với stats: {e}")
            raise
    
    def get_chat_messages_with_sources(self, chat_id: int, page: int = 1, 
                                     per_page: int = 50) -> Dict[str, Any]:
        """Lấy tin nhắn chat với thông tin sources đầy đủ"""
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
            
            # Format messages với sources info
            formatted_messages = []
            for msg in messages:
                msg_dict = {
                    "id": msg.id,
                    "chat_id": msg.chat_id,
                    "role": msg.role,
                    "content": msg.content,
                    "message_type": msg.message_type,
                    "processing_time": msg.processing_time,
                    "created_at": msg.created_at,
                    "updated_at": msg.updated_at
                }
                
                # Thêm thông tin sources nếu là AI response
                if msg.role == "assistant" and msg.response_metadata:
                    rag_response = msg.response_metadata.get("rag_response", {})
                    msg_dict["sources_info"] = {
                        "total_sources": rag_response.get("total_sources", 0),
                        "confidence": rag_response.get("confidence", 0.0),
                        "method": rag_response.get("method", "unknown"),
                        "sources": rag_response.get("sources", [])
                    }
                    
                    processing_info = msg.response_metadata.get("processing_info", {})
                    msg_dict["processing_info"] = processing_info
                
                formatted_messages.append(msg_dict)
            
            return {
                "messages": formatted_messages,
                "total": total,
                "page": page,
                "per_page": per_page
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy tin nhắn với sources: {e}")
            raise
    
    # ===== Basic Chat CRUD Operations =====
    
    def get_chat(self, chat_id: int):
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
    
    def update_chat(self, chat_id: int, **kwargs):
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
                logger.warning(f"Chat {chat_id} không tồn tại")
                return False
            
            # Soft delete chat
            chat.is_deleted = True
            chat.updated_at = datetime.utcnow()
            
            # Soft delete tất cả messages trong chat
            self.db.query(ChatMessage).filter(
                ChatMessage.chat_id == chat_id
            ).update({
                'is_deleted': True,
                'updated_at': datetime.utcnow()
            })
            
            self.db.commit()
            
            logger.info(f"Đã xóa chat {chat_id} và tất cả messages")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi xóa chat {chat_id}: {e}")
            self.db.rollback()
            raise

    # ===== Analytics & Insights =====
    
    def get_chat_analytics(self, chat_id: int) -> Dict[str, Any]:
        """Lấy analytics chi tiết cho chat"""
        try:
            chat_context = self.get_chat_with_context(chat_id)
            if not chat_context:
                return {"error": "Chat không tồn tại"}
            
            # Thống kê tin nhắn theo thời gian
            messages = self.db.query(ChatMessage).filter(
                and_(
                    ChatMessage.chat_id == chat_id,
                    ChatMessage.is_deleted == False
                )
            ).order_by(ChatMessage.created_at).all()
            
            # Phân tích sources được sử dụng
            sources_analysis = {}
            confidence_scores = []
            processing_times = []
            
            for msg in messages:
                if msg.role == "assistant" and msg.response_metadata:
                    rag_response = msg.response_metadata.get("rag_response", {})
                    
                    # Thu thập confidence scores
                    conf = rag_response.get("confidence", 0.0)
                    if conf > 0:
                        confidence_scores.append(conf)
                    
                    # Thu thập processing times
                    if msg.processing_time:
                        processing_times.append(msg.processing_time)
                    
                    # Phân tích sources
                    sources = rag_response.get("sources", [])
                    for source in sources:
                        filename = source.get("filename", "unknown")
                        category = source.get("category", "unknown")
                        
                        if filename not in sources_analysis:
                            sources_analysis[filename] = {
                                "count": 0,
                                "category": category,
                                "avg_score": 0.0,
                                "scores": []
                            }
                        
                        sources_analysis[filename]["count"] += 1
                        score = source.get("similarity_score", 0.0)
                        sources_analysis[filename]["scores"].append(score)
            
            # Tính average cho sources
            for filename, data in sources_analysis.items():
                if data["scores"]:
                    data["avg_score"] = sum(data["scores"]) / len(data["scores"])
            
            return {
                "chat_id": chat_id,
                "chat_info": {
                    "title": chat_context["chat"].title,
                    "created_at": chat_context["chat"].created_at,
                    "message_count": chat_context["message_count"],
                    "category_filter": chat_context["chat"].category_filter
                },
                "performance_metrics": {
                    "avg_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0,
                    "min_confidence": min(confidence_scores) if confidence_scores else 0.0,
                    "max_confidence": max(confidence_scores) if confidence_scores else 0.0,
                    "avg_processing_time": sum(processing_times) / len(processing_times) if processing_times else 0,
                    "total_ai_responses": len(confidence_scores)
                },
                "sources_analysis": sources_analysis,
                "timeline": [
                    {
                        "timestamp": msg.created_at.isoformat(),
                        "role": msg.role,
                        "message_type": msg.message_type,
                        "content_length": len(msg.content)
                    }
                    for msg in messages
                ]
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy analytics: {e}")
            return {"error": str(e)}

# Global instance
_chat_service_unified = None

def get_chat_service_unified(db: Session) -> ChatServiceUnified:
    """Get ChatServiceUnified instance"""
    return ChatServiceUnified(db)
