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
    if filename_lower.endswith((".mp4", ".mov", ".avi", ".webm")):
        file_type = "video"
    else:
        file_type = "image"

    # -----------------------------
    # Read raw bytes
    # -----------------------------
    raw_bytes = await file.read()
    print(f"📥 Received file: {file.filename}, size={len(raw_bytes) / 1024:.1f} KB")

    # -----------------------------
    # Normalize image input (CRITICAL)
    # -----------------------------
    if file_type == "image":
        try:
            img = Image.open(io.BytesIO(raw_bytes))
            img = img.convert("RGB")  # force RGB

            # HARD DOWNSCALE for phone/Mac photos
            MAX_SIZE = 1024
            img.thumbnail((MAX_SIZE, MAX_SIZE))

            print(f"🖼️ Normalized image size: {img.size}")

            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=95)
            file_bytes = buf.getvalue()

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
        file_bytes = raw_bytes

    # -----------------------------
    # Save temp file
    # -----------------------------
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        # -----------------------------
        # SINGLE SOURCE OF TRUTH
        # -----------------------------
        result = orchestrate_detection(tmp_path, file_type)

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
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
