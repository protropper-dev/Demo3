#!/usr/bin/env python3
"""
File Management Endpoints - Quản lý files và upload
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import os
from pathlib import Path

router = APIRouter()
logger = logging.getLogger(__name__)

# File models
class FileInfo(BaseModel):
    """Thông tin file"""
    filename: str
    size: int
    size_mb: float
    modified: float
    extension: str
    created: float

class FileListResponse(BaseModel):
    """Response cho danh sách files"""
    files: List[FileInfo]
    total: int
    upload_dir: str
    message: Optional[str] = None

class FileUploadResponse(BaseModel):
    """Response cho upload file"""
    filename: str
    size: int
    message: str
    success: bool

@router.get("/uploaded", response_model=FileListResponse,
            summary="Lấy danh sách files đã upload",
            description="Lấy danh sách các file trong thư mục documents/upload")
async def get_uploaded_files():
    """
    **Lấy danh sách files đã upload**
    
    Trả về danh sách các file trong thư mục upload
    để hiển thị trong sidebar hoặc file manager
    """
    try:
        upload_dir = "documents/upload"
        
        # Kiểm tra thư mục có tồn tại không
        if not os.path.exists(upload_dir):
            return FileListResponse(
                files=[],
                total=0,
                upload_dir=upload_dir,
                message="Thư mục upload chưa tồn tại"
            )
        
        # Lấy danh sách file trong thư mục
        files = []
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                # Lấy thông tin file
                stat = os.stat(file_path)
                files.append(FileInfo(
                    filename=filename,
                    size=stat.st_size,
                    size_mb=round(stat.st_size / (1024 * 1024), 2),
                    modified=stat.st_mtime,
                    extension=filename.split('.')[-1].lower() if '.' in filename else '',
                    created=stat.st_ctime
                ))
        
        # Sắp xếp theo thời gian modified
        files.sort(key=lambda x: x.modified, reverse=True)
        
        return FileListResponse(
            files=files,
            total=len(files),
            upload_dir=upload_dir
        )
        
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách file upload: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi lấy files: {str(e)}")

@router.post("/upload", response_model=FileUploadResponse,
             summary="Upload file mới",
             description="Upload file mới vào thư mục documents/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    **Upload file mới**
    
    Upload file vào thư mục documents/upload
    Hỗ trợ các định dạng: PDF, DOC, DOCX, TXT
    """
    try:
        # Kiểm tra định dạng file
        allowed_extensions = {'.pdf', '.doc', '.docx', '.txt'}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Định dạng file không được hỗ trợ. Chỉ chấp nhận: {', '.join(allowed_extensions)}"
            )
        
        # Kiểm tra kích thước file (10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(
                status_code=400,
                detail="File quá lớn. Kích thước tối đa: 10MB"
            )
        
        # Tạo thư mục upload nếu chưa có
        upload_dir = "documents/upload"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Lưu file
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        return FileUploadResponse(
            filename=file.filename,
            size=len(content),
            message="Upload thành công",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi upload file: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi upload: {str(e)}")

@router.delete("/{filename}",
               summary="Xóa file",
               description="Xóa file khỏi thư mục upload")
async def delete_file(filename: str):
    """
    **Xóa file**
    
    Xóa file khỏi thư mục documents/upload
    """
    try:
        upload_dir = "documents/upload"
        file_path = os.path.join(upload_dir, filename)
        
        # Kiểm tra file có tồn tại không
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File không tồn tại")
        
        # Xóa file
        os.remove(file_path)
        
        return {
            "message": f"Đã xóa file {filename}",
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi xóa file: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi xóa file: {str(e)}")

@router.get("/{filename}/info",
            summary="Thông tin file",
            description="Lấy thông tin chi tiết về file")
async def get_file_info(filename: str):
    """
    **Thông tin file**
    
    Lấy thông tin chi tiết về file
    """
    try:
        upload_dir = "documents/upload"
        file_path = os.path.join(upload_dir, filename)
        
        # Kiểm tra file có tồn tại không
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File không tồn tại")
        
        # Lấy thông tin file
        stat = os.stat(file_path)
        
        return FileInfo(
            filename=filename,
            size=stat.st_size,
            size_mb=round(stat.st_size / (1024 * 1024), 2),
            modified=stat.st_mtime,
            extension=filename.split('.')[-1].lower() if '.' in filename else '',
            created=stat.st_ctime
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi lấy thông tin file: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi lấy thông tin: {str(e)}")

@router.get("/stats",
            summary="Thống kê files",
            description="Lấy thống kê về files trong thư mục upload")
async def get_file_stats():
    """
    **Thống kê files**
    
    Lấy thống kê tổng quan về files trong thư mục upload
    """
    try:
        upload_dir = "documents/upload"
        
        if not os.path.exists(upload_dir):
            return {
                "total_files": 0,
                "total_size_mb": 0,
                "file_types": {},
                "message": "Thư mục upload chưa tồn tại"
            }
        
        files = os.listdir(upload_dir)
        total_size = 0
        file_types = {}
        
        for filename in files:
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                total_size += stat.st_size
                
                extension = filename.split('.')[-1].lower() if '.' in filename else 'no_extension'
                file_types[extension] = file_types.get(extension, 0) + 1
        
        return {
            "total_files": len(files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": file_types,
            "upload_dir": upload_dir
        }
        
    except Exception as e:
        logger.error(f"Lỗi khi lấy thống kê files: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi lấy thống kê: {str(e)}")
