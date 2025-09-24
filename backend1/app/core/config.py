# app/core/config.py
# File cấu hình chính của ứng dụng
# Chứa các biến môi trường, cài đặt database, và các thông số khác

from pydantic_settings import BaseSettings
from typing import List
import os
from .paths import (
    EMBEDDING_MODEL, LLM_MODEL, DOCUMENTS_ROOT, DOCS_LUAT, 
    DOCS_ENGLISH, DOCS_VIETNAMESE, DOCUMENTS_UPLOAD, DATA_DIR, 
    FAISS_INDEX, EMBEDDINGS_PKL, TESSERACT_PATH
)

class Settings(BaseSettings):
    """Cài đặt chính của ứng dụng"""
    
    # Thông tin dự án
    PROJECT_NAME: str = "FastAPI Backend"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API Backend sử dụng FastAPI"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:8000"]
    
    # File Upload
    MAX_FILE_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "uploads"
    DOCUMENTS_UPLOAD_DIR: str = "documents/upload"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Model paths - sử dụng paths.py
    EMBEDDING_MODEL_PATH: str = str(EMBEDDING_MODEL)
    LLM_MODEL_PATH: str = str(LLM_MODEL)
    
    # Document paths - sử dụng paths.py
    DOCUMENTS_PATH: str = str(DOCUMENTS_ROOT)
    LUAT_DOCS_PATH: str = str(DOCS_LUAT)
    ENGLISH_DOCS_PATH: str = str(DOCS_ENGLISH)
    VIETNAMESE_DOCS_PATH: str = str(DOCS_VIETNAMESE)
    DOCUMENTS_UPLOAD_DIR: str = str(DOCUMENTS_UPLOAD)
    
    # Vector store - sử dụng paths.py
    VECTOR_STORE_PATH: str = str(DATA_DIR)
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # RAG settings
    TOP_K_RESULTS: int = 10
    SIMILARITY_THRESHOLD: float = 0.3  # 0.7 Tạm thời giảm để debug
    
    # RAG data paths - sử dụng paths.py
    FAISS_PATH: str = str(FAISS_INDEX)
    PICKLE_PATH: str = str(EMBEDDINGS_PKL)
    
    # OCR settings - sử dụng paths.py
    TESSERACT_PATH: str = TESSERACT_PATH
    OCR_LANGUAGES: str = "vie+eng"  # Vietnamese + English
    OCR_PSM: int = 6  # Page segmentation mode
    USE_OCR: bool = True  # Enable/disable OCR
    
    # Model settings
    USE_QUANTIZATION: bool = False  # Tắt quantization vì gặp lỗi device_map  # Enable quantization để tiết kiệm memory
    MAX_MEMORY: str = "90%"  # Sử dụng 90% VRAM
    
    # Backend2 integration settings
    USE_4BIT_QUANTIZATION: bool = True
    USE_DOUBLE_QUANTIZATION: bool = True
    LOW_CPU_MEM_USAGE: bool = True
    USE_CACHE: bool = True
    
    # Device configuration
    DEVICE: str = "cuda:0"  # Sẽ được tự động detect
    GPU_MEMORY_FRACTION: float = 0.8
    GPU_DEVICE_ID: int = 0
    CPU_THREADS: int = 4
    
    # Model generation settings
    LLM_MAX_TOKENS: int = 512
    LLM_TEMPERATURE: float = 0.7
    LLM_TOP_K: int = 50
    LLM_TOP_P: float = 0.95
    EMBEDDING_TOP_K: int = 5
    EMBEDDING_MAX_TOKENS_PER_CHUNK: int = 4096
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Tạo instance settings
settings = Settings()
