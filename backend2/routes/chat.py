from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from utils.chat import get_response, get_response_stream
from models.chat import QueryRequest, ChatResponse, StreamToken
import json

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def get_response_endpoint(request: QueryRequest):
    """
    Trả về câu trả lời từ chatbot dựa trên câu hỏi
    """
    try:
        response = get_response(
            request.query,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_k=request.top_k,
            top_p=request.top_p
        )
        return ChatResponse(response=response, status="success")
    except Exception as e:
        return ChatResponse(
            response="", 
            status="error", 
            error=f"Lỗi xử lý: {str(e)}"
        )

@router.post("/chat/stream")
def get_response_stream_endpoint(request: QueryRequest):
    """
    Trả về câu trả lời từ chatbot dưới dạng stream
    """
    def event_generator():
        try:
            # Start event
            start_data = {
                'type': 'start', 
                'message': 'Đang xử lý câu hỏi...'
            }
            yield f"data: {json.dumps(start_data, ensure_ascii=False)}\n\n"
            
            # Stream tokens
            full_response = ""
            for token in get_response_stream(
                request.query,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_k=request.top_k,
                top_p=request.top_p
            ):
                if token.strip():  # Chỉ gửi token không rỗng
                    full_response += token
                    
                    # Token event
                    token_data = {
                        'type': 'token', 
                        'content': token
                    }
                    yield f"data: {json.dumps(token_data, ensure_ascii=False)}\n\n"
            
            # End event
            end_data = {
                'type': 'end',
                'response_length': len(full_response)
            }
            yield f"data: {json.dumps(end_data, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            # Error event
            error_data = {
                'type': 'error', 
                'message': f"Lỗi server: {str(e)}"
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )
