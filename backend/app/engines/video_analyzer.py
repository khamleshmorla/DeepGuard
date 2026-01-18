from app.engines.cnn import run_cnn
from app.engines.fft_detector import fft_score
from app.engines.heuristics import image_heuristics
from app.engines.watermark_detector import detect_watermark


def analyze_video_frames(frame_paths):
    """
    Analyze frames and aggregate signals.
    """

    cnn_scores = []
    fft_scores = []
    artifact_scores = []
    watermark_hits = 0

    for path in frame_paths:
        cnn = run_cnn(path)
        fft = fft_score(path)
        heur = image_heuristics(path)

        cnn_scores.append(cnn["fake"])
        fft_scores.append(fft)
        artifact_scores.append(heur["artifactDetection"])

        if detect_watermark(path):
            watermark_hits += 1

    return {
        "cnn_avg": sum(cnn_scores) / len(cnn_scores),
        "cnn_max": max(cnn_scores),
        "fft_avg": sum(fft_scores) / len(fft_scores),
        "fft_min": min(fft_scores),
        "artifact_avg": sum(artifact_scores) / len(artifact_scores),
        "watermark_hits": watermark_hits,
        "total_frames": len(frame_paths),
    }
