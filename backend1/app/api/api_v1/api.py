# app/api/api_v1/api.py
# File chính để tổng hợp tất cả các API routers
# Include tất cả các router con vào API chính

from fastapi import APIRouter, HTTPException
from app.api.api_v1.endpoints import health, rag_unified, file_upload

api_router = APIRouter()

# Redirect endpoints cho backward compatibility
@api_router.get("/chatbot/status/enhanced", deprecated=True)
async def chatbot_status_redirect():
    """[DEPRECATED] Redirect to new RAG unified health"""
    return {
        "status": "moved",
        "message": "This endpoint has been moved to /api/v1/rag/health",
        "new_endpoint": "/api/v1/rag/health",
        "deprecated": True
    }

@api_router.post("/chatbot/query/fixed", deprecated=True)
async def chatbot_query_redirect():
    """[DEPRECATED] Redirect to new RAG unified query"""
    return {
        "status": "moved",
        "message": "This endpoint has been moved to /api/v1/rag/query",
        "new_endpoint": "/api/v1/rag/query",
        "deprecated": True
    }

@api_router.get("/chatbot/health/fixed", deprecated=True)
async def chatbot_health_redirect():
    """[DEPRECATED] Redirect to new RAG unified health"""
    return {
        "status": "moved", 
        "message": "This endpoint has been moved to /api/v1/rag/health",
        "new_endpoint": "/api/v1/rag/health",
        "deprecated": True
    }

# Include các router con
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(rag_unified.router, prefix="/rag", tags=["rag-unified"])
api_router.include_router(file_upload.router, prefix="/files", tags=["file-upload"])