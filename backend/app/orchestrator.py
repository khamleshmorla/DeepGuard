from app.engines.vision_llm import run_vision_llm
from app.engines.heuristics import image_heuristics, video_heuristics
from app.engines.cnn import run_cnn
from app.engines.fft_detector import fft_score


def orchestrate_detection(file_path: str, file_type: str) -> dict:
    """
    DeepGuard forensic orchestration (FFT Phase 2).

    FFT is now used as a REAL-support signal,
    not a hard FAKE veto yet.
    """

    # -----------------------------
    # 1️⃣ Vision LLM
    # -----------------------------
    llm_result = run_vision_llm(file_path, file_type)
    llm_signals = llm_result.get("signals", {
        "facialAnalysis": 50,
        "temporalConsistency": 50,
        "artifactDetection": 50,
        "metadataAnalysis": 50,
    })

    # -----------------------------
    # 2️⃣ Heuristics
    # -----------------------------
    heur = image_heuristics(file_path) if file_type == "image" else video_heuristics(file_path)

    # -----------------------------
    # 3️⃣ CNN
    # -----------------------------
    cnn = run_cnn(file_path) if file_type == "image" else {
        "face": 50,
        "texture": 50,
        "artifact": 50,
        "fake": 50,
    }

    # -----------------------------
    # 4️⃣ FFT
    # -----------------------------
    fft = fft_score(file_path) if file_type == "image" else 50

    # EXPLICIT LOGGING
    print(f"📊 FFT score: {fft:.1f}")
    print(f"🧠 CNN fake: {cnn['fake']:.1f}")

    # -----------------------------
    # 5️⃣ Signal Fusion
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

    confidence = int(sum(merged_details.values()) / 4)

    # -----------------------------
    # 6️⃣ FFT-AWARE CALIBRATION (PHASE 2)
    # -----------------------------

    # Hard fake if artifacts are extreme
    if artifact >= 85 or cnn["fake"] >= 85:
        verdict = "FAKE"
        confidence = max(confidence, 85)

    # FFT supports REAL (camera photos)
    elif fft < 45 and cnn["fake"] < 75:
        verdict = "REAL"
        confidence = min(confidence + 15, 95)

    # Normal fake decision
    elif confidence >= 65:
        verdict = "FAKE"

    else:
        verdict = "REAL"

    # -----------------------------
    # 7️⃣ Final Response
    # -----------------------------
    return {
        "verdict": verdict,
        "confidence": confidence,
        "details": merged_details,
        "engine": {
            "primary": "cnn+vision-llm+fft",
            "secondary": "heuristics",
            "fft_debug": round(fft, 1),
            "cnn_fake": round(cnn["fake"], 1)
        }
    }
