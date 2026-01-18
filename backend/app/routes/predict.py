from fastapi import APIRouter, UploadFile, File
from datetime import datetime
import tempfile
import os
import io
from PIL import Image

from app.orchestrator import orchestrate_detection
from app.schemas import PredictResponse, ForensicDetails, EngineInfo

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
async def predict(file: UploadFile = File(...)):
    filename_lower = file.filename.lower()

    # -----------------------------
    # Determine file type
    # -----------------------------
    file_type = (
        "video"
        if filename_lower.endswith((".mp4", ".mov", ".avi", ".webm"))
        else "image"
    )

    raw_bytes = await file.read()
    print(f"📥 Received file: {file.filename}, size={len(raw_bytes)/1024:.1f} KB")

    # -----------------------------
    # Save ORIGINAL file (for EXIF)
    # -----------------------------
    with tempfile.NamedTemporaryFile(delete=False) as orig:
        orig.write(raw_bytes)
        orig_path = orig.name

    # -----------------------------
    # Create NORMALIZED image (for CNN / FFT)
    # -----------------------------
    if file_type == "image":
        try:
            img = Image.open(io.BytesIO(raw_bytes))
            img = img.convert("RGB")

            MAX_SIZE = 1024
            img.thumbnail((MAX_SIZE, MAX_SIZE))
            print(f"🖼️ Normalized image size: {img.size}")

            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=95)
            norm_bytes = buf.getvalue()

        except Exception as e:
            print("❌ Image normalization failed:", e)
            return PredictResponse(
                verdict="UNKNOWN",
                confidence=0,
                fileName=file.filename,
                fileType=file_type,
                analyzedAt=datetime.utcnow(),
                details=ForensicDetails(
                    facialAnalysis=0,
                    temporalConsistency=0,
                    artifactDetection=0,
                    metadataAnalysis=0,
                ),
                engine=EngineInfo(
                    primary="input-validation",
                    secondary=None,
                ),
                explanation="Unsupported or corrupted image file.",
            )
    else:
        norm_bytes = raw_bytes

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as norm:
        norm.write(norm_bytes)
        norm_path = norm.name

    try:
        # -----------------------------
        # SINGLE SOURCE OF TRUTH
        # -----------------------------
        result = orchestrate_detection(
            file_path=norm_path,
            file_type=file_type,
            original_path=orig_path
        )

        return PredictResponse(
            verdict=result["verdict"],
            confidence=result["confidence"],
            fileName=file.filename,
            fileType=file_type,
            analyzedAt=datetime.utcnow(),
            details=ForensicDetails(
                facialAnalysis=result["details"]["facialAnalysis"],
                temporalConsistency=result["details"]["temporalConsistency"],
                artifactDetection=result["details"]["artifactDetection"],
                metadataAnalysis=result["details"]["metadataAnalysis"],
            ),
            engine=EngineInfo(
                primary=result["engine"]["primary"],
                secondary=result["engine"]["secondary"],
            ),
        )

    finally:
        for p in (orig_path, norm_path):
            if os.path.exists(p):
                os.remove(p)
