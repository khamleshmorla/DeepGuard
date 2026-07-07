"""
Hugging Face Deepfake Video Frame Detector Engine
Uses local `dima806/deepfake_vs_real_image_detection` ViT model.

PURPOSE: Dedicated to VIDEO frame analysis ONLY.
         This model is NOT used for standalone image uploads.
         It is lazily loaded into RAM only when the first video is uploaded.

ARCHITECTURE: Thread-safe singleton pattern (same as hf_ai_detector.py).
"""
import threading
from PIL import Image

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Dedicated video deepfake model
VIDEO_MODEL_NAME = "dima806/deepfake_vs_real_image_detection"
VIDEO_FAKE_LABEL = "fake"
VIDEO_REAL_LABEL = "real"

# Thread-safe singleton cache
_video_pipeline = None
_video_pipeline_lock = threading.Lock()


def _get_video_pipeline():
    """Lazily load the video deepfake model into RAM on first video upload."""
    global _video_pipeline

    if _video_pipeline is not None:
        return _video_pipeline

    with _video_pipeline_lock:
        # Double-check inside lock
        if _video_pipeline is not None:
            return _video_pipeline

        if not TRANSFORMERS_AVAILABLE:
            print("❌ HF Video Detector: transformers library not installed.")
            return None

        try:
            print(f"📥 Loading dedicated video deepfake model: {VIDEO_MODEL_NAME}...")
            _video_pipeline = pipeline("image-classification", model=VIDEO_MODEL_NAME)
            print(f"✅ Loaded {VIDEO_MODEL_NAME} successfully.")
        except Exception as e:
            print(f"❌ Failed to load video model {VIDEO_MODEL_NAME}: {e}")
            _video_pipeline = None

    return _video_pipeline


def classify_video_frame(frame_path: str) -> float:
    """
    Classify a single extracted video frame as FAKE or REAL.

    Args:
        frame_path: Absolute path to a single extracted video frame image.

    Returns:
        Float 0-100 representing the FAKE probability percentage.
        Returns 50.0 (uncertain) if the model fails or is unavailable.
    """
    pipe = _get_video_pipeline()
    if pipe is None:
        return 50.0

    try:
        image = Image.open(frame_path).convert("RGB")
        results = pipe(image)

        if not results or not isinstance(results, list):
            return 50.0

        fake_score = None
        real_score = None

        for item in results:
            label = item.get("label", "").lower().strip()
            score = item.get("score", 0)

            if VIDEO_FAKE_LABEL in label:
                fake_score = score * 100
            elif VIDEO_REAL_LABEL in label:
                real_score = score * 100

        if fake_score is not None:
            return fake_score
        if real_score is not None:
            return 100.0 - real_score

        return 50.0

    except Exception as e:
        print(f"⚠️ HF Video frame classification failed: {e}")
        return 50.0
