import cv2
import numpy as np
from app.engines.fft_detector import fft_score
from app.engines.cnn import run_cnn


def analyze_video_frames(video_path: str, max_frames: int = 15) -> dict:
    """
    Production-grade video forensic analysis.
    CNN is SUPPORT only. FFT is primary.
    """

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames <= 0:
        return _safe_video_fallback()

    step = max(1, total_frames // max_frames)

    cnn_scores = []
    fft_scores = []
    artifact_scores = []

    frame_idx = 0
    processed = 0

    while cap.isOpened() and processed < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % step == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # FFT (PRIMARY SIGNAL)
            fft_val = fft_score(gray)
            fft_scores.append(fft_val)

            # Artifact proxy (blur variance)
            blur = cv2.Laplacian(gray, cv2.CV_64F).var()
            artifact_scores.append(
                85 if blur < 80 else 65
            )

            # CNN SUPPORT ONLY
            try:
                tmp = "/tmp/frame.jpg"
                cv2.imwrite(tmp, frame)
                cnn = run_cnn(tmp)
                cnn_scores.append(cnn["fake"])
            except Exception:
                cnn_scores.append(50)

            processed += 1

        frame_idx += 1

    cap.release()

    return {
        "cnn_avg": float(np.mean(cnn_scores)) if cnn_scores else 50,
        "cnn_max": float(np.max(cnn_scores)) if cnn_scores else 50,
        "fft_avg": float(np.mean(fft_scores)) if fft_scores else 50,
        "fft_min": float(np.min(fft_scores)) if fft_scores else 50,
        "artifact_avg": float(np.mean(artifact_scores)) if artifact_scores else 50,
        "total_frames": processed,
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
