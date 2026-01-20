from app.engines.vision_llm import run_vision_llm
from app.engines.heuristics import image_heuristics, video_heuristics
from app.engines.cnn import run_cnn
from app.engines.fft_detector import fft_score
from app.engines.exif_detector import extract_exif_authenticity

# VIDEO
from app.engines.video_frames import extract_video_frames
from app.engines.video_analyzer import analyze_video_frames


# -------------------------------------------------
# 🔧 CNN CALIBRATION ENGINE
# -------------------------------------------------
def calibrate_cnn_score(cnn_fake: float, fft: float, exif_score: int) -> float:
    """
    Adjust CNN fake score based on physics (FFT) and metadata (EXIF).
    Prevents CNN from overconfidently flagging real photos.
    """
    calibrated = cnn_fake
    
    # Rule 1: FFT says REAL, but CNN says FAKE → reduce CNN
    if fft < 40 and cnn_fake > 85:
        # Strong physics signal contradicts CNN
        reduction_factor = 0.70  # Reduce by 30%
        calibrated = cnn_fake * reduction_factor
        print(f"⚠️  CNN Calibration: FFT real signal detected. {cnn_fake:.1f} → {calibrated:.1f}")
    
    # Rule 2: FFT says REAL + EXIF has metadata → even more reduction
    elif fft < 35 and exif_score >= 30 and cnn_fake > 80:
        reduction_factor = 0.65  # Reduce by 35%
        calibrated = cnn_fake * reduction_factor
        print(f"⚠️  CNN Calibration: Real camera signals (FFT + EXIF). {cnn_fake:.1f} → {calibrated:.1f}")
    
    # Rule 3: Very low FFT (natural compression) + moderate EXIF
    elif fft < 30 and exif_score >= 20 and cnn_fake > 75:
        reduction_factor = 0.60  # Reduce by 40%
        calibrated = cnn_fake * reduction_factor
        print(f"⚠️  CNN Calibration: Strong real camera pattern. {cnn_fake:.1f} → {calibrated:.1f}")
    
    # Rule 4: FFT shows FAKE pattern, support CNN
    elif fft >= 70 and cnn_fake > 75:
        # FFT and CNN agree → boost CNN confidence slightly
        boost_factor = 1.05  # Boost by 5%
        calibrated = min(cnn_fake * boost_factor, 98)
        print(f"✅ CNN Calibration: FFT fake signal confirms CNN. {cnn_fake:.1f} → {calibrated:.1f}")
    
    return calibrated


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
    Dynamic CNN influence - REDUCED for unreliable CNN
    """
    if context == "REAL_STRONG":
        return 0.10   # Reduced from 0.15 (trust physics more)
    elif context == "FAKE_STRONG":
        return 0.35   # Reduced from 0.45 (less reliant on CNN)
    else:
        return 0.20   # Reduced from 0.30 (more balanced toward FFT/EXIF)


# =================================================
# 🧠 MAIN ORCHESTRATOR
# =================================================
def orchestrate_detection(file_path: str, file_type: str, original_path: str) -> dict:
    """
    DeepGuard forensic orchestration — PHASE 4.3 (CNN CALIBRATED)

    CORE RULE:
    ❌ CNN NEVER decides alone
    ✅ Physics (FFT) + Metadata (EXIF) define truth
    ✅ CNN calibrated against physics signals
    """

    # =================================================
    # 🎥 VIDEO PIPELINE (REAL FORENSICS)
    # =================================================
    if file_type == "video":

        frame_paths = extract_video_frames(file_path)
        stats = analyze_video_frames(frame_paths)

        for p in frame_paths:
            pass

        print("🎥 VIDEO ANALYSIS:", stats)

        fft_avg = stats["fft_avg"]
        fft_min = stats["fft_min"]
        cnn_avg = stats["cnn_avg"]
        cnn_max = stats["cnn_max"]
        artifact_avg = stats["artifact_avg"]

        # -----------------------------
        # VIDEO DECISION (MULTI-SIGNAL VOTING)
        # -----------------------------

        # Count how many signals indicate FAKE
        fake_signals = 0
        signal_scores = []

        # Signal 1: CNN confidence
        if cnn_max >= 75:
            fake_signals += 1
            signal_scores.append(("CNN", cnn_max))

        # Signal 2: Artifact detection
        if artifact_avg >= 70:
            fake_signals += 1
            signal_scores.append(("Artifact", artifact_avg))

        # Signal 3: FFT anomaly
        if fft_avg >= 65:
            fake_signals += 1
            signal_scores.append(("FFT", fft_avg))

        # Signal 4: Temporal consistency (check if frames vary too much)
        temporal_variance = abs(fft_avg - fft_min)
        if temporal_variance > 15:
            fake_signals += 1
            signal_scores.append(("Temporal", temporal_variance))

        # 🔴 STRONG FAKE — 2+ signals agree it's fake
        if fake_signals >= 2:
            # Calculate confidence from detected signals
            avg_fake_score = sum([s[1] for s in signal_scores]) / len(signal_scores)
            verdict = "FAKE"
            confidence = int(min(avg_fake_score, 95))

        # 🟢 STRONG REAL — clean frequency + stable frames + low CNN
        elif fft_avg < 35 and cnn_max < 70 and abs(fft_avg - fft_min) < 8:
            verdict = "REAL"
            confidence = 85

        # 🟡 UNCERTAIN → conservative (lean REAL but lower confidence)
        else:
            verdict = "REAL"
            confidence = 65

        return {
            "verdict": verdict,
            "confidence": confidence,
            "details": {
                "facialAnalysis": int(cnn_avg),
                "artifactDetection": int(artifact_avg),
                "temporalConsistency": int(100 - min(abs(fft_avg - fft_min), 100)),
                "metadataAnalysis": 0,
            },
            "engine": {
                "primary": "video-forensics-v2",
                "secondary": "fft+temporal+multi-signal-voting",
                "video_debug": {
                    **stats,
                    "fake_signal_count": fake_signals,
                    "detected_signals": [f"{s[0]}:{int(s[1])}" for s in signal_scores],
                }
            }
        }


    # =================================================
    # 🖼️ IMAGE PIPELINE (CALIBRATED CNN)
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

    # 🔧 CNN CALIBRATION: Apply physics-based adjustment
    cnn["fake"] = calibrate_cnn_score(
        cnn_fake=cnn["fake"],
        fft=fft,
        exif_score=exif["authenticity_score"]
    )

    print(
        f"📊 FFT: {fft:.1f} | "
        f"🧠 CNN: {cnn['fake']:.1f} (calibrated) | "
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
    # FINAL IMAGE DECISION (CALIBRATED CNN)
    # -------------------------------------------------
    
    # ✅ SMART CNN OVERRIDE: CNN is confident AND other signals agree
    if cnn["fake"] >= 90:
        # Only override if:
        # 1. CNN is VERY confident (>=90) AND
        # 2. At least ONE of these is true:
        #    - High artifact score (CNN + artifacts agree)
        #    - FFT shows clear fake pattern (>=70)
        #    - Low EXIF (missing real camera metadata)
        
        has_artifact_agreement = artifact_raw >= 75
        has_fft_fake_pattern = fft >= 70
        has_low_exif = exif["authenticity_score"] <= 20
        
        if has_artifact_agreement or has_fft_fake_pattern or has_low_exif:
            verdict = "FAKE"
            confidence = int(cnn["fake"])
        else:
            # CNN is high but other signals don't support it → trust context
            if context == "REAL_STRONG":
                verdict = "REAL"
                confidence = 75
            elif context == "FAKE_STRONG":
                verdict = "FAKE"
                confidence = max(base_confidence, 80)
            else:
                verdict = "REAL"
                confidence = base_confidence
    
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
            "secondary": "fft+exif+calibrated-cnn",
            "debug": {
                "context": context,
                "cnn_weight": cnn_w,
                "fft": round(fft, 1),
                "cnn_fake_calibrated": round(cnn["fake"], 1),
                "exif": exif["authenticity_score"],
                "cnn_override_applied": cnn["fake"] >= 90,
            }
        }
    }
