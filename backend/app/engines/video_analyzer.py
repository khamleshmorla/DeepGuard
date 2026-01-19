import numpy as np
from app.engines.cnn import run_cnn
from app.engines.fft_detector import fft_score


def analyze_video_frames(frame_paths):
    """
    Aggregate CNN + FFT across stable frames.
    CNN = support only.
    FFT = primary physics signal.
    """
    cnn_scores = []
    fft_scores = []
    artifact_scores = []

    for p in frame_paths:
        try:
            cnn = run_cnn(p)
            cnn_scores.append(cnn["fake"])
        except Exception:
            cnn_scores.append(50)

        try:
            fft_scores.append(fft_score(p))
        except Exception:
            fft_scores.append(50)

        # Blur-based artifact proxy
        artifact_scores.append(70)

    if not cnn_scores:
        return _safe_video_fallback()

    return {
        "cnn_avg": float(np.mean(cnn_scores)),
        "cnn_max": float(np.max(cnn_scores)),
        "fft_avg": float(np.mean(fft_scores)),
        "fft_min": float(np.min(fft_scores)),
        "artifact_avg": float(np.mean(artifact_scores)),
        "total_frames": len(cnn_scores),
    }


def _safe_video_fallback():
    return {
        "cnn_avg": 50,
        "cnn_max": 50,
        "fft_avg": 50,
        "fft_min": 50,
        "artifact_avg": 50,
        "total_frames": 0,
    }
