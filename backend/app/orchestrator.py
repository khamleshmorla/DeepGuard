from app.engines.vision_llm import run_vision_llm
from app.engines.heuristics import image_heuristics, video_heuristics
from app.engines.cnn import run_cnn
from app.engines.fft_detector import fft_score
from app.engines.exif_detector import extract_exif_authenticity

# NEW (VIDEO)
from app.engines.video_frames import extract_video_frames
from app.engines.video_analyzer import analyze_video_frames

import os


def orchestrate_detection(
    file_path: str,
    file_type: str,
    original_path: str
) -> dict:
    """
    DeepGuard forensic orchestration (production-grade).

    IMAGE TRUST HIERARCHY:
    1. EXIF  → provenance
    2. FFT   → physics (GAN artifacts)
    3. CNN   → statistical patterns (support only)
    4. LLM   → semantic reasoning
    5. Heuristics → support

    VIDEO TRUST HIERARCHY:
    1. Watermarks / overlays
    2. Frame-level CNN aggregation
    3. Frame-level FFT aggregation
    """

    # =================================================
    # 🎥 VIDEO PIPELINE (PHASE 4 — REAL ANALYSIS)
    # =================================================
    if file_type == "video":
        frame_paths = extract_video_frames(file_path)
        video_stats = analyze_video_frames(frame_paths)

        # Cleanup extracted frames
        for p in frame_paths:
            if os.path.exists(p):
                os.remove(p)

        print("🎥 VIDEO ANALYSIS:", video_stats)

        # -----------------------------
        # VIDEO DECISION LOGIC
        # -----------------------------
        # Strong fake: visible watermark
        if video_stats["watermark_hits"] > 0:
            verdict = "FAKE"
            confidence = 95

        # Strong fake: CNN screams fake on any frame
        elif video_stats["cnn_max"] >= 80:
            verdict = "FAKE"
            confidence = int(video_stats["cnn_max"])

        # Strong fake: frequency artifacts across frames
        elif video_stats["fft_avg"] >= 65:
            verdict = "FAKE"
            confidence = 90

        # Otherwise uncertain → default REAL with caution
        else:
            verdict = "REAL"
            confidence = 70

        return {
            "verdict": verdict,
            "confidence": confidence,
            "details": {
                "facialAnalysis": int(video_stats["cnn_avg"]),
                "artifactDetection": int(video_stats["artifact_avg"]),
                "temporalConsistency": 60,
                "metadataAnalysis": 0,
            },
            "engine": {
                "primary": "video-cnn+fft+watermark",
                "secondary": "frame-aggregation",
                "video_debug": video_stats,
            }
        }

    # =================================================
    # 🖼️ IMAGE PIPELINE (LOCKED & CALIBRATED)
    # =================================================

    # -------------------------------------------------
    # 1️⃣ Vision LLM
    # -------------------------------------------------
    llm_result = run_vision_llm(file_path, file_type)
    llm = llm_result.get("signals", {
        "facialAnalysis": 50,
        "temporalConsistency": 50,
        "artifactDetection": 50,
        "metadataAnalysis": 50,
    })

    # -------------------------------------------------
    # 2️⃣ Heuristics
    # -------------------------------------------------
    heur = image_heuristics(file_path)

    # -------------------------------------------------
    # 3️⃣ CNN (support signal only)
    # -------------------------------------------------
    cnn = run_cnn(file_path)

    # -------------------------------------------------
    # 4️⃣ FFT
    # -------------------------------------------------
    fft = fft_score(file_path)

    # -------------------------------------------------
    # 5️⃣ EXIF (ORIGINAL FILE ONLY)
    # -------------------------------------------------
    exif = extract_exif_authenticity(original_path)

    # -------------------------------------------------
    # DEBUG LOGS
    # -------------------------------------------------
    print(f"📊 FFT score: {fft:.1f}")
    print(f"🧠 CNN fake: {cnn['fake']:.1f}")
    print(f"📸 EXIF authenticity score: {exif['authenticity_score']}")

    # -------------------------------------------------
    # 6️⃣ Signal Fusion (scores only)
    # -------------------------------------------------
    facial = (
        cnn["face"] * 0.6 +
        llm["facialAnalysis"] * 0.25 +
        heur["facialAnalysis"] * 0.15
    )

    artifact = max(
        cnn["artifact"],
        llm["artifactDetection"],
        heur["artifactDetection"]
    )

    temporal = (
        llm["temporalConsistency"] * 0.6 +
        heur["temporalConsistency"] * 0.4
    )

    metadata = heur["metadataAnalysis"]

    merged = {
        "facialAnalysis": int(round(facial)),
        "artifactDetection": int(round(artifact)),
        "temporalConsistency": int(round(temporal)),
        "metadataAnalysis": int(round(metadata)),
    }

    base_confidence = int(sum(merged.values()) / 4)

    # -------------------------------------------------
    # 7️⃣ FINAL IMAGE DECISION LOGIC (LOCKED)
    # -------------------------------------------------

    # ✅ STRONG REAL — camera originals
    if exif["authenticity_score"] >= 70 and fft < 40:
        verdict = "REAL"
        confidence = max(85, min(base_confidence + 20, 95))

    # ✅ LIKELY REAL — phone photos / exports
    elif exif["authenticity_score"] >= 45 and fft < 35:
        verdict = "REAL"
        confidence = max(80, min(base_confidence + 10, 90))

    # ✅ REAL — screenshots / UI images
    elif fft < 30 and cnn["fake"] < 85:
        verdict = "REAL"
        confidence = max(75, min(base_confidence, 85))

    # ❌ STRONG FAKE — GAN frequency signature
    elif fft >= 80:
        verdict = "FAKE"
        confidence = max(base_confidence, 90)

    # ❌ STRONG FAKE — multi-signal agreement
    elif artifact >= 85 and fft >= 60:
        verdict = "FAKE"
        confidence = max(base_confidence, 85)

    # ⚠️ WEAK FAKE
    elif base_confidence >= 65:
        verdict = "FAKE"
        confidence = base_confidence

    # ✅ DEFAULT REAL
    else:
        verdict = "REAL"
        confidence = base_confidence

    # -------------------------------------------------
    # 8️⃣ FINAL IMAGE RESPONSE
    # -------------------------------------------------
    return {
        "verdict": verdict,
        "confidence": confidence,
        "details": merged,
        "engine": {
            "primary": "cnn+vision-llm+fft+exif",
            "secondary": "heuristics",
            "fft_debug": round(fft, 1),
            "cnn_fake": round(cnn["fake"], 1),
            "exif_debug": exif["authenticity_score"],
        }
    }
