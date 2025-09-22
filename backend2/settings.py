from pathlib import Path
import sys

file_path = Path(__file__).resolve()
root_path = file_path.parent

if root_path not in sys.path:
    sys.path.append(str(root_path))

# Đường dẫn gốc của API
ROOT_API = root_path
ROOT_PROJECT = root_path.parent

# Thư mục chứa file tải lên
FILE_FOLDER = ROOT_PROJECT / "documents" / "upload"

# Thư mục chứa model và kết quả embedding từ backend hiện tại
EMBEDDING_FOLDER = ROOT_PROJECT / "backend" / "data"
EMBEDDING_MODEL_FOLDER = Path("D:/Vian/MODELS/multilingual_e5_large")
FAISS_PATH = EMBEDDING_FOLDER / "all_faiss.index"
PICKLE_PATH = EMBEDDING_FOLDER / "all_embeddings.pkl"

# Thư mục chứa mô hình LLM - sử dụng từ backend hiện tại
LLM_MODEL_FOLDER = Path("D:/Vian/MODELS")
MODEL = LLM_MODEL_FOLDER / "vinallama-2.7b-chat"

# Chỉ cho phép các định dạng file nhất định
ALLOWED_FILE = {".pdf", ".doc", ".docx", ".txt"}

# Cấu hình API
API_HOST = "0.0.0.0"
API_PORT = 8001
API_TITLE = "Chatbot Security API"
API_DESCRIPTION = "API cho chatbot an toàn thông tin"
API_VERSION = "1.0.0"
