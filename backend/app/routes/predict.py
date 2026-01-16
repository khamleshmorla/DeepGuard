from fastapi import APIRouter, UploadFile, File
from datetime import datetime
import tempfile
import os

from app.engines.vision_llm import analyze_image_with_gemini
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
    # Read file bytes (for Gemini)
    # -----------------------------
    file_bytes = await file.read()

    # -----------------------------
    # Save uploaded file temporarily (for heuristics / video)
    # -----------------------------
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        # -----------------------------
        # STEP 5A — Run existing detection pipeline
        # (heuristics, placeholders, etc.)
        # -----------------------------
        base_result = orchestrate_detection(tmp_path, file_type)

        # -----------------------------
        # STEP 5B — Gemini Vision (IMAGE ONLY)
        # -----------------------------
        gemini_result = None

        if file_type == "image":
            try:
                gemini_result = analyze_image_with_gemini(file_bytes)
            except Exception as e:
                gemini_result = {
                    "verdict": "FAKE",
                    "confidence": 50,
                    "explanation": "Gemini Vision analysis failed safely."
                }

        # -----------------------------
        # STEP 5C — TEMPORARY DECISION LOGIC
        # (Gemini drives verdict for now)
        # -----------------------------
        if gemini_result:
            verdict = gemini_result["verdict"]
            confidence = gemini_result["confidence"]
            explanation = gemini_result["explanation"]

            engine_primary = "gemini-vision"
            engine_secondary = base_result["engine"]["primary"]
        else:
            verdict = base_result["verdict"]
            confidence = base_result["confidence"]
            explanation = "Gemini Vision not applied."

            engine_primary = base_result["engine"]["primary"]
            engine_secondary = base_result["engine"]["secondary"]

        # -----------------------------
        # Return standardized response
        # -----------------------------
        return PredictResponse(
            verdict=verdict,
            confidence=confidence,
            fileName=file.filename,
            fileType=file_type,
            analyzedAt=datetime.utcnow(),
            details=ForensicDetails(
                facialAnalysis=base_result["details"]["facialAnalysis"],
                temporalConsistency=base_result["details"]["temporalConsistency"],
                artifactDetection=base_result["details"]["artifactDetection"],
                metadataAnalysis=base_result["details"]["metadataAnalysis"],
            ),
            engine=EngineInfo(
                primary=engine_primary,
                secondary=engine_secondary,
            ),
            explanation=explanation,
        )

    finally:
        # -----------------------------
        # Cleanup temp file
        # -----------------------------
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
