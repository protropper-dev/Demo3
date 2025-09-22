# app/core/models.py
# Model loading và quản lý cho backend1 (tích hợp từ backend2)

import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ModelManager:
    """Quản lý việc load và sử dụng các models"""
    
    def __init__(self):
        self.llm_model = None
        self.llm_tokenizer = None
        self.embedding_model = None
        self.embedding_tokenizer = None
        self.device = None
        self._initialized = False
    
    def initialize(self):
        """Khởi tạo tất cả models"""
        if self._initialized:
            return
        
        try:
            # Auto-detect device
            if torch.cuda.is_available():
                self.device = torch.device("cuda:0")
                logger.info("✅ Sử dụng GPU CUDA")
            else:
                self.device = torch.device("cpu")
                logger.info("⚠️  Sử dụng CPU (không có GPU)")
            
            # Load LLM model
            self._load_llm_model()
            
            # Load embedding model
            self._load_embedding_model()
            
            self._initialized = True
            logger.info("✅ Tất cả models đã được khởi tạo thành công!")
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi khởi tạo models: {e}")
            raise
    
    def _load_llm_model(self):
        """Load LLM model"""
        try:
            logger.info(f"🔄 Đang tải LLM model từ: {settings.LLM_MODEL_PATH}")
            
            self.llm_tokenizer = AutoTokenizer.from_pretrained(
                settings.LLM_MODEL_PATH,
                trust_remote_code=True,  # Thêm trust_remote_code
                padding_side="left"  # Thêm padding_side
            )
            self.llm_tokenizer.pad_token = self.llm_tokenizer.eos_token
            
            if self.device.type == "cpu":
                # Cấu hình cho CPU
                self.llm_model = AutoModelForCausalLM.from_pretrained(
                    settings.LLM_MODEL_PATH,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=settings.LOW_CPU_MEM_USAGE,
                    device_map="cpu"
                )
            else:
                # Cấu hình cho GPU với quantization
                from transformers import BitsAndBytesConfig
                
                if settings.USE_4BIT_QUANTIZATION:
                    bnb_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_use_double_quant=settings.USE_DOUBLE_QUANTIZATION,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_compute_dtype=torch.float16,
                    )
                    
                    self.llm_model = AutoModelForCausalLM.from_pretrained(
                        settings.LLM_MODEL_PATH,
                        device_map="auto",  # Thay đổi từ "cuda:0" thành "auto"
                        torch_dtype=torch.float16,
                        quantization_config=bnb_config,
                        trust_remote_code=True,  # Thêm trust_remote_code
                    )
                else:
                    self.llm_model = AutoModelForCausalLM.from_pretrained(
                        settings.LLM_MODEL_PATH,
                        device_map="auto",  # Thay đổi từ "cuda:0" thành "auto"
                        torch_dtype=torch.float16,
                        trust_remote_code=True,  # Thêm trust_remote_code
                    )
            
            # Kiểm tra xem model có phải là quantized không trước khi gọi .eval()
            if hasattr(self.llm_model, 'config') and hasattr(self.llm_model.config, 'quantization_config'):
                logger.info("✅ LLM model (quantized) đã được tải thành công")
            else:
                self.llm_model.eval()
                logger.info("✅ LLM model đã được tải thành công")
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi tải LLM model: {e}")
            self.llm_model = None
            self.llm_tokenizer = None
    
    def _load_embedding_model(self):
        """Load embedding model"""
        try:
            logger.info(f"🔄 Đang tải Embedding model từ: {settings.EMBEDDING_MODEL_PATH}")
            
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL_PATH)
            self.embedding_tokenizer = AutoTokenizer.from_pretrained(settings.EMBEDDING_MODEL_PATH)
            
            logger.info("✅ Embedding model đã được tải thành công")
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi tải Embedding model: {e}")
            self.embedding_model = None
            self.embedding_tokenizer = None
    
    def get_models_status(self):
        """Lấy trạng thái của các models"""
        return {
            "llm_model_loaded": self.llm_model is not None,
            "llm_tokenizer_loaded": self.llm_tokenizer is not None,
            "embedding_model_loaded": self.embedding_model is not None,
            "embedding_tokenizer_loaded": self.embedding_tokenizer is not None,
            "device": str(self.device) if self.device else "unknown",
            "initialized": self._initialized,
            "cuda_available": torch.cuda.is_available(),
            "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        }
    
    def is_ready(self):
        """Kiểm tra xem tất cả models đã sẵn sàng chưa"""
        return (
            self.llm_model is not None
            and self.llm_tokenizer is not None
            and self.embedding_model is not None
            and self.embedding_tokenizer is not None
        )

# Global model manager instance
model_manager = ModelManager()

def get_model_manager():
    """Lấy model manager instance"""
    return model_manager
