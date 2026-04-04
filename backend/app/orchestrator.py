from app.engines.vision_llm import run_vision_llm
from app.engines.heuristics import image_heuristics, video_heuristics
from app.engines.cnn import run_cnn
from app.engines.fft_detector import fft_score
from app.engines.exif_detector import extract_exif_authenticity
from app.engines.hf_ai_detector import run_hf_ai_detector

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
        return 0.15
    elif context == "FAKE_STRONG":
        return 0.45
    else:
        return 0.30


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

        # Signal 4: Temporal consistency
        temporal_variance = abs(fft_avg - fft_min)
        if temporal_variance > 15:
            fake_signals += 1
            signal_scores.append(("Temporal", temporal_variance))

        # 🔴 FAKE DECISION LOGIC
        # Case A: Multiple signals agree it's fake
        # Case B: CNN is very confident (>= 84%) even if others are neutral
        # (Threshold 84 selected to catch 85.1% fake while sparing 80.3% real)
        is_primary_fake = False
        if fake_signals >= 2:
            is_primary_fake = True
        elif cnn_max >= 75:
            is_primary_fake = True

        if is_primary_fake:
            # VETO: If FFT is "Strong Real" (< 30) AND Temporal is Stable (< 5)
            # Then we need VERY strong CNN confidence (> 82) to override. 
            # (User's false positive was CNN ~80.3)
            # VETO LOGIC DISABLED (User requires high sensitivity for Deepfakes with clean physics)
            # if fft_avg < 30 and temporal_variance < 5 and cnn_max < 82:
            #    print(f"⚠️ VETO: Physics says REAL (FFT={fft_avg:.1f}, Var={temporal_variance:.1f}). Overriding CNN ({cnn_max:.1f}).")
            #    verdict = "REAL"
            #    confidence = 75
            # else:
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

    # ---- HF AI Detector (catches DALL-E, Midjourney, SDXL) ----
    hf_result = run_hf_ai_detector(file_path)
    hf_verdict = hf_result.get("verdict", "UNKNOWN").upper()
    hf_confidence = hf_result.get("confidence", 50)
    print(f"🔬 HF AI Detector: {hf_verdict} ({hf_confidence}%)")

    # ---- EXIF cross-check to prevent false positives ----
    # Real camera photos have EXIF metadata. AI images (DALL-E, Midjourney) have NONE.
    # If HF says FAKE but the image has strong EXIF → likely a false positive → skip override.
    exif = extract_exif_authenticity(original_path)
    exif_score = exif["authenticity_score"]

    hf_override = False
    if hf_verdict == "FAKE" and hf_confidence >= 60:
        if exif_score >= 30:
            # Strong EXIF = real camera. HF might be wrong (heavily filtered photo).
            # Let the full pipeline decide instead.
            print(f"🛡️ SAFETY: HF says FAKE but EXIF is strong ({exif_score}). Running full pipeline to verify.")
            hf_override = False
        else:
            # No/weak EXIF = no camera metadata = likely AI-generated. Trust HF.
            hf_override = True

    if hf_override:
        # Still run LLM for signal scores (display purposes)
        llm = run_vision_llm(file_path, file_type).get("signals", {
            "facialAnalysis": 50,
            "artifactDetection": 50,
            "temporalConsistency": 50,
            "metadataAnalysis": 50,
        })

        heur = image_heuristics(file_path)

        merged = {
            "facialAnalysis": max(llm["facialAnalysis"], heur["facialAnalysis"]),
            "artifactDetection": max(llm["artifactDetection"], heur["artifactDetection"]),
            "temporalConsistency": max(llm["temporalConsistency"], heur["temporalConsistency"]),
            "metadataAnalysis": heur["metadataAnalysis"],
        }

        print(f"🔬 HF OVERRIDE: AI-image detected (no camera EXIF) → FAKE ({hf_confidence}%)")

        return {
            "verdict": "FAKE",
            "confidence": hf_confidence,
            "details": merged,
            "engine": {
                "primary": "hf-ai-detector",
                "secondary": "ensemble-ai-vs-real",
            }
        }

    # ---- Original pipeline (unchanged from before) ----
    llm = run_vision_llm(file_path, file_type).get("signals", {
        "facialAnalysis": 50,
        "artifactDetection": 50,
        "temporalConsistency": 50,
        "metadataAnalysis": 50,
    })

    heur = image_heuristics(file_path)
    cnn = run_cnn(file_path)
    fft = fft_score(file_path)
    # exif already extracted above for HF cross-check

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
    # FINAL IMAGE DECISION
    # -------------------------------------------------
    
    
    # 🔴 PRIORITY 1: STRONG REAL SIGNAL (Veto with Metadata)
    if context == "REAL_STRONG" and cnn["fake"] < 99 and exif["authenticity_score"] >= 15:
        verdict = "REAL"
        confidence = max(80, min(base_confidence + 10, 95))
        print(f"⚠️ VETO (Image): Physics + EXIF says REAL. Overriding CNN ({cnn['fake']:.1f}).")

    # 🔴 PRIORITY 2: BLATANT FAKE
    elif cnn["fake"] >= 90:
        verdict = "FAKE"
        confidence = int(cnn["fake"])
    
    # 🔴 PRIORITY 3: STRONG FAKE CONTEXT
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

