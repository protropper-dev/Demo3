import os
import shutil
from pathlib import Path
import settings

def save_uploaded_file(file_content, filename):
    """
    Lưu file đã upload
    """
    try:
        # Tạo thư mục upload nếu chưa có
        settings.FILE_FOLDER.mkdir(parents=True, exist_ok=True)
        
        # Tạo đường dẫn file
        file_path = settings.FILE_FOLDER / filename
        
        # Lưu file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return str(file_path)
        
    except Exception as e:
        print(f"❌ Lỗi khi lưu file: {e}")
        return None

def delete_file(file_path):
    """
    Xóa file
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"❌ Lỗi khi xóa file: {e}")
        return False

def get_file_info(file_path):
    """
    Lấy thông tin file
    """
    try:
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        return {
            "filename": os.path.basename(file_path),
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "extension": Path(file_path).suffix.lower()
        }
    except Exception as e:
        print(f"❌ Lỗi khi lấy thông tin file: {e}")
        return None

def is_allowed_file(filename):
    """
    Kiểm tra file có được phép upload không
    """
    file_extension = Path(filename).suffix.lower()
    return file_extension in settings.ALLOWED_FILE

def list_uploaded_files():
    """
    Liệt kê các file đã upload
    """
    try:
        if not settings.FILE_FOLDER.exists():
            return []
        
        files = []
        for file_path in settings.FILE_FOLDER.iterdir():
            if file_path.is_file():
                file_info = get_file_info(file_path)
                if file_info:
                    files.append(file_info)
        
        return files
        
    except Exception as e:
        print(f"❌ Lỗi khi liệt kê file: {e}")
        return []
