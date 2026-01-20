from app.engines.vision_llm import run_vision_llm
from app.engines.heuristics import image_heuristics, video_heuristics
from app.engines.cnn import run_cnn
from app.engines.fft_detector import fft_score
from app.engines.exif_detector import extract_exif_authenticity

# VIDEO
from app.engines.video_frames import extract_video_frames
from app.engines.video_analyzer import analyze_video_frames

import os


# -------------------------------------------------
# 🔐 CONTEXT CLASSIFIER (NON-CNN SIGNALS)
# -------------------------------------------------
def signal_context(fft, exif_score, artifact):
    """
    Decide how strong NON-CNN signals are.
    """
    # STRONG REAL
    if fft < 35 and exif_score >= 50:
        return "REAL_STRONG"
    if fft < 30:
        return "REAL_STRONG"

    # STRONG FAKE
    if fft >= 80:
        return "FAKE_STRONG"
    if artifact >= 85 and fft >= 60:
        return "FAKE_STRONG"

    return "UNCERTAIN"


def cnn_weight(context):
    """
    Dynamic CNN influence.
    """
    if context == "REAL_STRONG":
        return 0.15   # CNN almost ignored
    elif context == "FAKE_STRONG":
        return 0.45   # CNN trusted more
    else:
        return 0.30   # balanced


# =================================================
# 🧠 MAIN ORCHESTRATOR
# =================================================
def orchestrate_detection(file_path: str, file_type: str, original_path: str) -> dict:
    """
    DeepGuard forensic orchestration — PHASE 4.2 (LOCKED)

    CORE RULE:
    ❌ CNN NEVER decides alone
    ✅ Physics (FFT) + Metadata (EXIF) define truth
    """

    # =================================================
    # 🎥 VIDEO PIPELINE (REAL FORENSICS)
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
        artifact_avg = stats["artifact_avg"]

        # -----------------------------
        # VIDEO DECISION (SAFE)
        # -----------------------------

        # 🔴 STRONG FAKE — physics + stats agree
        if fft_avg >= 65 and artifact_avg >= 80 and cnn_max >= 85:
            verdict = "FAKE"
            confidence = 90

        # 🟢 STRONG REAL — clean frequency + stable frames
        elif fft_avg < 40 and abs(fft_avg - fft_min) < 10:
            verdict = "REAL"
            confidence = 80

        # 🟡 UNCERTAIN → SAFE REAL
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
                "primary": "video-forensics-v2",
                "secondary": "fft+temporal",
                "video_debug": stats,
            }
        }

    # =================================================
    # 🖼️ IMAGE PIPELINE (DYNAMIC CNN CONTROL)
    # =================================================

    llm = run_vision_llm(file_path, file_type).get("signals", {
        "facialAnalysis": 50,
        "artifactDetection": 50,
        "temporalConsistency": 50,
        "metadataAnalysis": 50,
    })

    heur = image_heuristics(file_path)
    cnn = run_cnn(file_path)
    fft = fft_score(file_path)
    exif = extract_exif_authenticity(original_path)

    print(
        f"📊 FFT: {fft:.1f} | "
        f"🧠 CNN: {cnn['fake']:.1f} | "
        f"📸 EXIF: {exif['authenticity_score']}"
    )

    # -------------------------------------------------
    # CONTEXT AWARE CNN SCALING
    # -------------------------------------------------
    artifact_raw = max(
        cnn["artifact"],
        llm["artifactDetection"],
        heur["artifactDetection"]
    )

    context = signal_context(
        fft=fft,
        exif_score=exif["authenticity_score"],
        artifact=artifact_raw
    )

    cnn_w = cnn_weight(context)

    # -------------------------------------------------
    # SIGNAL FUSION (CNN IS ADAPTIVE)
    # -------------------------------------------------
    facial = (
        cnn["face"] * cnn_w +
        llm["facialAnalysis"] * 0.35 +
        heur["facialAnalysis"] * (0.65 - cnn_w)
    )

    artifact = max(
        llm["artifactDetection"],
        heur["artifactDetection"],
        cnn["artifact"] * cnn_w
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
    # FINAL IMAGE DECISION (CNN NEVER OVERRIDES)
    # -------------------------------------------------
    
    # ✅ NEW: CNN CONFIDENCE OVERRIDE (when extremely confident)
    if cnn["fake"] >= 90:  # CNN is VERY sure it's fake
        verdict = "FAKE"
        confidence = int(cnn["fake"])
    
    elif context == "REAL_STRONG":
        verdict = "REAL"
        confidence = max(80, min(base_confidence + 10, 90))

    elif context == "FAKE_STRONG":
        verdict = "FAKE"
        confidence = max(base_confidence, 85)

    elif base_confidence >= 70:
        verdict = "FAKE"
        confidence = base_confidence

    else:
        verdict = "REAL"
        confidence = base_confidence

    return {
        "verdict": verdict,
        "confidence": confidence,
        "details": merged,
        "engine": {
            "primary": "image-forensics-v3",
            "secondary": "fft+exif+adaptive-cnn",
            "debug": {
                "context": context,
                "cnn_weight": cnn_w,
                "fft": round(fft, 1),
                "cnn_fake": round(cnn["fake"], 1),
                "exif": exif["authenticity_score"],
            }
        }
    }
