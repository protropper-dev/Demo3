import os
import fitz  # PyMuPDF
from pathlib import Path
import settings

def embedding(pdf_path):
    """
    Kiểm tra xem file PDF đã được embedding với text chưa
    """
    try:
        # Kiểm tra file có tồn tại không
        if not os.path.exists(pdf_path):
            return f"File không tồn tại: {pdf_path}"
        
        # Mở file PDF
        doc = fitz.open(pdf_path)
        
        # Lấy thông tin cơ bản
        info = {
            "filename": os.path.basename(pdf_path),
            "page_count": doc.page_count,
            "has_text": False,
            "text_length": 0,
            "first_page_text": ""
        }
        
        # Kiểm tra trang đầu tiên có text không
        if doc.page_count > 0:
            first_page = doc[0]
            text = first_page.get_text()
            info["has_text"] = len(text.strip()) > 0
            info["text_length"] = len(text.strip())
            info["first_page_text"] = text.strip()[:200] + "..." if len(text.strip()) > 200 else text.strip()
        
        doc.close()
        
        return info
        
    except Exception as e:
        return f"Lỗi khi xử lý file PDF: {str(e)}"

def extract_text_from_pdf(pdf_path):
    """
    Trích xuất toàn bộ text từ file PDF
    """
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text = page.get_text()
            full_text += text + "\n"
        
        doc.close()
        return full_text
        
    except Exception as e:
        print(f"❌ Lỗi khi trích xuất text từ PDF: {e}")
        return ""

def process_document_for_embedding(file_path):
    """
    Xử lý document để chuẩn bị cho embedding
    """
    try:
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == ".pdf":
            return extract_text_from_pdf(file_path)
        elif file_extension == ".txt":
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return f"Định dạng file không được hỗ trợ: {file_extension}"
            
    except Exception as e:
        return f"Lỗi xử lý document: {str(e)}"
