from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from models.chat import FileUploadResponse
import settings
import os
import aiofiles
from pathlib import Path

router = APIRouter()

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload file lên server
    """
    try:
        # Kiểm tra định dạng file
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in settings.ALLOWED_FILE:
            return FileUploadResponse(
                filename=file.filename,
                status="error",
                message=f"Định dạng file không được hỗ trợ. Chỉ hỗ trợ: {', '.join(settings.ALLOWED_FILE)}"
            )
        
        # Tạo thư mục upload nếu chưa có
        settings.FILE_FOLDER.mkdir(parents=True, exist_ok=True)
        
        # Tạo đường dẫn file
        file_path = settings.FILE_FOLDER / file.filename
        
        # Lưu file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return FileUploadResponse(
            filename=file.filename,
            status="success",
            message="File đã được upload thành công",
            file_path=str(file_path)
        )
        
    except Exception as e:
        return FileUploadResponse(
            filename=file.filename if file else "unknown",
            status="error",
            message=f"Lỗi upload file: {str(e)}"
        )

@router.get("/files")
def list_files():
    """
    Liệt kê các file đã upload
    """
    try:
        if not settings.FILE_FOLDER.exists():
            return {"files": [], "message": "Thư mục upload chưa tồn tại"}
        
        files = []
        for file_path in settings.FILE_FOLDER.iterdir():
            if file_path.is_file():
                files.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "path": str(file_path)
                })
        
        return {"files": files, "total": len(files)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi liệt kê file: {str(e)}")

@router.delete("/files/{filename}")
def delete_file(filename: str):
    """
    Xóa file
    """
    try:
        file_path = settings.FILE_FOLDER / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File không tồn tại")
        
        file_path.unlink()
        
        return {"message": f"Đã xóa file {filename} thành công"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xóa file: {str(e)}")
