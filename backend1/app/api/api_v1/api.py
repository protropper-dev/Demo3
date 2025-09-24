# app/api/api_v1/api.py
# File chính để tổng hợp tất cả các API routers
# Include tất cả các router con vào API chính

from fastapi import APIRouter, HTTPException
from app.api.api_v1.endpoints import health, rag_unified, file_upload, chat_endpoints, file_management, admin_debug

api_router = APIRouter()

# Deprecated endpoints đã được xóa vì frontend đã cập nhật sử dụng endpoint mới

# Include các router con
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(rag_unified.router, prefix="/rag", tags=["rag-unified"])

# File management endpoints - sử dụng file_management.py (mới hơn)
api_router.include_router(file_management.router, prefix="/files", tags=["file-management"])

# Chat endpoints
api_router.include_router(chat_endpoints.router, prefix="/chat", tags=["chat"])

# Admin & debug endpoints
api_router.include_router(admin_debug.router, prefix="/admin", tags=["admin"])

# File upload endpoints - sử dụng prefix khác để tránh conflict
api_router.include_router(file_upload.router, prefix="/upload", tags=["file-upload"])