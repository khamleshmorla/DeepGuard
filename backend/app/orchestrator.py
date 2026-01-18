from app.engines.vision_llm import run_vision_llm
from app.engines.heuristics import image_heuristics, video_heuristics
from app.engines.cnn import run_cnn
from app.engines.fft_detector import fft_score


def orchestrate_detection(file_path: str, file_type: str) -> dict:
    """
    DeepGuard forensic orchestration.

    Combines:
    - Vision LLM (semantic reasoning)
    - CNN (statistical evidence)
    - FFT (frequency-domain, OBSERVATION ONLY)
    - Heuristics (deterministic checks)

    FFT Phase 1:
    - FFT is logged
    - FFT does NOT affect verdict or confidence
    """

    # -----------------------------
    # 1️⃣ Vision LLM (reasoning)
    # -----------------------------
    llm_result = run_vision_llm(file_path, file_type)

    llm_signals = llm_result.get("signals", {
        "facialAnalysis": 50,
        "temporalConsistency": 50,
        "artifactDetection": 50,
        "metadataAnalysis": 50,
    })

    # -----------------------------
    # 2️⃣ Heuristics (support)
    # -----------------------------
    if file_type == "image":
        heur = image_heuristics(file_path)
    else:
        heur = video_heuristics(file_path)

    # -----------------------------
    # 3️⃣ CNN (grounding evidence)
    # -----------------------------
    cnn = None
    if file_type == "image":
        cnn = run_cnn(file_path)

    # CNN fallback (safety)
    if cnn is None:
        cnn = {
            "face": 50,
            "texture": 50,
            "artifact": 50,
            "fake": 50,
        }

    # -----------------------------
    # 4️⃣ FFT (PHASE 1 — LOG ONLY)
    # -----------------------------
    if file_type == "image":
        fft = fft_score(file_path)
    else:
        fft = 50

    print(f"📊 FFT anomaly score: {fft:.1f}")

    # -----------------------------
    # 5️⃣ Signal Fusion (NO FFT YET)
    # -----------------------------
    facial = (
        cnn["face"] * 0.6 +
        llm_signals["facialAnalysis"] * 0.25 +
        heur["facialAnalysis"] * 0.15
    )

    artifact = max(
        cnn["artifact"],
        llm_signals["artifactDetection"],
        heur["artifactDetection"]
    )

    temporal = (
        llm_signals["temporalConsistency"] * 0.6 +
        heur["temporalConsistency"] * 0.4
    )

    metadata = heur["metadataAnalysis"]

    merged_details = {
        "facialAnalysis": int(round(facial)),
        "artifactDetection": int(round(artifact)),
        "temporalConsistency": int(round(temporal)),
        "metadataAnalysis": int(round(metadata)),
    }

    # -----------------------------
    # 6️⃣ Confidence Calculation
    # -----------------------------
    confidence = int(sum(merged_details.values()) / 4)

    # -----------------------------
    # 7️⃣ Calibration (PRE-FFT)
    # -----------------------------
    natural_markers = 0

    if merged_details["facialAnalysis"] < 40:
        natural_markers += 1
    if merged_details["artifactDetection"] < 35:
        natural_markers += 1
    if merged_details["metadataAnalysis"] < 40:
        natural_markers += 1

    # Hard veto (CNN / artifact only)
    if merged_details["artifactDetection"] >= 80 or cnn["fake"] >= 80:
        verdict = "FAKE"
        confidence = max(confidence, 80)

    elif confidence >= 65:
        verdict = "FAKE"

    elif natural_markers >= 2:
        verdict = "REAL"
        confidence = min(confidence + 10, 95)

    else:
        verdict = "REAL"

    # -----------------------------
    # 8️⃣ Final Response
    # -----------------------------
    return {
        "verdict": verdict,
        "confidence": confidence,
        "details": merged_details,
        "engine": {
            "primary": "cnn+vision-llm",
            "secondary": "heuristics",
            "fft_debug": round(fft, 1)   # TEMPORARY (Phase 1 only)
        }
    }
