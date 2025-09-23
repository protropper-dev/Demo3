#!/usr/bin/env python3
"""
File Upload API Endpoint
Xử lý upload file và embedding vào vector database
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import os
import shutil
import asyncio
from pathlib import Path
import uuid
from datetime import datetime

from app.core.config import settings
from app.utils.rag_utils import FileUtils
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic Models
class UploadResponse(BaseModel):
    """Response model cho upload file"""
    success: bool
    message: str
    filename: str
    file_id: str
    file_size: int
    upload_time: str
    status: str = "uploaded"  # uploaded, processing, embedded, error

class EmbeddingStatus(BaseModel):
    """Status của quá trình embedding"""
    file_id: str
    filename: str
    status: str  # processing, completed, error
    progress: int = 0  # 0-100
    message: str = ""
    embedding_time: Optional[str] = None

class FileInfo(BaseModel):
    """Thông tin file"""
    file_id: str
    filename: str
    size: int
    size_mb: float
    extension: str
    uploaded_at: str
    status: str
    is_embedded: bool = False

class AllFilesResponse(BaseModel):
    """Response cho tất cả files trong documents"""
    recent_uploads: List[FileInfo]
    all_files: Dict[str, List[Dict[str, Any]]]
    total_files: int
    categories: Dict[str, int]

# Utility functions
def ensure_upload_directory():
    """Đảm bảo thư mục upload tồn tại"""
    upload_dir = Path(settings.DOCUMENTS_UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir

def validate_file_type(filename: str) -> bool:
    """Kiểm tra loại file có được phép không"""
    allowed_extensions = {".pdf", ".doc", ".docx", ".txt"}
    file_extension = Path(filename).suffix.lower()
    return file_extension in allowed_extensions

def get_file_size_mb(size_bytes: int) -> float:
    """Chuyển đổi size từ bytes sang MB"""
    return round(size_bytes / (1024 * 1024), 2)

async def process_file_embedding(file_path: str, file_id: str, filename: str):
    """
    Xử lý embedding file trong background
    """
    try:
        logger.info(f"🔄 Bắt đầu embedding file: {filename} (ID: {file_id})")
        
        # Khởi tạo embedding service
        embedding_service = EmbeddingService(
            model_path=settings.EMBEDDING_MODEL_PATH,
            output_dir=settings.VECTOR_STORE_PATH
        )
        
        # Load model nếu chưa có
        if embedding_service.model is None:
            embedding_service.load_model()
        
        # Xử lý document để tạo embeddings
        result = embedding_service.process_document(
            doc_path=file_path,
            chunk_size=settings.CHUNK_SIZE,
            overlap=settings.CHUNK_OVERLAP
        )
        
        if result and result.get("status") == "success":
            logger.info(f"✅ Hoàn thành embedding file: {filename} (ID: {file_id})")
            logger.info(f"   - Số chunks: {result['num_chunks']}")
            logger.info(f"   - Embedding shape: {result['embedding_shape']}")
        else:
            logger.error(f"❌ Lỗi embedding file {filename}: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        logger.error(f"❌ Lỗi embedding file {filename}: {e}")

@router.post("/upload", response_model=UploadResponse,
             summary="Upload File", 
             description="Upload file PDF, DOC, TXT và tự động embedding")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="File cần upload (PDF, DOC, DOCX, TXT)")
):
    """
    **Upload File với Auto Embedding**
    
    Tính năng:
    - Chỉ chấp nhận file PDF, DOC, DOCX, TXT
    - Kiểm tra kích thước file (tối đa 10MB)
    - Lưu file vào thư mục upload
    - Tự động embedding vào vector database
    - Trả về thông tin file và status
    
    **Quy trình:**
    1. Validate file type và size
    2. Tạo file ID unique
    3. Lưu file vào thư mục upload
    4. Bắt đầu quá trình embedding (background)
    5. Trả về response với file info
    """
    try:
        # Validate file type
        if not validate_file_type(file.filename):
            raise HTTPException(
                status_code=400, 
                detail="Chỉ chấp nhận file PDF, DOC, DOCX, TXT"
            )
        
        # Validate file size
        if file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File quá lớn. Kích thước tối đa: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        # Tạo file ID unique
        file_id = str(uuid.uuid4())
        
        # Đảm bảo thư mục upload tồn tại
        upload_dir = ensure_upload_directory()
        
        # Tạo tên file với timestamp để tránh conflict
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = upload_dir / safe_filename
        
        # Lưu file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Lấy thông tin file
        file_size_mb = get_file_size_mb(file.size)
        upload_time = datetime.now().isoformat()
        
        # Bắt đầu quá trình embedding trong background
        background_tasks.add_task(
            process_file_embedding, 
            str(file_path), 
            file_id, 
            file.filename
        )
        
        logger.info(f"✅ File uploaded: {file.filename} -> {file_path} (ID: {file_id})")
        
        return UploadResponse(
            success=True,
            message=f"File {file.filename} đã được upload thành công",
            filename=file.filename,
            file_id=file_id,
            file_size=file.size,
            upload_time=upload_time,
            status="uploaded"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi upload file: {str(e)}")

@router.get("/files/uploaded", response_model=List[FileInfo],
            summary="Lấy danh sách files đã upload",
            description="Lấy danh sách tất cả files trong thư mục upload")
async def get_uploaded_files():
    """
    **Lấy danh sách files đã upload**
    
    Trả về:
    - Danh sách tất cả files trong thư mục upload
    - Thông tin chi tiết: size, extension, upload time
    - Status embedding
    """
    try:
        upload_dir = Path(settings.DOCUMENTS_UPLOAD_DIR)
        
        if not upload_dir.exists():
            return []
        
        # Khởi tạo embedding service để kiểm tra status
        embedding_service = EmbeddingService(
            model_path=settings.EMBEDDING_MODEL_PATH,
            output_dir=settings.VECTOR_STORE_PATH
        )
        
        files = []
        for file_path in upload_dir.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                
                # Kiểm tra xem file đã được embedding chưa
                is_embedded = embedding_service.is_document_embedded(str(file_path))
                
                files.append(FileInfo(
                    file_id=str(uuid.uuid4()),  # TODO: Lưu file_id thực tế
                    filename=file_path.name,
                    size=stat.st_size,
                    size_mb=get_file_size_mb(stat.st_size),
                    extension=file_path.suffix.lower(),
                    uploaded_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    status="embedded" if is_embedded else "uploaded",
                    is_embedded=is_embedded
                ))
        
        # Sắp xếp theo thời gian upload (mới nhất trước)
        files.sort(key=lambda x: x.uploaded_at, reverse=True)
        
        return files
        
    except Exception as e:
        logger.error(f"❌ Error getting files: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi lấy danh sách file: {str(e)}")

@router.get("/files/all", response_model=AllFilesResponse,
            summary="Lấy tất cả files trong documents",
            description="Lấy danh sách tất cả files từ các thư mục documents")
async def get_all_files():
    """
    **Lấy tất cả files trong documents**
    
    Trả về:
    - Files upload gần đây (10 files)
    - Tất cả files theo danh mục (Luat, TaiLieuTiengAnh, TaiLieuTiengViet, upload)
    - Thống kê số lượng files
    """
    try:
        # Định nghĩa các thư mục documents
        document_dirs = {
            "Luật": settings.LUAT_DOCS_PATH,
            "Tài liệu Tiếng Anh": settings.ENGLISH_DOCS_PATH,
            "Tài liệu Tiếng Việt": settings.VIETNAMESE_DOCS_PATH,
            "Files Upload": settings.DOCUMENTS_UPLOAD_DIR
        }
        
        all_files = {}
        total_files = 0
        categories = {}
        recent_uploads = []
        
        # Khởi tạo embedding service để kiểm tra status
        embedding_service = EmbeddingService(
            model_path=settings.EMBEDDING_MODEL_PATH,
            output_dir=settings.VECTOR_STORE_PATH
        )
        
        # Duyệt qua từng thư mục
        for category, dir_path in document_dirs.items():
            category_files = []
            category_count = 0
            
            if Path(dir_path).exists():
                for file_path in Path(dir_path).iterdir():
                    if file_path.is_file() and validate_file_type(file_path.name):
                        stat = file_path.stat()
                        is_embedded = embedding_service.is_document_embedded(str(file_path))
                        
                        file_info = {
                            "filename": file_path.name,
                            "size": stat.st_size,
                            "size_mb": get_file_size_mb(stat.st_size),
                            "extension": file_path.suffix.lower(),
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "path": str(file_path),
                            "category": category,
                            "is_embedded": is_embedded,
                            "status": "embedded" if is_embedded else "not_embedded"
                        }
                        
                        category_files.append(file_info)
                        category_count += 1
                        
                        # Nếu là file upload gần đây, thêm vào recent_uploads
                        if category == "Files Upload":
                            recent_uploads.append(FileInfo(
                                file_id=str(uuid.uuid4()),
                                filename=file_path.name,
                                size=stat.st_size,
                                size_mb=get_file_size_mb(stat.st_size),
                                extension=file_path.suffix.lower(),
                                uploaded_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                status="embedded" if is_embedded else "uploaded",
                                is_embedded=is_embedded
                            ))
            
            # Sắp xếp files theo thời gian modified (mới nhất trước)
            category_files.sort(key=lambda x: x['modified'], reverse=True)
            
            all_files[category] = category_files
            categories[category] = category_count
            total_files += category_count
        
        # Sắp xếp recent_uploads và chỉ lấy 10 files gần nhất
        recent_uploads.sort(key=lambda x: x.uploaded_at, reverse=True)
        recent_uploads = recent_uploads[:10]
        
        return AllFilesResponse(
            recent_uploads=recent_uploads,
            all_files=all_files,
            total_files=total_files,
            categories=categories
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting all files: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi lấy tất cả files: {str(e)}")

@router.get("/status/{file_id}", response_model=EmbeddingStatus,
            summary="Kiểm tra status embedding",
            description="Kiểm tra trạng thái quá trình embedding của file")
async def get_embedding_status(file_id: str):
    """
    **Kiểm tra status embedding file**
    
    Trả về:
    - Trạng thái hiện tại (processing, completed, error)
    - Tiến trình embedding (0-100%)
    - Thông báo chi tiết
    """
    try:
        # TODO: Implement status checking logic
        # Tạm thời trả về status mặc định
        
        return EmbeddingStatus(
            file_id=file_id,
            filename="unknown",  # TODO: Lấy từ database/cache
            status="processing",
            progress=50,
            message="Đang xử lý embedding...",
            embedding_time=None
        )
        
    except Exception as e:
        logger.error(f"❌ Error checking status: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi kiểm tra status: {str(e)}")

@router.delete("/files/{file_id}",
               summary="Xóa file",
               description="Xóa file khỏi thư mục upload")
async def delete_file(file_id: str):
    """
    **Xóa file**
    
    Xóa file khỏi thư mục upload và vector database
    """
    try:
        # TODO: Implement file deletion logic
        # 1. Tìm file theo file_id
        # 2. Xóa file từ filesystem
        # 3. Xóa vector embeddings liên quan
        
        return {"message": f"File {file_id} đã được xóa", "success": True}
        
    except Exception as e:
        logger.error(f"❌ Error deleting file: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi xóa file: {str(e)}")

@router.get("/health",
            summary="Health Check",
            description="Kiểm tra trạng thái file upload service")
async def health_check():
    """
    **Health Check File Upload Service**
    """
    try:
        upload_dir = Path(settings.DOCUMENTS_UPLOAD_DIR)
        
        return {
            "status": "healthy",
            "service": "File Upload",
            "upload_dir": str(upload_dir),
            "upload_dir_exists": upload_dir.exists(),
            "max_file_size_mb": settings.MAX_FILE_SIZE / (1024*1024),
            "allowed_extensions": [".pdf", ".doc", ".docx", ".txt"]
        }
        
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return {
            "status": "unhealthy",
            "service": "File Upload",
            "error": str(e)
        }
