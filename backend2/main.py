from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import system, file, embedding, chat
import settings

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# Bật CORS cho mọi nguồn
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép mọi origin
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả các phương thức
    allow_headers=["*"],  # Cho phép tất cả headers
)

# Include các router
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(system.router, prefix="/api/v1", tags=["System"])
app.include_router(file.router, prefix="/api/v1", tags=["File"])
app.include_router(embedding.router, prefix="/api/v1", tags=["Embedding"])

@app.get("/")
async def root():
    return {
        "message": "Chatbot Security API",
        "version": settings.API_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
