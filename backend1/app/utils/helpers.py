# app/utils/helpers.py
# Các helper functions và tiện ích chung
# Chứa các hàm tiện ích được sử dụng trong toàn bộ ứng dụng

import os
import hashlib
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
import re

def generate_uuid() -> str:
    """Tạo UUID string"""
    return str(uuid.uuid4())

def generate_hash(text: str) -> str:
    """Tạo hash MD5 từ text"""
    return hashlib.md5(text.encode()).hexdigest()

def is_valid_email(email: str) -> bool:
    """Kiểm tra email có hợp lệ không"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone: str) -> bool:
    """Kiểm tra số điện thoại có hợp lệ không"""
    pattern = r'^(\+84|84|0)[1-9][0-9]{8,9}$'
    return re.match(pattern, phone) is not None

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime thành string"""
    return dt.strftime(format_str)

def safe_get_dict_value(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Lấy giá trị từ dict một cách an toàn"""
    return data.get(key, default)

def create_directory(path: str) -> bool:
    """Tạo thư mục nếu chưa tồn tại"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception:
        return False

def get_file_extension(filename: str) -> str:
    """Lấy extension của file"""
    return os.path.splitext(filename)[1].lower()

def is_allowed_file_extension(filename: str, allowed_extensions: list) -> bool:
    """Kiểm tra extension file có được phép không"""
    extension = get_file_extension(filename)
    return extension in allowed_extensions

def format_file_size(size_bytes: int) -> str:
    """Format kích thước file thành string dễ đọc"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"
