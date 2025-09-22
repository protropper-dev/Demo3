# app/models/base.py
# File chứa base model và các mixin chung
# Định nghĩa các trường và phương thức chung cho tất cả models

from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func
from app.core.database import Base

class TimestampMixin:
    """Mixin thêm timestamp cho các model"""
    
    @declared_attr
    def created_at(cls):
        return Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    @declared_attr
    def updated_at(cls):
        return Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class SoftDeleteMixin:
    """Mixin thêm soft delete cho các model"""
    
    @declared_attr
    def is_deleted(cls):
        return Column(Boolean, default=False, nullable=False)

class BaseModel(Base, TimestampMixin, SoftDeleteMixin):
    """Base model với các trường chung"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
