# Backend Setup Guide

Complete guide for setting up the DeepGuard Python backend locally.

## Quick Start

```bash
# 1. Create backend directory
mkdir backend && cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env with your Firebase credentials

# 5. Run server
uvicorn app.main:app --reload
```

## Complete File Structure

Create these files in your `backend/` directory:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── predict.py
│   │   ├── upload.py
│   │   └── train.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── detector.py
│   └── services/
│       ├── __init__.py
│       ├── firebase.py
│       └── preprocessing.py
├── ml/
│   ├── train.py
│   ├── inference.py
│   └── dataset.py
├── models/                    # Saved ML models go here
├── data/                      # Training data
│   ├── train/
│   │   ├── real/
│   │   └── fake/
│   └── val/
│       ├── real/
│       └── fake/
├── requirements.txt
├── .env.example
├── .env
└── Dockerfile
```

## Environment Variables

Create `.env.example`:

```env
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Firebase
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
FIREBASE_STORAGE_BUCKET=your-project.appspot.com

# ML Model
MODEL_PATH=./models/deepfake_detector.pth
USE_GPU=false

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Configuration Module

Create `app/config.py`:

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Firebase
    firebase_credentials_path: str = "./firebase-credentials.json"
    firebase_storage_bucket: str = ""
    
    # ML
    model_path: str = "./models/deepfake_detector.pth"
    use_gpu: bool = False
    
    # CORS
    allowed_origins: str = "http://localhost:5173"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
```

## Complete Main App

Create `app/main.py`:

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.routes import predict, upload, train
from app.models.detector import DeepfakeDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model instance
detector = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load ML model on startup."""
    global detector
    logger.info("Loading deepfake detection model...")
    detector = DeepfakeDetector(model_path=settings.model_path if settings.model_path else None)
    logger.info("Model loaded successfully!")
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title="DeepGuard API",
    description="AI-Powered Deepfake Detection API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
origins = settings.allowed_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(predict.router, prefix="/api", tags=["Prediction"])
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(train.router, prefix="/api", tags=["Training"])

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "deepguard-api",
        "model_loaded": detector is not None
    }

@app.get("/")
async def root():
    return {
        "message": "DeepGuard API - Deepfake Detection Service",
        "docs": "/docs",
        "health": "/health"
    }

def get_detector():
    """Dependency to get the detector instance."""
    return detector
```

## Complete Prediction Route

Create `app/routes/predict.py`:

```python
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Optional
import tempfile
import os
import logging
from datetime import datetime

from app.models.detector import DeepfakeDetector
from app.services.preprocessing import preprocess_image, extract_frames, detect_faces
from app.main import get_detector

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp", "image/gif"]
ALLOWED_VIDEO_TYPES = ["video/mp4", "video/webm", "video/quicktime"]
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

@router.post("/predict")
async def predict(
    file: UploadFile = File(...),
    detector: DeepfakeDetector = Depends(get_detector)
):
    """
    Analyze uploaded media for deepfake content.
    
    - **file**: Image or video file to analyze
    
    Returns verdict (REAL/FAKE) and confidence score with detailed breakdown.
    """
    
    # Validate file type
    content_type = file.content_type
    if content_type not in ALLOWED_IMAGE_TYPES + ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {content_type}. Allowed: images and videos"
        )
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Save to temporary file
    suffix = os.path.splitext(file.filename)[1] if file.filename else ".tmp"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        logger.info(f"Processing file: {file.filename} ({content_type})")
        
        if content_type in ALLOWED_IMAGE_TYPES:
            # Process image
            image = preprocess_image(tmp_path)
            faces = detect_faces(image)
            result = detector.predict(image)
            
            # Add face detection info
            result["faces_detected"] = len(faces)
            
        else:
            # Process video - extract and analyze frames
            frames = extract_frames(tmp_path, max_frames=16)
            
            if not frames:
                raise HTTPException(status_code=400, detail="Could not extract frames from video")
            
            # Analyze each frame
            results = []
            for frame in frames:
                frame_result = detector.predict(frame)
                results.append(frame_result)
            
            # Aggregate results
            avg_confidence = sum(r["confidence"] for r in results) / len(results)
            fake_votes = sum(1 for r in results if r["verdict"] == "FAKE")
            
            # Majority voting
            is_fake = fake_votes > len(results) / 2
            
            result = {
                "verdict": "FAKE" if is_fake else "REAL",
                "confidence": round(avg_confidence, 1),
                "frames_analyzed": len(frames),
                "fake_frame_ratio": round(fake_votes / len(frames), 2)
            }
        
        # Build response
        response = {
            "verdict": result["verdict"],
            "confidence": result["confidence"],
            "fileName": file.filename,
            "fileSize": len(content),
            "fileType": "image" if content_type in ALLOWED_IMAGE_TYPES else "video",
            "analyzedAt": datetime.utcnow().isoformat(),
            "details": {
                "facialAnalysis": result.get("facial_score", 85),
                "temporalConsistency": result.get("temporal_score", 82),
                "artifactDetection": result.get("artifact_score", 78),
                "metadataAnalysis": result.get("metadata_score", 90)
            }
        }
        
        if "faces_detected" in result:
            response["facesDetected"] = result["faces_detected"]
        if "frames_analyzed" in result:
            response["framesAnalyzed"] = result["frames_analyzed"]
        
        logger.info(f"Analysis complete: {result['verdict']} ({result['confidence']}%)")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        # Cleanup temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

@router.post("/predict/batch")
async def predict_batch(
    files: list[UploadFile] = File(...),
    detector: DeepfakeDetector = Depends(get_detector)
):
    """Analyze multiple files at once."""
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files per batch")
    
    results = []
    for file in files:
        try:
            result = await predict(file, detector)
            results.append({"status": "success", "data": result})
        except HTTPException as e:
            results.append({"status": "error", "fileName": file.filename, "error": e.detail})
        except Exception as e:
            results.append({"status": "error", "fileName": file.filename, "error": str(e)})
    
    return {"results": results, "total": len(files)}
```

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Predict image
curl -X POST "http://localhost:8000/api/predict" \
  -F "file=@test_image.jpg"

# Predict video
curl -X POST "http://localhost:8000/api/predict" \
  -F "file=@test_video.mp4"
```

### Using Python

```python
import requests

# Analyze an image
with open("test_image.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/predict",
        files={"file": f}
    )
    print(response.json())
```

## Connecting Frontend to Backend

Update your frontend to call the real API. In `src/hooks/useAnalysis.ts`, replace the simulated analysis:

```typescript
const analyzeMedia = useCallback(async (file: File) => {
  setIsAnalyzing(true);
  setResult(null);

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("http://localhost:8000/api/predict", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Analysis failed");
    }

    const data = await response.json();
    
    const analysisResult: AnalysisResultData = {
      verdict: data.verdict,
      confidence: data.confidence,
      fileName: data.fileName,
      analyzedAt: new Date(data.analyzedAt),
      details: data.details,
    };

    setResult(analysisResult);
    // ... rest of history logic
    
  } catch (error) {
    console.error("Analysis error:", error);
    throw error;
  } finally {
    setIsAnalyzing(false);
  }
}, []);
```

## Troubleshooting

### Common Issues

1. **CORS errors**: Ensure your frontend URL is in `ALLOWED_ORIGINS`
2. **Model not found**: Check `MODEL_PATH` in `.env` or use pretrained weights
3. **GPU not detected**: Set `USE_GPU=false` for CPU-only mode
4. **File too large**: Adjust `MAX_FILE_SIZE` in predict.py

### Debug Mode

Run with verbose logging:

```bash
uvicorn app.main:app --reload --log-level debug
```
