# app/schemas/__init__.py
# File khởi tạo package schemas
# Import tất cả các schema để sử dụng trong API

from .base import BaseSchema, TimestampSchema, IDSchema, MessageSchema, ErrorSchema
from .chat import (
    ChatBase, ChatCreate, ChatUpdate, ChatResponse, ChatListResponse,
    ChatMessageBase, ChatMessageCreate, ChatMessageUpdate, ChatMessageResponse, ChatMessageListResponse,
    ChatSessionBase, ChatSessionCreate, ChatSessionResponse,
    ChatRequest, ChatResponseWithSources, ChatHistoryRequest, ChatTitleUpdateRequest,
    StreamToken
)

__all__ = [
    "BaseSchema", "TimestampSchema", "IDSchema", "MessageSchema", "ErrorSchema",
    # Chat schemas
    "ChatBase", "ChatCreate", "ChatUpdate", "ChatResponse", "ChatListResponse",
    "ChatMessageBase", "ChatMessageCreate", "ChatMessageUpdate", "ChatMessageResponse", "ChatMessageListResponse",
    "ChatSessionBase", "ChatSessionCreate", "ChatSessionResponse",
    "ChatRequest", "ChatResponseWithSources", "ChatHistoryRequest", "ChatTitleUpdateRequest",
    "StreamToken"
]
