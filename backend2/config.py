"""
Cấu hình linh hoạt cho backend2
Điều chỉnh các thông số này phù hợp với máy của bạn
"""

import torch
from pathlib import Path

# ==================== THÔNG SỐ MÁY ====================
class DeviceConfig:
    """Cấu hình thiết bị"""
    
    # Tự động phát hiện GPU/CPU
    USE_GPU = torch.cuda.is_available()
    DEVICE = "cuda:0" if USE_GPU else "cpu"
    
    # Cấu hình GPU
    GPU_MEMORY_FRACTION = 0.8  # Sử dụng 80% GPU memory
    GPU_DEVICE_ID = 0
    
    # Cấu hình CPU
    CPU_THREADS = 4  # Số thread cho CPU
    
    @classmethod
    def get_device_info(cls):
        """Lấy thông tin thiết bị"""
        info = {
            "device": cls.DEVICE,
            "use_gpu": cls.USE_GPU,
            "gpu_available": torch.cuda.is_available(),
            "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
        }
        
        if cls.USE_GPU and torch.cuda.is_available():
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_memory"] = torch.cuda.get_device_properties(0).total_memory
        
        return info

# ==================== THÔNG SỐ MÔ HÌNH ====================
class ModelConfig:
    """Cấu hình mô hình"""
    
    # LLM Model
    LLM_MAX_TOKENS = 512  # Tăng từ 256 để có câu trả lời dài hơn
    LLM_TEMPERATURE = 0.7
    LLM_TOP_K = 50
    LLM_TOP_P = 0.95
    
    # Embedding
    EMBEDDING_TOP_K = 5  # Tăng số chunks để có context tốt hơn
    EMBEDDING_MAX_TOKENS_PER_CHUNK = 4096  # Giảm để phù hợp với context window
    
    # Quantization cho GPU
    USE_4BIT_QUANTIZATION = True
    USE_DOUBLE_QUANTIZATION = True
    
    # Memory optimization
    LOW_CPU_MEM_USAGE = True
    USE_CACHE = True

# ==================== THÔNG SỐ SERVER ====================
class ServerConfig:
    """Cấu hình server"""
    
    HOST = "0.0.0.0"
    PORT = 8001
    WORKERS = 1  # FastAPI với reload=True chỉ nên dùng 1 worker
    
    # CORS
    ALLOWED_ORIGINS = ["*"]
    ALLOW_CREDENTIALS = True
    
    # Timeout
    REQUEST_TIMEOUT = 300  # 5 phút
    STREAM_TIMEOUT = 60    # 1 phút

# ==================== THÔNG SỐ FILE ====================
class FileConfig:
    """Cấu hình file"""
    
    # Định dạng file được phép
    ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt"}
    
    # Kích thước file tối đa (MB)
    MAX_FILE_SIZE = 50
    
    # Thư mục upload
    UPLOAD_FOLDER = "documents/upload"
    
    # Chunk size cho file processing
    CHUNK_SIZE = 1024 * 1024  # 1MB

# ==================== THÔNG SỐ LOGGING ====================
class LogConfig:
    """Cấu hình logging"""
    
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = "backend2.log"
    
    # Log các thông tin quan trọng
    LOG_MODEL_LOADING = True
    LOG_REQUEST_RESPONSE = True
    LOG_ERROR_DETAILS = True

# ==================== HÀM TIỆN ÍCH ====================
def get_optimal_config():
    """Lấy cấu hình tối ưu dựa trên máy hiện tại"""
    
    device_info = DeviceConfig.get_device_info()
    
    config = {
        "device": DeviceConfig.DEVICE,
        "use_gpu": DeviceConfig.USE_GPU,
        "model_config": {
            "max_tokens": ModelConfig.LLM_MAX_TOKENS,
            "temperature": ModelConfig.LLM_TEMPERATURE,
            "top_k": ModelConfig.LLM_TOP_K,
            "top_p": ModelConfig.LLM_TOP_P,
            "embedding_top_k": ModelConfig.EMBEDDING_TOP_K,
        },
        "server_config": {
            "host": ServerConfig.HOST,
            "port": ServerConfig.PORT,
            "workers": ServerConfig.WORKERS,
        },
        "file_config": {
            "allowed_extensions": list(FileConfig.ALLOWED_EXTENSIONS),
            "max_file_size": FileConfig.MAX_FILE_SIZE,
        }
    }
    
    return config

def print_config_summary():
    """In tóm tắt cấu hình"""
    print("🔧 Backend2 Configuration Summary:")
    print("=" * 50)
    
    device_info = DeviceConfig.get_device_info()
    print(f"🖥️  Device: {device_info['device']}")
    print(f"🎮 GPU Available: {device_info['gpu_available']}")
    
    if device_info['gpu_available']:
        print(f"🎮 GPU Count: {device_info['gpu_count']}")
        print(f"🎮 GPU Name: {device_info.get('gpu_name', 'Unknown')}")
    
    print(f"⚙️  Max Tokens: {ModelConfig.LLM_MAX_TOKENS}")
    print(f"🌡️  Temperature: {ModelConfig.LLM_TEMPERATURE}")
    print(f"📡 Server: {ServerConfig.HOST}:{ServerConfig.PORT}")
    print(f"📁 Upload Folder: {FileConfig.UPLOAD_FOLDER}")
    print("=" * 50)

if __name__ == "__main__":
    print_config_summary()
