from fastapi import APIRouter
from models.chat import SystemStatus
import consts
import torch

router = APIRouter()

@router.get("/status", response_model=SystemStatus)
def get_system_status():
    """
    Kiểm tra trạng thái hệ thống
    """
    try:
        llm_loaded = consts.llm_model is not None and consts.llm_tokenizer is not None
        embedding_loaded = consts.embedding_model is not None and consts.embedding_tokenizer is not None
        
        device_info = str(consts.device)
        
        if llm_loaded and embedding_loaded:
            status = "healthy"
            message = "Tất cả mô hình đã được tải thành công"
        else:
            status = "partial"
            message = "Một số mô hình chưa được tải"
            
        return SystemStatus(
            status=status,
            llm_model_loaded=llm_loaded,
            embedding_model_loaded=embedding_loaded,
            device=device_info,
            message=message
        )
    except Exception as e:
        return SystemStatus(
            status="error",
            llm_model_loaded=False,
            embedding_model_loaded=False,
            device="unknown",
            message=f"Lỗi kiểm tra hệ thống: {str(e)}"
        )

@router.get("/device")
def get_device_info():
    """
    Lấy thông tin thiết bị
    """
    return {
        "device": str(consts.device),
        "cuda_available": torch.cuda.is_available(),
        "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    }
