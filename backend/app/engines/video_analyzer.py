import numpy as np
from app.engines.cnn import run_cnn
from app.engines.fft_detector import fft_score


import concurrent.futures

def analyze_single_frame(path):
    """Helper to process a single frame in parallel."""
    try:
        cnn_val = run_cnn(path)["fake"]
    except Exception:
        cnn_val = 50
    
    try:
        fft_val = fft_score(path)
    except Exception:
        fft_val = 50
        
    return cnn_val, fft_val, 70  # 70 is artifact proxy

def analyze_video_frames(frame_paths):
    """
    Aggregate CNN + FFT across stable frames.
    Parallel execution for performance.
    """
    cnn_scores = []
    fft_scores = []
    artifact_scores = []

    # Parallelize frame analysis
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(analyze_single_frame, frame_paths))

    for c, f, a in results:
        cnn_scores.append(c)
        fft_scores.append(f)
        artifact_scores.append(a)

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
