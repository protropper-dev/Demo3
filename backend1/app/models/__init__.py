# app/models/__init__.py
# Import tất cả models để đảm bảo chúng được đăng ký với SQLAlchemy

from .base import BaseModel, TimestampMixin, SoftDeleteMixin
from .chat import Chat, ChatMessage, ChatSession

# Export tất cả models
__all__ = [
    "BaseModel",
    "TimestampMixin", 
    "SoftDeleteMixin",
    "Chat",
    "ChatMessage", 
    "ChatSession"
]