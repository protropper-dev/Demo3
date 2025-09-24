#!/usr/bin/env python3
"""
File quản lý tập trung tất cả các đường dẫn trong dự án
Chỉ chứa các biến đường dẫn, không có chức năng phụ trợ
"""

import os
from pathlib import Path

# Tự động detect thư mục gốc của project
current_file = Path(__file__).resolve()
BACKEND_ROOT = current_file.parent.parent.parent  # backend1/app/core -> backend1
PROJECT_ROOT = BACKEND_ROOT.parent  # Demo3

# ==================== THƯ MỤC GỐC ====================
PROJECT_ROOT = PROJECT_ROOT
BACKEND_ROOT = BACKEND_ROOT

# ==================== MODELS ====================
MODELS_DIR = BACKEND_ROOT / "models"
EMBEDDING_MODEL = MODELS_DIR / "multilingual_e5_large"
LLM_MODEL = MODELS_DIR / "vinallama-2.7b-chat"

# ==================== DOCUMENTS ====================
DOCUMENTS_ROOT = PROJECT_ROOT / "documents"
DOCUMENTS_UPLOAD = BACKEND_ROOT / "documents" / "upload"

# Tài liệu theo danh mục
DOCS_LUAT = DOCUMENTS_ROOT / "Luat"
DOCS_ENGLISH = DOCUMENTS_ROOT / "TaiLieuTiengAnh"
DOCS_VIETNAMESE = DOCUMENTS_ROOT / "TaiLieuTiengViet"

# ==================== DATA & VECTOR STORE ====================
DATA_DIR = BACKEND_ROOT / "data"
VECTOR_STORE_DIR = DATA_DIR

# File vector database
FAISS_INDEX = DATA_DIR / "all_faiss.index"
EMBEDDINGS_PKL = DATA_DIR / "all_embeddings.pkl"

# ==================== LOGS & TEMP ====================
LOGS_DIR = BACKEND_ROOT / "logs"
TEMP_DIR = BACKEND_ROOT / "temp"
CACHE_DIR = BACKEND_ROOT / "cache"

# ==================== DATABASE ====================
DATABASE_FILE = BACKEND_ROOT / "app.db"

# ==================== CONFIG FILES ====================
CONFIG_DIR = BACKEND_ROOT / "app" / "core"
ENV_FILE = BACKEND_ROOT / ".env"
ALEMBIC_DIR = BACKEND_ROOT / "alembic"

# ==================== FRONTEND ====================
FRONTEND_ROOT = PROJECT_ROOT / "frontend1"
FRONTEND_BUILD = FRONTEND_ROOT / "dist"

# ==================== EXTERNAL TOOLS ====================
# OCR (có thể cần điều chỉnh theo hệ điều hành)
if os.name == 'nt':  # Windows
    TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:  # Linux/Mac
    TESSERACT_PATH = "/usr/bin/tesseract"
