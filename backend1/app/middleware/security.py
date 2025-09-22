# app/middleware/security.py
# Middleware bảo mật
# Chứa các middleware để tăng cường bảo mật cho API

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware thêm các security headers"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Thêm các security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware giới hạn tần suất request (đơn giản)"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Làm sạch các record cũ
        if client_ip in self.clients:
            self.clients[client_ip] = [
                timestamp for timestamp in self.clients[client_ip]
                if current_time - timestamp < self.period
            ]
        else:
            self.clients[client_ip] = []
        
        # Kiểm tra rate limit
        if len(self.clients[client_ip]) >= self.calls:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=429,
                detail="Quá nhiều request. Vui lòng thử lại sau."
            )
        
        # Thêm timestamp hiện tại
        self.clients[client_ip].append(current_time)
        
        response = await call_next(request)
        return response
