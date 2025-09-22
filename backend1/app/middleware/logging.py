# app/middleware/logging.py
# Middleware để logging requests và responses
# Ghi lại thông tin về các request đến API

import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware để log các request và response"""
    
    async def dispatch(self, request: Request, call_next):
        # Ghi lại thời gian bắt đầu request
        start_time = time.time()
        
        # Log thông tin request
        logger.info(
            f"Request: {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        # Xử lý request
        response = await call_next(request)
        
        # Tính thời gian xử lý
        process_time = time.time() - start_time
        
        # Log thông tin response
        logger.info(
            f"Response: {response.status_code} - "
            f"Process time: {process_time:.4f}s"
        )
        
        # Thêm header thời gian xử lý
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
