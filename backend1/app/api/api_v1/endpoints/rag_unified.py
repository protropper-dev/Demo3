#!/usr/bin/env python3
"""
RAG Unified API Endpoint - Core RAG functionality only
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

from app.services.rag_service_unified import get_rag_service_unified

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic Models
class UnifiedQueryRequest(BaseModel):
    """Request model cho unified query API"""
    question: str = Field(..., description="Câu hỏi cần trả lời", min_length=1, max_length=1000)
    top_k: Optional[int] = Field(default=5, description="Số lượng nguồn tài liệu tối đa", ge=1, le=20)
    filter_category: Optional[str] = Field(default=None, description="Lọc theo danh mục: 'luat', 'english', 'vietnamese', 'all'")
    include_sources: Optional[bool] = Field(default=True, description="Có bao gồm thông tin nguồn tài liệu không")
    similarity_threshold: Optional[float] = Field(default=None, description="Ngưỡng độ tương đồng tối thiểu", ge=0.0, le=1.0)
    use_enhancement: Optional[bool] = Field(default=True, description="Sử dụng LLM enhancement để nâng cao chất lượng response")

class SourceInfo(BaseModel):
    """Thông tin nguồn tài liệu"""
    filename: str
    display_name: str
    category: str
    content_preview: str
    similarity_score: float
    content_length: int

class UnifiedQueryResponse(BaseModel):
    """Response model cho unified query API"""
    question: str
    answer: str
    sources: List[SourceInfo]
    total_sources: int
    confidence: float = Field(..., description="Độ tin cậy của câu trả lời (0-1)")
    method: str = Field(..., description="Phương pháp tạo câu trả lời")
    processing_time_ms: int
    filter_category: str
    timestamp: str
    service_version: str
    enhancement_applied: Optional[bool] = Field(default=False, description="Có áp dụng LLM enhancement không")
    original_response: Optional[str] = Field(default=None, description="Response gốc trước khi enhancement")

class ServiceStats(BaseModel):
    """Thống kê service"""
    service_name: str
    version: str
    status: str
    total_documents: int
    total_chunks: int
    categories: Dict[str, Any]
    device: str
    default_settings: Dict[str, Any]

# Core RAG models only

@router.post("/query", response_model=UnifiedQueryResponse, 
             summary="Query RAG Unified", 
             description="API duy nhất để hỏi đáp với toàn bộ tài liệu đã embedding")
async def unified_query(request: UnifiedQueryRequest):
    """
    **API Thống nhất cho Query/Response RAG**
    
    Đây là API duy nhất để:
    - Gửi câu hỏi và nhận câu trả lời từ toàn bộ knowledge base
    - Tìm kiếm trong tất cả tài liệu đã được embedding
    - Lọc theo danh mục tài liệu
    - Điều chỉnh độ chính xác và số lượng nguồn
    
    **Categories:**
    - `luat`: Tài liệu luật pháp Việt Nam
    - `english`: Tài liệu tiếng Anh (NIST, ISO)
    - `vietnamese`: Tài liệu tiếng Việt
    - `all` hoặc `null`: Tất cả tài liệu
    
    **Ví dụ câu hỏi:**
    - "An toàn thông tin là gì?"
    - "Luật An toàn thông tin quy định gì?"
    - "ISO 27001 có những yêu cầu nào?"
    - "Các biện pháp bảo mật cơ bản?"
    """
    try:
        logger.info(f"📝 Unified query: {request.question[:100]}...")
        
        # Get RAG service
        rag_service = await get_rag_service_unified()
        
        # Process query
        result = await rag_service.query(
            question=request.question,
            top_k=request.top_k,
            filter_category=request.filter_category,
            include_sources=request.include_sources,
            similarity_threshold=request.similarity_threshold,
            use_enhancement=request.use_enhancement
        )
        
        # Convert to response model
        sources = [SourceInfo(**source) for source in result.get('sources', [])]
        
        response = UnifiedQueryResponse(
            question=result['question'],
            answer=result['answer'],
            sources=sources,
            total_sources=result['total_sources'],
            confidence=result.get('confidence', 0.0),
            method=result.get('method', 'unified'),
            processing_time_ms=result.get('processing_time_ms', 0),
            filter_category=result.get('filter_category', 'all'),
            timestamp=result.get('timestamp', ''),
            service_version=result.get('service_version', '2.0.0'),
            enhancement_applied=result.get('enhancement_applied', False),
            original_response=result.get('original_response', None)
        )
        
        logger.info(f"✅ Query processed: {response.total_sources} sources, {response.processing_time_ms}ms")
        return response
        
    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Lỗi dữ liệu đầu vào: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Unified query error: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý câu hỏi: {str(e)}")

@router.get("/stats", response_model=ServiceStats,
            summary="Service Statistics",
            description="Lấy thống kê chi tiết về RAG service")
async def get_service_stats():
    """
    **Thống kê RAG Service**
    
    Trả về thông tin chi tiết về:
    - Số lượng tài liệu và chunks
    - Phân bố theo danh mục
    - Cấu hình mặc định
    - Trạng thái service
    """
    try:
        rag_service = await get_rag_service_unified()
        stats = await rag_service.get_service_stats()
        
        return ServiceStats(
            service_name=stats['service_name'],
            version=stats['version'],
            status=stats['status'],
            total_documents=stats['total_documents'],
            total_chunks=stats['total_chunks'],
            categories=stats['categories'],
            device=stats['device'],
            default_settings=stats['default_settings']
        )
        
    except Exception as e:
        logger.error(f"❌ Stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi lấy thống kê: {str(e)}")

@router.get("/health",
            summary="Health Check",
            description="Kiểm tra trạng thái sức khỏe của RAG service")
async def health_check():
    """
    **Health Check**
    
    Kiểm tra:
    - Service có sẵn sàng không
    - Thời gian khởi tạo
    - Thông tin cơ bản
    """
    try:
        rag_service = await get_rag_service_unified()
        stats = await rag_service.get_service_stats()
        
        return {
            "status": "healthy",
            "service": "RAG Unified",
            "version": "1.0.0",
            "ready": stats.get('status') == 'ready',
            "total_documents": stats.get('total_documents', 0),
            "total_chunks": stats.get('total_chunks', 0),
            "initialization_time": stats.get('initialization_time', 0)
        }
        
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return {
            "status": "unhealthy",
            "service": "RAG Unified",
            "version": "1.0.0",
            "error": str(e)
        }

@router.get("/categories",
            summary="Available Categories",
            description="Lấy danh sách các danh mục tài liệu có sẵn")
async def get_categories():
    """
    **Danh mục tài liệu có sẵn**
    
    Trả về danh sách các category có thể sử dụng để filter
    """
    try:
        rag_service = await get_rag_service_unified()
        stats = await rag_service.get_service_stats()
        
        categories = []
        for cat_id, cat_info in stats.get('categories', {}).items():
            categories.append({
                'id': cat_id,
                'name': {
                    'luat': 'Luật pháp Việt Nam',
                    'english': 'Tài liệu tiếng Anh',
                    'vietnamese': 'Tài liệu tiếng Việt'
                }.get(cat_id, cat_id.title()),
                'chunks': cat_info.get('chunks', 0),
                'total_length': cat_info.get('total_length', 0)
            })
        
        return {
            'categories': categories,
            'total_categories': len(categories),
            'note': 'Sử dụng filter_category="all" để tìm trong tất cả danh mục'
        }
        
    except Exception as e:
        logger.error(f"❌ Categories error: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi lấy danh mục: {str(e)}")

# Compatibility endpoint (deprecated)
@router.post("/query/simple", 
             deprecated=True,
             summary="[DEPRECATED] Simple Query",
             description="Sử dụng /query thay thế")
async def simple_query_deprecated(question: str = Query(..., description="Câu hỏi")):
    """Endpoint tương thích ngược - khuyến nghị sử dụng /query"""
    request = UnifiedQueryRequest(question=question)
    return await unified_query(request)

@router.get("/info",
            summary="Service Information", 
            description="Thông tin tổng quan về RAG Unified API")
async def service_info():
    """
    **Thông tin RAG Unified API**
    
    API duy nhất để truy vấn toàn bộ knowledge base
    """
    return {
        "name": "RAG Unified API",
        "version": "1.0.0",
        "description": "API thống nhất cho query/response từ toàn bộ tài liệu đã embedding",
        "main_endpoint": "/api/v1/rag/query",
        "features": [
            "Tìm kiếm thông minh với embedding vectors",
            "Lọc theo danh mục tài liệu", 
            "Điều chỉnh độ chính xác và số lượng kết quả",
            "Trả về câu trả lời chi tiết với nguồn tham khảo",
            "Thống kê và monitoring"
        ],
        "supported_categories": ["luat", "english", "vietnamese", "all"],
        "example_questions": [
            "An toàn thông tin là gì?",
            "Luật An toàn thông tin quy định gì?", 
            "ISO 27001 có những yêu cầu nào?",
            "Các biện pháp bảo mật cơ bản?"
        ]
    }

# End of core RAG endpoints
