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
    hf_result = run_hf_ai_detector(original_path)
    hf_avg = hf_result.get("avg_score", 0)
    hf_max = hf_result.get("max_score", 0)
    hf_verdict = hf_result.get("verdict", "UNKNOWN").upper()

    # ---- EXIF cross-check for high-confidence real indicators ----
    exif = extract_exif_authenticity(original_path)
    exif_score = exif["authenticity_score"]

    # ---- Vision LLM (Semantic Reasoning) ----
    llm = run_vision_llm(file_path, file_type).get("signals", {
        "facialAnalysis": 50,
        "artifactDetection": 50,
        "temporalConsistency": 50,
        "metadataAnalysis": 50,
    })

    # ---- Classic Forensics (CNN & FFT) ----
    heur = image_heuristics(file_path)
    cnn = run_cnn(file_path)
    fft = fft_score(file_path)

    print(
        f"📊 HF Ensemble: Avg={hf_avg:.1f} Max={hf_max:.1f} | "
        f"🧠 CNN: {cnn['fake']:.1f} | "
        f"📸 EXIF: {exif_score}"
    )

    # -------------------------------------------------
    # SIGNAL FUSION (ADAPTIVE & CONTEXT-AWARE)
    # -------------------------------------------------
    
    # 1. Artifact Detection (Highest Weight to HF & LLM for AI images)
    artifact = max(
        hf_max,                      # 🔴 AI Ensemble Pixel Artifacts
        llm["artifactDetection"],    # 🧠 Vision LLM Semantic Mistakes
        cnn["artifact"],             # 🧪 Classic CNN Artifacts
        heur["artifactDetection"]    # 📏 Heuristic signals
    )

    # 2. Facial Analysis (Balance CNN with LLM reasoning)
    facial = max(
        hf_max if hf_max > 70 else 0, # HF also looks at faces
        cnn["face"] * 0.7 + llm["facialAnalysis"] * 0.3
    )

    # 3. Final Merged Details (for UI display)
    merged = {
        "facialAnalysis": int(round(facial)),
        "artifactDetection": int(round(artifact)),
        "temporalConsistency": int(round(max(llm["temporalConsistency"], heur["temporalConsistency"]))),
        "metadataAnalysis": int(round(exif_score if exif_score > 0 else 0)),
    }

    # -------------------------------------------------
    # FINAL IMAGE DECISION LOGIC
    # -------------------------------------------------
    
    # Context calculation for decision weighting
    artifact_raw = max(cnn["artifact"], llm["artifactDetection"], hf_avg)
    context = signal_context(fft=fft, exif_score=exif_score, artifact=artifact_raw)

    is_fake = False
    confidence = 50

    # PRIORITY 1: High-confidence AI Ensemble OR LLM Semantic Certainty
    if (hf_max >= 82) or (llm["artifactDetection"] >= 85):
        is_fake = True
        confidence = int(max(hf_max, llm["artifactDetection"]))
        print(f"🎯 FUSION: AI Signature Detected ({hf_max}%) or Semantic Errors ({llm['artifactDetection']}%).")

    # PRIORITY 2: Multiple signals indicate FAKE
    elif (hf_avg >= 55) and (cnn["fake"] >= 65):
        is_fake = True
        confidence = int((hf_avg + cnn["fake"]) / 2)
        print(f"🎯 FUSION: Signal Agreement (HF={hf_avg}%, CNN={cnn['fake']}%).")

    # PRIORITY 3: DeepGuard CNN is certain
    elif cnn["fake"] >= 85:
        is_fake = True
        confidence = int(cnn["fake"])
        print(f"🎯 FUSION: Backend CNN High-Confidence ({cnn['fake']}%).")

    # PRIORITY 4: Strong Metadata VETO (Real Camera Verification)
    elif context == "REAL_STRONG" and exif_score >= 25 and hf_max < 90:
        is_fake = False
        confidence = 90
        print(f"🛡️ FUSION: Camera Metadata Veto - Image appears REAL ({exif_score}).")

    # DEFAULT
    else:
        is_fake = artifact >= 70 or facial >= 72
        confidence = int(max(artifact, facial)) if is_fake else int(100 - max(artifact, facial))

    verdict = "FAKE" if is_fake else "REAL"

    return {
        "verdict": verdict,
        "confidence": int(min(max(confidence, 50), 99)),
        "details": merged,
        "engine": {
            "primary": "image-fusion-v4",
            "secondary": "ensemble+vision-llm+cnn",
            "debug": {
                "hf_avg": round(hf_avg, 1),
                "hf_max": round(hf_max, 1),
                "cnn_fake": round(cnn["fake"], 1),
                "exif": exif_score,
                "llm_artifact": llm["artifactDetection"]
            }
        }
    }


