from app.engines.vision_llm import run_vision_llm
from app.engines.heuristics import image_heuristics, video_heuristics
from app.engines.cnn import run_cnn
from app.engines.fft_detector import fft_score
from app.engines.exif_detector import extract_exif_authenticity

# VIDEO
from app.engines.video_analyzer import analyze_video_frames

import os


def orchestrate_detection(
    file_path: str,
    file_type: str,
    original_path: str
) -> dict:
    """
    DeepGuard forensic orchestration (PRODUCTION-GRADE)

    IMAGE TRUST HIERARCHY:
    1. EXIF  → provenance (camera truth)
    2. FFT   → physics-based GAN artifacts
    3. CNN   → statistical patterns (SUPPORT ONLY)
    4. Vision LLM → semantic reasoning
    5. Heuristics → support only

    VIDEO TRUST HIERARCHY:
    1. Temporal consistency + physics (FFT)
    2. Frame aggregation (CNN SUPPORT)
    3. Watermark presence (WEAK signal)
    """

    # =================================================
    # 🎥 VIDEO PIPELINE (PHASE 4 — REAL VIDEO ANALYSIS)
    # =================================================
    if file_type == "video":

        video_stats = analyze_video_frames(file_path)

        print("🎥 VIDEO ANALYSIS:", video_stats)

        fft_avg = video_stats["fft_avg"]
        fft_min = video_stats["fft_min"]
        cnn_avg = video_stats["cnn_avg"]
        cnn_max = video_stats["cnn_max"]
        artifact_avg = video_stats["artifact_avg"]
        watermark_hits = video_stats.get("watermark_hits", 0)

        # -----------------------------
        # VIDEO DECISION (SAFE LOGIC)
        # -----------------------------

        # 🔴 STRONG FAKE — multiple agreeing signals
        if (
            fft_avg >= 65 and
            artifact_avg >= 75 and
            cnn_max >= 85
        ):
            verdict = "FAKE"
            confidence = 90

        # 🟡 UNCERTAIN (mapped to REAL for UI safety)
        elif fft_avg < 40:
            verdict = "REAL"
            confidence = 60

        # 🟡 UNCERTAIN — watermark alone is NOT proof
        elif watermark_hits > 5 and cnn_avg < 80:
            verdict = "REAL"
            confidence = 65

        # 🔴 LIKELY FAKE — CNN very high + artifacts
        elif cnn_avg >= 85 and artifact_avg >= 80:
            verdict = "FAKE"
            confidence = 85

        # 🟢 DEFAULT SAFE
        else:
            verdict = "REAL"
            confidence = 60

        return {
            "verdict": verdict,
            "confidence": confidence,
            "details": {
                "facialAnalysis": int(cnn_avg),
                "artifactDetection": int(artifact_avg),
                "temporalConsistency": int(100 - abs(fft_avg - fft_min)),
                "metadataAnalysis": 0,
            },
            "engine": {
                "primary": "video-forensics",
                "secondary": "fft+temporal",
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
    # 3️⃣ CNN (SUPPORT ONLY)
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
    # 6️⃣ SIGNAL FUSION (NO VERDICT YET)
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
    # 7️⃣ FINAL IMAGE DECISION (CORRECT & SAFE)
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
