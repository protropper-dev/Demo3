# app/schemas/base.py
# Base schema và các schema chung
# Định nghĩa các schema cơ bản được sử dụng chung trong toàn bộ ứng dụng

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BaseSchema(BaseModel):
    """Base schema với các trường chung"""
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TimestampSchema(BaseSchema):
    """Schema với timestamp"""
    created_at: datetime
    updated_at: datetime

class IDSchema(BaseSchema):
    """Schema chỉ chứa ID"""
    id: int

class MessageSchema(BaseSchema):
    """Schema cho thông báo"""
    message: str

class ErrorSchema(BaseSchema):
    """Schema cho lỗi"""
    error: str
    detail: Optional[str] = None
