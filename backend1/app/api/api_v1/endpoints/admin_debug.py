#!/usr/bin/env python3
"""
Admin & Debug Endpoints - Quản lý hệ thống và debug
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import logging
import torch
import os
import time

router = APIRouter()
logger = logging.getLogger(__name__)

# Admin models
class SystemInfo(BaseModel):
    """Thông tin hệ thống"""
    status: str
    service: str
    version: str
    ready: bool
    total_documents: int
    total_chunks: int
    initialization_time: float
    gpu_info: Optional[Dict[str, Any]] = None

class LLMStatus(BaseModel):
    """Trạng thái LLM"""
    status: str
    llm_available: bool
    use_llm_generation: bool
    gpu_info: Optional[Dict[str, Any]] = None
    model_filepath: str  # Đổi tên từ model_path để tránh conflict với protected namespace
    error: Optional[str] = None

class ReloadResponse(BaseModel):
    """Response cho reload"""
    message: str
    llm_status: str
    use_llm_generation: bool
    success: bool

@router.post("/reload-llm", response_model=ReloadResponse,
             summary="Reload LLM Service",
             description="Force reload LLM service for debugging")
async def reload_llm_service():
    """
    **Force Reload LLM Service**
    
    Debug endpoint để reload LLM service
    Useful khi LLM không hoạt động
    """
    try:
        from app.services.rag_service_unified import _rag_service_unified
        
        if _rag_service_unified:
            # Reset LLM service
            _rag_service_unified.llm_service = None
            _rag_service_unified.use_llm_generation = True
            
            # Reinitialize
            await _rag_service_unified.initialize()
            
            # Check status
            llm_status = "available" if _rag_service_unified.llm_service else "not_available"
            
            return ReloadResponse(
                message="LLM service reload attempted",
                llm_status=llm_status,
                use_llm_generation=_rag_service_unified.use_llm_generation,
                success=True
            )
        else:
            return ReloadResponse(
                message="RAG service not initialized yet",
                llm_status="unknown",
                use_llm_generation=False,
                success=False
            )
            
    except Exception as e:
        logger.error(f"❌ Reload LLM error: {e}")
        return ReloadResponse(
            message=f"Reload failed: {str(e)}",
            llm_status="error",
            use_llm_generation=False,
            success=False
        )

@router.get("/llm-status", response_model=LLMStatus,
            summary="Check LLM Status",
            description="Kiểm tra trạng thái LLM service")
async def check_llm_status():
    """
    **Check LLM Service Status**
    
    Debug endpoint để kiểm tra:
    - LLM service có được load không
    - Memory usage
    - Configuration
    """
    try:
        from app.services.rag_service_unified import _rag_service_unified
        
        if not _rag_service_unified:
            return LLMStatus(
                status="rag_service_not_initialized",
                llm_available=False,
                use_llm_generation=False,
                model_filepath="models/vinallama-2.7b-chat"
            )
        
        # Check LLM service
        llm_available = _rag_service_unified.llm_service is not None
        use_llm = _rag_service_unified.use_llm_generation
        
        # GPU info
        gpu_info = {}
        if torch.cuda.is_available():
            device = torch.cuda.current_device()
            total_memory = torch.cuda.get_device_properties(device).total_memory / 1024**3
            allocated_memory = torch.cuda.memory_allocated(device) / 1024**3
            
            gpu_info = {
                "gpu_name": torch.cuda.get_device_name(device),
                "total_memory_gb": round(total_memory, 2),
                "allocated_memory_gb": round(allocated_memory, 2),
                "free_memory_gb": round(total_memory - allocated_memory, 2)
            }
        
        return LLMStatus(
            status="initialized",
            llm_available=llm_available,
            use_llm_generation=use_llm,
            gpu_info=gpu_info,
            model_path="models/vinallama-2.7b-chat"
        )
        
    except Exception as e:
        logger.error(f"❌ LLM status check error: {e}")
        return LLMStatus(
            status="error",
            llm_available=False,
            use_llm_generation=False,
            model_filepath="models/vinallama-2.7b-chat",
            error=str(e)
        )

@router.get("/system-info", response_model=SystemInfo,
            summary="System Information",
            description="Lấy thông tin tổng quan về hệ thống")
async def get_system_info():
    """
    **System Information**
    
    Lấy thông tin tổng quan về:
    - Trạng thái service
    - Thống kê documents và chunks
    - Thông tin GPU
    - Thời gian khởi tạo
    """
    try:
        from app.services.rag_service_unified import get_rag_service_unified
        
        rag_service = await get_rag_service_unified()
        stats = await rag_service.get_service_stats()
        
        # GPU info
        gpu_info = {}
        if torch.cuda.is_available():
            device = torch.cuda.current_device()
            total_memory = torch.cuda.get_device_properties(device).total_memory / 1024**3
            allocated_memory = torch.cuda.memory_allocated(device) / 1024**3
            
            gpu_info = {
                "gpu_name": torch.cuda.get_device_name(device),
                "total_memory_gb": round(total_memory, 2),
                "allocated_memory_gb": round(allocated_memory, 2),
                "free_memory_gb": round(total_memory - allocated_memory, 2),
                "device_count": torch.cuda.device_count()
            }
        
        return SystemInfo(
            status="healthy",
            service="RAG Unified",
            version="1.0.0",
            ready=stats.get('status') == 'ready',
            total_documents=stats.get('total_documents', 0),
            total_chunks=stats.get('total_chunks', 0),
            initialization_time=stats.get('initialization_time', 0),
            gpu_info=gpu_info
        )
        
    except Exception as e:
        logger.error(f"❌ System info error: {e}")
        return SystemInfo(
            status="unhealthy",
            service="RAG Unified",
            version="1.0.0",
            ready=False,
            total_documents=0,
            total_chunks=0,
            initialization_time=0,
            gpu_info=None
        )

@router.post("/rebuild-index",
             summary="Rebuild FAISS Index",
             description="Rebuild FAISS index từ dữ liệu hiện có")
async def rebuild_faiss_index():
    """
    **Rebuild FAISS Index**
    
    Rebuild FAISS index từ dữ liệu hiện có
    Useful khi index bị corrupt hoặc cần cập nhật
    """
    try:
        from app.services.rag_service_unified import _rag_service_unified
        
        if not _rag_service_unified:
            raise HTTPException(status_code=500, detail="RAG service chưa được khởi tạo")
        
        # Rebuild index
        start_time = time.time()
        await _rag_service_unified.initialize()
        rebuild_time = time.time() - start_time
        
        return {
            "message": "FAISS index đã được rebuild thành công",
            "rebuild_time_seconds": round(rebuild_time, 2),
            "total_documents": _rag_service_unified.total_documents,
            "total_chunks": _rag_service_unified.total_chunks,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"❌ Rebuild index error: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi rebuild index: {str(e)}")

@router.get("/memory-usage",
            summary="Memory Usage",
            description="Kiểm tra memory usage của hệ thống")
async def get_memory_usage():
    """
    **Memory Usage**
    
    Kiểm tra memory usage của:
    - System memory
    - GPU memory
    - Python process memory
    """
    try:
        import psutil
        
        # System memory
        system_memory = psutil.virtual_memory()
        
        # Process memory
        process = psutil.Process()
        process_memory = process.memory_info()
        
        # GPU memory
        gpu_memory = {}
        if torch.cuda.is_available():
            device = torch.cuda.current_device()
            total_memory = torch.cuda.get_device_properties(device).total_memory / 1024**3
            allocated_memory = torch.cuda.memory_allocated(device) / 1024**3
            cached_memory = torch.cuda.memory_reserved(device) / 1024**3
            
            gpu_memory = {
                "gpu_name": torch.cuda.get_device_name(device),
                "total_memory_gb": round(total_memory, 2),
                "allocated_memory_gb": round(allocated_memory, 2),
                "cached_memory_gb": round(cached_memory, 2),
                "free_memory_gb": round(total_memory - allocated_memory, 2)
            }
        
        return {
            "system_memory": {
                "total_gb": round(system_memory.total / 1024**3, 2),
                "available_gb": round(system_memory.available / 1024**3, 2),
                "used_gb": round(system_memory.used / 1024**3, 2),
                "percent_used": system_memory.percent
            },
            "process_memory": {
                "rss_gb": round(process_memory.rss / 1024**3, 2),
                "vms_gb": round(process_memory.vms / 1024**3, 2)
            },
            "gpu_memory": gpu_memory
        }
        
    except Exception as e:
        logger.error(f"❌ Memory usage error: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi lấy memory usage: {str(e)}")

@router.get("/config",
            summary="System Configuration",
            description="Lấy cấu hình hiện tại của hệ thống")
async def get_system_config():
    """
    **System Configuration**
    
    Lấy cấu hình hiện tại của:
    - RAG service settings
    - Model paths
    - Default parameters
    """
    try:
        from app.services.rag_service_unified import _rag_service_unified
        from app.core.config import settings
        
        if not _rag_service_unified:
            return {
                "status": "service_not_initialized",
                "config": {}
            }
        
        return {
            "status": "initialized",
            "config": {
                "rag_settings": {
                    "default_top_k": _rag_service_unified.default_top_k,
                    "default_similarity_threshold": _rag_service_unified.default_similarity_threshold,
                    "max_answer_length": _rag_service_unified.max_answer_length,
                    "max_context_length": _rag_service_unified.max_context_length,
                    "use_llm_generation": _rag_service_unified.use_llm_generation
                },
                "model_filepaths": {
                    "embedding_model": settings.EMBEDDING_MODEL_PATH,
                    "llm_model": settings.LLM_MODEL_PATH
                },
                "data_paths": {
                    "faiss_path": settings.FAISS_PATH,
                    "pickle_path": settings.PICKLE_PATH,
                    "documents_path": settings.DOCUMENTS_PATH
                },
                "service_info": {
                    "total_documents": _rag_service_unified.total_documents,
                    "total_chunks": _rag_service_unified.total_chunks,
                    "initialization_time": _rag_service_unified.initialization_time
                }
            }
        }
        
    except Exception as e:
        logger.error(f"❌ System config error: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi lấy config: {str(e)}")
