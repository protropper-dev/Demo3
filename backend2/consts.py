import settings
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os
from config import DeviceConfig, ModelConfig

# Sử dụng cấu hình từ config
device = torch.device(DeviceConfig.DEVICE)
print(f"✅ Sử dụng thiết bị: {DeviceConfig.DEVICE}")

# Load LLM model với cấu hình tối ưu cho máy hiện tại
llm_model_path = str(settings.MODEL)
print(f"🔄 Đang tải LLM model từ: {llm_model_path}")

try:
    llm_tokenizer = AutoTokenizer.from_pretrained(llm_model_path)
    llm_tokenizer.pad_token = llm_tokenizer.eos_token  # Set padding token
    
    # Cấu hình quantization cho CPU hoặc GPU yếu
    if device.type == "cpu":
        # Cấu hình cho CPU
        llm_model = AutoModelForCausalLM.from_pretrained(
            llm_model_path,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=ModelConfig.LOW_CPU_MEM_USAGE,
            device_map="cpu"
        )
    else:
        # Cấu hình cho GPU với quantization
        from transformers import BitsAndBytesConfig
        
        if ModelConfig.USE_4BIT_QUANTIZATION:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=ModelConfig.USE_DOUBLE_QUANTIZATION,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
            )
            
            llm_model = AutoModelForCausalLM.from_pretrained(
                llm_model_path,
                device_map="cuda:0",
                torch_dtype=torch.float16,
                quantization_config=bnb_config,
            )
        else:
            llm_model = AutoModelForCausalLM.from_pretrained(
                llm_model_path,
                device_map="cuda:0",
                torch_dtype=torch.float16,
            )
    
    llm_model.eval()  # Chuyển model sang chế độ đánh giá
    print("✅ LLM model đã được tải thành công")
    
except Exception as e:
    print(f"❌ Lỗi khi tải LLM model: {e}")
    llm_model = None
    llm_tokenizer = None

# Load embedding model
embedding_model_path = str(settings.EMBEDDING_MODEL_FOLDER)
print(f"🔄 Đang tải Embedding model từ: {embedding_model_path}")

try:
    embedding_model = SentenceTransformer(embedding_model_path)
    embedding_tokenizer = AutoTokenizer.from_pretrained(embedding_model_path)
    print("✅ Embedding model đã được tải thành công")
except Exception as e:
    print(f"❌ Lỗi khi tải Embedding model: {e}")
    embedding_model = None
    embedding_tokenizer = None

# Kiểm tra các model đã được tải thành công
models_loaded = (
    embedding_model is not None
    and embedding_tokenizer is not None
    and llm_model is not None
    and llm_tokenizer is not None
)

if not models_loaded:
    print("⚠️  Cảnh báo: Một số mô hình chưa được tải thành công.")
    print("   Backend vẫn sẽ khởi động nhưng một số chức năng có thể không hoạt động.")
    print("   Vui lòng kiểm tra đường dẫn mô hình trong settings.py")
else:
    print("✅ Tất cả mô hình đã được tải thành công!")
