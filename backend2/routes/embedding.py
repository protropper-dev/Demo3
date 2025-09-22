from fastapi import APIRouter
from utils.embedding import embedding
from models.chat import ChatResponse

router = APIRouter()

@router.get("/embedding")
def embedding_endpoint(pdf_path: str):
    """
    Kiểm tra xem file PDF đã được embedding với text chưa
    """
    try:
        result = embedding(pdf_path)
        return ChatResponse(
            response=str(result),
            status="success"
        )
    except Exception as e:
        return ChatResponse(
            response="",
            status="error",
            error=str(e)
        )

@router.post("/embedding/process")
def process_embedding(file_path: str):
    """
    Xử lý embedding cho một file
    """
    try:
        result = embedding(file_path)
        return {
            "status": "success",
            "message": f"Đã xử lý embedding cho file: {file_path}",
            "result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Lỗi xử lý embedding: {str(e)}"
        }
