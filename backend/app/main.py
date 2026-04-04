import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (one level above backend/)
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)
    print("✅ Loaded .env from: " + str(_env_path))
else:
    # Try current working directory
    load_dotenv()
    print("⚠️ .env not found at " + str(_env_path) + ", trying CWD")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.predict import router as predict_router

app = FastAPI(
    title="DeepGuard API",
    description="Forensic Deepfake Detection Backend",
    version="1.0.0"
)

# 🔥 CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can later restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "DeepGuard backend is running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "deepguard-backend"
    }
