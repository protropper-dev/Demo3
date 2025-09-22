# app/api/api_v1/endpoints/chatbot_fixed.py
# Endpoint RAG đã được sửa

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from app.services.rag_service_fixed import get_rag_service_fixed

logger = logging.getLogger(__name__)

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5
    filter_category: Optional[str] = None

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list
    total_sources: int

@router.post("/query/fixed", response_model=QueryResponse)
async def query_fixed(request: QueryRequest):
    """Query endpoint đã được sửa"""
    try:
        rag_service = await get_rag_service_fixed()
        result = await rag_service.query(
            question=request.question,
            top_k=request.top_k,
            filter_category=request.filter_category
        )
        
        return QueryResponse(
            question=result["question"],
            answer=result["answer"],
            sources=result.get("sources", []),
            total_sources=result.get("total_sources", 0)
        )
        
    except Exception as e:
        logger.error(f"Lỗi trong query fixed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health/fixed")
async def health_fixed():
    """Health check cho fixed endpoint"""
    return {
        "status": "healthy",
        "service": "chatbot-fixed",
        "version": "1.0.0"
    }

# Compatibility redirects for old endpoints
@router.get("/status/enhanced", deprecated=True)
async def status_enhanced_redirect():
    """[DEPRECATED] Redirect to new RAG unified health"""
    return {
        "status": "moved",
        "message": "This endpoint has been moved to /api/v1/rag/health",
        "new_endpoint": "/api/v1/rag/health",
        "deprecated": True
    }