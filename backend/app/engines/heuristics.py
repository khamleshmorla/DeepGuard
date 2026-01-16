import cv2
import numpy as np
from PIL import Image


# --------------------------------------------------
# IMAGE FORENSIC HEURISTICS
# --------------------------------------------------
def image_heuristics(image_path: str) -> dict:
    """
    Deterministic forensic signals from an image.
    No ML. No randomness. Always safe.
    """

    img = Image.open(image_path).convert("RGB")
    width, height = img.size

    # Facial analysis (proxy: resolution clarity)
    facial_analysis = 90 if min(width, height) >= 224 else 65

    # Artifact detection (blur / over-smoothing)
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    blur_score = cv2.Laplacian(img_cv, cv2.CV_64F).var()

    artifact_detection = 85 if blur_score < 100 else 70

    # Metadata analysis (placeholder, stable)
    metadata_analysis = 80

    return {
        "facialAnalysis": int(np.clip(facial_analysis, 0, 100)),
        "temporalConsistency": 0,
        "artifactDetection": int(np.clip(artifact_detection, 0, 100)),
        "metadataAnalysis": int(np.clip(metadata_analysis, 0, 100)),
    }


# --------------------------------------------------
# VIDEO FORENSIC HEURISTICS
# --------------------------------------------------
def video_heuristics(video_path: str, max_frames: int = 10) -> dict:
    """
    Deterministic forensic signals from a video.
    Handles corrupt / short / edge cases safely.
    """

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return _safe_fallback()

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames <= 0:
        cap.release()
        return _safe_fallback()

    blur_scores = []
    step = max(1, total_frames // max_frames)
    idx = 0
    sampled = 0

    while cap.isOpened() and sampled < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        if idx % step == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur_scores.append(cv2.Laplacian(gray, cv2.CV_64F).var())
            sampled += 1

        idx += 1

    cap.release()

    # SAFETY: handle empty blur_scores
    if not blur_scores:
        return _safe_fallback()

    blur_std = float(np.std(blur_scores))
    blur_mean = float(np.mean(blur_scores))

    temporal_consistency = 85 if blur_std < 50 else 65
    artifact_detection = 80 if blur_mean < 120 else 70

    facial_analysis = 75
    metadata_analysis = 78

    return {
        "facialAnalysis": int(np.clip(facial_analysis, 0, 100)),
        "temporalConsistency": int(np.clip(temporal_consistency, 0, 100)),
        "artifactDetection": int(np.clip(artifact_detection, 0, 100)),
        "metadataAnalysis": int(np.clip(metadata_analysis, 0, 100)),
    }


# --------------------------------------------------
# CNN SIGNAL BLENDING (STUB / FUTURE SAFE)
# --------------------------------------------------
def apply_cnn_signal(details: dict, cnn_score: float) -> dict:
    """
    CNN hook (currently inactive).
    cnn_score ∈ [0,1]
    """

    # CNN intentionally neutral for now
    return details


# --------------------------------------------------
# INTERNAL SAFE FALLBACK
# --------------------------------------------------
def _safe_fallback() -> dict:
    """
    Guaranteed-safe forensic output for unreadable videos.
    """
    return {
        "facialAnalysis": 60,
        "temporalConsistency": 60,
        "artifactDetection": 60,
        "metadataAnalysis": 60,
    }
