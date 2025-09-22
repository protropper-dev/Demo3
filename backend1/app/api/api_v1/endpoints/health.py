# app/api/api_v1/endpoints/health.py
# Endpoint kiểm tra sức khỏe của API
# Cung cấp thông tin về trạng thái hệ thống, database, và các service

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.schemas.base import MessageSchema
from datetime import datetime
import os

router = APIRouter()

@router.get("/", response_model=MessageSchema)
async def health_check():
    """Kiểm tra sức khỏe cơ bản của API"""
    return {"message": "API đang hoạt động bình thường"}

@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Kiểm tra sức khỏe chi tiết bao gồm database"""
    try:
        # Kiểm tra kết nối database
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database": db_status,
        "services": {
            "api": "healthy",
            "database": db_status
        }
    }

@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Kiểm tra readiness - API sẵn sàng nhận request"""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")

@router.get("/live")
async def liveness_check():
    """Kiểm tra liveness - API còn sống"""
    return {"status": "alive"}
