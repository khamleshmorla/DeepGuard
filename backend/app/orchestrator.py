from app.engines.vision_llm import run_vision_llm
from app.engines.heuristics import image_heuristics, video_heuristics
from app.engines.cnn import run_cnn
from app.engines.fft_detector import fft_score
from app.engines.exif_detector import extract_exif_authenticity

# VIDEO
from app.engines.video_frames import extract_video_frames
from app.engines.video_analyzer import analyze_video_frames

import os


def orchestrate_detection(file_path: str, file_type: str, original_path: str) -> dict:
    """
    DeepGuard forensic orchestration — PHASE 4.2 (LOCKED)

    CORE PRINCIPLE:
    ❌ CNN NEVER decides alone
    ✅ Physics (FFT) > Metadata (EXIF) > Temporal stability
    """

    # =================================================
    # 🎥 VIDEO PIPELINE
    # =================================================
    if file_type == "video":
        frame_paths = extract_video_frames(file_path)
        stats = analyze_video_frames(frame_paths)

        for p in frame_paths:
            if os.path.exists(p):
                os.remove(p)

        print("🎥 VIDEO ANALYSIS:", stats)

        fft_avg = stats["fft_avg"]
        fft_min = stats["fft_min"]
        cnn_avg = stats["cnn_avg"]
        cnn_max = stats["cnn_max"]

        # -----------------------------
        # VIDEO DECISION (SAFE)
        # -----------------------------

        # STRONG FAKE — physics + stats agree
        if fft_avg >= 65 and cnn_max >= 85:
            verdict = "FAKE"
            confidence = 90

        # STRONG REAL — clean frequency & stable
        elif fft_avg < 40 and abs(fft_avg - fft_min) < 10:
            verdict = "REAL"
            confidence = 80

        # UNCERTAIN → SAFE REAL
        else:
            verdict = "REAL"
            confidence = 60

        return {
            "verdict": verdict,
            "confidence": confidence,
            "details": {
                "facialAnalysis": int(cnn_avg),
                "artifactDetection": int(stats["artifact_avg"]),
                "temporalConsistency": int(100 - abs(fft_avg - fft_min)),
                "metadataAnalysis": 0,
            },
            "engine": {
                "primary": "video-forensics-v2",
                "secondary": "cnn+fft",
                "video_debug": stats,
            }
        }

    # =================================================
    # 🖼️ IMAGE PIPELINE (STABLE)
    # =================================================

    llm = run_vision_llm(file_path, file_type).get("signals", {})
    heur = image_heuristics(file_path)
    cnn = run_cnn(file_path)
    fft = fft_score(file_path)
    exif = extract_exif_authenticity(original_path)

    print(f"📊 FFT: {fft:.1f} | 🧠 CNN: {cnn['fake']:.1f} | 📸 EXIF: {exif['authenticity_score']}")

    facial = cnn["face"] * 0.6 + llm.get("facialAnalysis", 50) * 0.25 + heur["facialAnalysis"] * 0.15
    artifact = max(cnn["artifact"], llm.get("artifactDetection", 50), heur["artifactDetection"])
    temporal = llm.get("temporalConsistency", 50)
    metadata = heur["metadataAnalysis"]

    merged = {
        "facialAnalysis": int(facial),
        "artifactDetection": int(artifact),
        "temporalConsistency": int(temporal),
        "metadataAnalysis": int(metadata),
    }

    base_conf = sum(merged.values()) // 4

    # IMAGE DECISION
    if exif["authenticity_score"] >= 60 and fft < 40:
        verdict = "REAL"
        confidence = max(85, base_conf)
    elif fft >= 80:
        verdict = "FAKE"
        confidence = 90
    elif base_conf >= 65:
        verdict = "FAKE"
        confidence = base_conf
    else:
        verdict = "REAL"
        confidence = base_conf

    return {
        "verdict": verdict,
        "confidence": confidence,
        "details": merged,
        "engine": {
            "primary": "image-forensics-v2",
            "secondary": "cnn+fft+exif",
        }
    }
