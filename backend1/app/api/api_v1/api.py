# app/api/api_v1/api.py
# File chính để tổng hợp tất cả các API routers
# Include tất cả các router con vào API chính

from fastapi import APIRouter
from app.api.api_v1.endpoints import health, chatbot_fixed, rag_unified

api_router = APIRouter()

# Include các router con
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(rag_unified.router, prefix="/rag", tags=["rag-unified"])
api_router.include_router(chatbot_fixed.router, prefix="/chatbot", tags=["chatbot-fixed"])