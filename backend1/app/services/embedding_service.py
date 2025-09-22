# app/services/embedding_service.py
# Service xử lý embeddings sử dụng multilingual_e5_large model với OCR và xử lý đa định dạng

import os
import logging
import numpy as np
import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import io
from datetime import datetime
import pickle
import re
from typing import List, Union, Optional, Dict, Any
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
from underthesea import sent_tokenize
import torch
import faiss
from langchain.schema import Document

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service xử lý embeddings với OCR, xử lý đa định dạng và chunking tiếng Việt"""
    
    def __init__(self, model_path: str, output_dir: str = "data"):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.output_dir = output_dir
        
        # Tạo thư mục output nếu chưa có
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Đường dẫn FAISS và pickle chung
        self.all_faiss_path = os.path.join(self.output_dir, "all_faiss.index")
        self.all_pickle_path = os.path.join(self.output_dir, "all_embeddings.pkl")
        
        logger.info(f"Sử dụng device: {self.device}")
        
    def load_model(self):
        """Load model embedding và tokenizer"""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model path không tồn tại: {self.model_path}")
            
            logger.info(f"Đang load model từ {self.model_path}")
            self.model = SentenceTransformer(self.model_path)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            logger.info("Model và tokenizer đã được load thành công")
            
        except Exception as e:
            logger.error(f"Lỗi khi load model: {e}")
            raise

    def preprocess_image(self, img: Image.Image) -> Image.Image:
        """Tiền xử lý ảnh để cải thiện OCR"""
        if img.mode != 'L':
            img = img.convert('L')
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        img = img.filter(ImageFilter.SHARPEN)
        return img

    def extract_text_from_pdf(self, pdf_path: str) -> Optional[str]:
        """OCR file PDF thành text"""
        try:
            logger.info(f"Đang OCR file: {pdf_path}")
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            full_text = ""
            ocr_config = r'--oem 3 --psm 6 -l vie'
            
            for page_num in range(total_pages):
                logger.info(f"Xử lý trang {page_num + 1}/{total_pages}...")
                page = doc.load_page(page_num)
                matrix = fitz.Matrix(2.5, 2.5)
                pix = page.get_pixmap(matrix=matrix)
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                img = self.preprocess_image(img)
                page_text = pytesseract.image_to_string(img, config=ocr_config)
                full_text += page_text.strip() + "\n"
                
            doc.close()
            logger.info(f"Hoàn thành OCR {total_pages} trang")
            return full_text
            
        except Exception as e:
            logger.error(f"Lỗi OCR cho file {pdf_path}: {e}")
            return None

    def extract_text_from_word(self, doc_path: str) -> Optional[str]:
        """Trích xuất text từ file Word (.doc, .docx)"""
        try:
            import docx
            from docx import Document as DocxDocument
            
            doc = DocxDocument(doc_path)
            full_text = ""
            
            for paragraph in doc.paragraphs:
                full_text += paragraph.text + "\n"
            
            logger.info(f"Đã trích xuất text từ Word: {doc_path}")
            return full_text
            
        except Exception as e:
            logger.error(f"Lỗi trích xuất Word cho file {doc_path}: {e}")
            return None

    def extract_text_from_txt(self, txt_path: str) -> Optional[str]:
        """Đọc text từ file .txt với nhiều encoding"""
        try:
            encodings = ['utf-8', 'utf-16', 'cp1252', 'latin-1']
            
            for encoding in encodings:
                try:
                    with open(txt_path, 'r', encoding=encoding) as f:
                        full_text = f.read()
                    logger.info(f"Đã đọc file TXT với encoding {encoding}: {txt_path}")
                    return full_text
                except UnicodeDecodeError:
                    continue
            
            logger.error(f"Không thể đọc file {txt_path} với các encoding đã thử")
            return None
            
        except Exception as e:
            logger.error(f"Lỗi đọc TXT cho file {txt_path}: {e}")
            return None

    def extract_text_from_document(self, doc_path: str) -> Optional[str]:
        """Trích xuất text từ các loại file tài liệu khác nhau"""
        try:
            file_ext = os.path.splitext(doc_path)[1].lower()
            
            if file_ext == '.pdf':
                return self.extract_text_from_pdf(doc_path)
            elif file_ext in ['.doc', '.docx']:
                return self.extract_text_from_word(doc_path)
            elif file_ext == '.txt':
                return self.extract_text_from_txt(doc_path)
            else:
                logger.warning(f"Loại file không được hỗ trợ: {file_ext}")
                return None
                
        except Exception as e:
            logger.error(f"Lỗi xử lý file {doc_path}: {e}")
            return None

    def clean_text(self, text: str) -> str:
        """Làm sạch text"""
        # Loại bỏ ký tự đặc biệt không cần thiết
        text = re.sub(r'[^\w\s.,;:()\[\]?!\"\'\-–—…°%‰≥≤→←≠=+/*<>\n\r]', '', text)
        # Xử lý gạch nối cuối dòng
        text = re.sub(r'-\n', '', text)
        # Kết hợp dòng với từ
        text = re.sub(r'\n(?=\w)', ' ', text)
        # Chuẩn hóa dấu chấm
        text = re.sub(r'\.{3,}', '...', text)
        # Chuẩn hóa xuống dòng
        text = re.sub(r'\n\s*\n', '\n\n', text)
        # Chuẩn hóa khoảng trắng
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r' *\n *', '\n', text)
        
        return text.strip()

    def split_sections(self, text: str) -> List[str]:
        """Tách text thành sections theo tiêu đề"""
        sections = re.split(r'\n(?=(?:[IVXLCDM]+\.)|(?:\d+\.)|(?:[a-z]\)))', text)
        return [s.strip() for s in sections if s.strip()]

    def split_text_to_chunks_vi(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """Chia text thành chunks dựa trên token, giữ cấu trúc section cho tiếng Việt"""
        if self.tokenizer is None:
            self.load_model()
        
        sections = self.split_sections(text)
        all_chunks = []
        
        for section in sections:
            sentences = sent_tokenize(section)
            current_chunk = []
            current_tokens = 0
            
            for sentence in sentences:
                num_tokens = len(self.tokenizer.tokenize(sentence))
                
                if current_tokens + num_tokens > chunk_size:
                    if current_chunk:
                        chunk_text = '\n'.join(current_chunk).strip()
                        all_chunks.append(chunk_text)
                    
                    # Tạo overlap
                    overlap_chunk = []
                    total = 0
                    for s in reversed(current_chunk):
                        toks = len(self.tokenizer.tokenize(s))
                        if total + toks > overlap:
                            break
                        overlap_chunk.insert(0, s)
                        total += toks
                    
                    current_chunk = overlap_chunk + [sentence]
                    current_tokens = total + num_tokens
                else:
                    current_chunk.append(sentence)
                    current_tokens += num_tokens
            
            if current_chunk:
                all_chunks.append(' '.join(current_chunk).strip())
        
        return all_chunks

    def create_embeddings(self, chunks: List[str], batch_size: int = 32) -> Optional[np.ndarray]:
        """Tạo embeddings cho chunks"""
        if self.model is None:
            self.load_model()
        
        try:
            logger.info(f"Tạo embeddings cho {len(chunks)} chunks...")
            
            # Xử lý theo batch để tránh out of memory
            embeddings = []
            
            for i in range(0, len(chunks), batch_size):
                batch_chunks = chunks[i:i + batch_size]
                batch_embeddings = self.model.encode(
                    batch_chunks,
                    convert_to_tensor=False,
                    show_progress_bar=True,
                    batch_size=batch_size
                )
                embeddings.append(batch_embeddings)
            
            # Kết hợp tất cả embeddings
            all_embeddings = np.vstack(embeddings)
            logger.info(f"Hoàn thành tạo embeddings: {all_embeddings.shape}")
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Lỗi tạo embeddings: {e}")
            return None

    def save_embeddings_to_faiss(self, chunks: List[str], embeddings: np.ndarray, 
                                doc_path: str) -> Dict[str, str]:
        """Lưu embeddings vào FAISS index và pickle"""
        doc_name = os.path.splitext(os.path.basename(doc_path))[0]
        doc_folder = os.path.join(self.output_dir, doc_name)
        os.makedirs(doc_folder, exist_ok=True)

        # Tạo data structure
        data = {
            'pdf_name': doc_name,
            'doc_path': doc_path,
            'chunks': chunks,
            'embeddings': embeddings,
            'created_at': datetime.now().isoformat()
        }

        # Lưu embeddings pickle riêng
        pickle_path = os.path.join(doc_folder, f"{doc_name}_embeddings.pkl")
        with open(pickle_path, 'wb') as f:
            pickle.dump(data, f)

        # Lưu FAISS index riêng
        index_path = os.path.join(doc_folder, f"{doc_name}_faiss.index")
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings.astype(np.float32))
        faiss.write_index(index, index_path)

        # Cập nhật FAISS chung
        if os.path.exists(self.all_faiss_path):
            index_all = faiss.read_index(self.all_faiss_path)
        else:
            index_all = faiss.IndexFlatL2(dim)
        index_all.add(embeddings.astype(np.float32))
        faiss.write_index(index_all, self.all_faiss_path)

        # Cập nhật pickle chung
        if os.path.exists(self.all_pickle_path):
            with open(self.all_pickle_path, 'rb') as f:
                all_data = pickle.load(f)
        else:
            all_data = []
        all_data.append(data)
        with open(self.all_pickle_path, 'wb') as f:
            pickle.dump(all_data, f)

        logger.info(f"Đã lưu embeddings: {pickle_path}")
        logger.info(f"Đã lưu FAISS index: {index_path}")

        return {
            "pickle_path": pickle_path,
            "faiss_path": index_path,
            "all_faiss_path": self.all_faiss_path,
            "all_pickle_path": self.all_pickle_path
        }

    def process_document(self, doc_path: str, chunk_size: int = 512, 
                        overlap: int = 50) -> Optional[Dict[str, Any]]:
        """Xử lý toàn bộ một document: extract -> clean -> chunk -> embed -> save"""
        try:
            logger.info(f"Bắt đầu xử lý document: {doc_path}")
            
            # 1. Trích xuất text
            raw_text = self.extract_text_from_document(doc_path)
            if not raw_text:
                return None
            
            # 2. Làm sạch text
            cleaned_text = self.clean_text(raw_text)
            
            # 3. Chia thành chunks
            chunks = self.split_text_to_chunks_vi(cleaned_text, chunk_size, overlap)
            logger.info(f"Đã tạo {len(chunks)} chunks")
            
            # 4. Tạo embeddings
            embeddings = self.create_embeddings(chunks)
            if embeddings is None:
                return None
            
            # 5. Lưu vào FAISS
            paths = self.save_embeddings_to_faiss(chunks, embeddings, doc_path)
            
            return {
                "doc_path": doc_path,
                "num_chunks": len(chunks),
                "embedding_shape": embeddings.shape,
                "paths": paths,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Lỗi xử lý document {doc_path}: {e}")
            return {
                "doc_path": doc_path,
                "status": "error",
                "error": str(e)
            }

    def is_document_embedded(self, doc_path: str) -> bool:
        """Kiểm tra xem file tài liệu đã được embedding hay chưa"""
        if not os.path.exists(self.all_pickle_path):
            return False
        
        doc_name = os.path.splitext(os.path.basename(doc_path))[0]
        
        try:
            with open(self.all_pickle_path, 'rb') as f:
                all_data = pickle.load(f)
            existing_doc_names = {entry['pdf_name'] for entry in all_data}
            return doc_name in existing_doc_names
        except Exception as e:
            logger.error(f"Lỗi kiểm tra document embedded: {e}")
            return False

    def get_all_document_files(self, root_folder: str) -> List[str]:
        """Quét đệ quy tất cả thư mục con để tìm các file tài liệu"""
        supported_extensions = ['.pdf', '.doc', '.docx', '.txt']
        document_files = []
        
        for root, dirs, files in os.walk(root_folder):
            for file in files:
                if any(file.lower().endswith(ext) for ext in supported_extensions):
                    full_path = os.path.join(root, file)
                    document_files.append(full_path)
        
        return document_files

    def process_all_documents(self, input_folders: List[str], 
                             force_rebuild: bool = False) -> Dict[str, Any]:
        """Xử lý tất cả documents trong các folders"""
        try:
            all_document_files = []
            
            # Lấy tất cả files từ các folders
            for folder in input_folders:
                if os.path.exists(folder):
                    files = self.get_all_document_files(folder)
                    all_document_files.extend(files)
                    logger.info(f"Tìm thấy {len(files)} files trong {folder}")
                else:
                    logger.warning(f"Folder không tồn tại: {folder}")
            
            logger.info(f"Tổng cộng {len(all_document_files)} files để xử lý")
            
            # Xử lý từng file
            results = []
            processed_count = 0
            skipped_count = 0
            error_count = 0
            
            for doc_path in all_document_files:
                if not force_rebuild and self.is_document_embedded(doc_path):
                    logger.info(f"File đã được embedding, bỏ qua: {os.path.basename(doc_path)}")
                    skipped_count += 1
                    continue
                
                result = self.process_document(doc_path)
                if result:
                    if result.get("status") == "success":
                        processed_count += 1
                    else:
                        error_count += 1
                    results.append(result)
            
            return {
                "total_files": len(all_document_files),
                "processed": processed_count,
                "skipped": skipped_count,
                "errors": error_count,
                "results": results,
                "all_faiss_path": self.all_faiss_path,
                "all_pickle_path": self.all_pickle_path
            }
            
        except Exception as e:
            logger.error(f"Lỗi xử lý tất cả documents: {e}")
            return {"error": str(e)}

    # Giữ lại các phương thức cũ để tương thích
    def encode_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Tạo embeddings cho danh sách text"""
        return self.create_embeddings(texts, batch_size)
    
    def encode_single_text(self, text: str) -> np.ndarray:
        """Tạo embedding cho một text"""
        if self.model is None:
            self.load_model()
        
        try:
            embedding = self.model.encode([text], convert_to_tensor=False)
            return embedding[0]
        except Exception as e:
            logger.error(f"Lỗi khi tạo embedding cho text: {e}")
            raise
    
    def encode_documents(self, documents: List[Document], batch_size: int = 32) -> List[np.ndarray]:
        """Tạo embeddings cho danh sách documents"""
        texts = [doc.page_content for doc in documents]
        embeddings = self.encode_texts(texts, batch_size)
        return [embeddings[i] for i in range(len(embeddings))]
    
    def get_model_info(self) -> dict:
        """Lấy thông tin về model"""
        if self.model is None:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "model_path": self.model_path,
            "device": str(self.device),
            "output_dir": self.output_dir,
            "all_faiss_path": self.all_faiss_path,
            "all_pickle_path": self.all_pickle_path,
            "max_seq_length": getattr(self.model, 'max_seq_length', 'unknown'),
            "embedding_dimension": getattr(self.model, 'get_sentence_embedding_dimension', lambda: 'unknown')()
        }
