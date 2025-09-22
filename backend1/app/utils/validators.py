# app/utils/validators.py
# Các validator functions
# Chứa các hàm validation cho dữ liệu đầu vào

import re
from typing import List, Optional

def validate_password_strength(password: str) -> tuple[bool, List[str]]:
    """Kiểm tra độ mạnh của mật khẩu"""
    errors = []
    
    if len(password) < 8:
        errors.append("Mật khẩu phải có ít nhất 8 ký tự")
    
    if not re.search(r"[A-Z]", password):
        errors.append("Mật khẩu phải có ít nhất 1 chữ hoa")
    
    if not re.search(r"[a-z]", password):
        errors.append("Mật khẩu phải có ít nhất 1 chữ thường")
    
    if not re.search(r"\d", password):
        errors.append("Mật khẩu phải có ít nhất 1 số")
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Mật khẩu phải có ít nhất 1 ký tự đặc biệt")
    
    return len(errors) == 0, errors

def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """Kiểm tra username có hợp lệ không"""
    if len(username) < 3:
        return False, "Username phải có ít nhất 3 ký tự"
    
    if len(username) > 20:
        return False, "Username không được quá 20 ký tự"
    
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username chỉ được chứa chữ cái, số và dấu gạch dưới"
    
    if username.startswith("_") or username.endswith("_"):
        return False, "Username không được bắt đầu hoặc kết thúc bằng dấu gạch dưới"
    
    return True, None

def validate_vietnamese_phone(phone: str) -> tuple[bool, Optional[str]]:
    """Kiểm tra số điện thoại Việt Nam"""
    # Loại bỏ khoảng trắng và ký tự đặc biệt
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Pattern cho số điện thoại Việt Nam
    pattern = r'^(\+84|84|0)[1-9][0-9]{8,9}$'
    
    if not re.match(pattern, clean_phone):
        return False, "Số điện thoại không hợp lệ"
    
    return True, None

def validate_file_size(file_size: int, max_size_mb: int = 10) -> tuple[bool, Optional[str]]:
    """Kiểm tra kích thước file"""
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file_size > max_size_bytes:
        return False, f"File quá lớn. Kích thước tối đa: {max_size_mb}MB"
    
    return True, None

def validate_file_type(filename: str, allowed_types: List[str]) -> tuple[bool, Optional[str]]:
    """Kiểm tra loại file"""
    file_extension = filename.split('.')[-1].lower() if '.' in filename else ''
    
    if file_extension not in allowed_types:
        return False, f"Loại file không được hỗ trợ. Các loại được phép: {', '.join(allowed_types)}"
    
    return True, None
