from pydantic import BaseModel
from typing import Optional, List

class QueryRequest(BaseModel):
    query: str
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.7
    top_k: Optional[int] = 50
    top_p: Optional[float] = 0.95

class ChatResponse(BaseModel):
    response: str
    status: str = "success"
    error: Optional[str] = None

class StreamToken(BaseModel):
    type: str  # "start", "token", "end", "error"
    content: Optional[str] = None
    message: Optional[str] = None
    response_length: Optional[int] = None

class FileUploadResponse(BaseModel):
    filename: str
    status: str
    message: str
    file_path: Optional[str] = None

class SystemStatus(BaseModel):
    status: str
    llm_model_loaded: bool
    embedding_model_loaded: bool
    device: str
    message: str
