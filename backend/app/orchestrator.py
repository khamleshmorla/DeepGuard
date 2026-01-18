from app.engines.vision_llm import run_vision_llm
from app.engines.heuristics import image_heuristics, video_heuristics
from app.engines.cnn import run_cnn
from app.engines.fft_detector import fft_score
from app.engines.exif_detector import extract_exif_authenticity


def orchestrate_detection(file_path: str, file_type: str) -> dict:
    """
    DeepGuard forensic orchestration.

    Active signals:
    - Vision LLM (semantic reasoning)
    - CNN (statistical evidence)
    - FFT (frequency-domain)
    - EXIF (camera authenticity)
    - Heuristics (deterministic checks)

    Current phase:
    - FFT Phase 2 (soft support)
    - EXIF Phase 2.5A (observation only)
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
    heur = (
        image_heuristics(file_path)
        if file_type == "image"
        else video_heuristics(file_path)
    )

    # -----------------------------
    # 3️⃣ CNN
    # -----------------------------
    cnn = (
        run_cnn(file_path)
        if file_type == "image"
        else {
            "face": 50,
            "texture": 50,
            "artifact": 50,
            "fake": 50,
        }
    )

    # -----------------------------
    # 4️⃣ FFT
    # -----------------------------
    fft = fft_score(file_path) if file_type == "image" else 50

    print(f"📊 FFT score: {fft:.1f}")
    print(f"🧠 CNN fake: {cnn['fake']:.1f}")

    # -----------------------------
    # 4.5️⃣ EXIF (AUTHENTICITY SIGNAL)
    # -----------------------------
    if file_type == "image":
        exif = extract_exif_authenticity(file_path)
    else:
        exif = {"authenticity_score": 0}

    print(f"📸 EXIF authenticity score: {exif['authenticity_score']}")

    # -----------------------------
    # 5️⃣ Signal Fusion (NO EXIF YET)
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
    # 6️⃣ Calibration (PRE-temperature scaling)
    # -----------------------------

    # Extreme artifact = fake
    if artifact >= 85:
        verdict = "FAKE"
        confidence = max(confidence, 90)

    # FFT supports REAL (soft)
    elif fft < 45 and cnn["fake"] < 80:
        verdict = "REAL"
        confidence = min(confidence + 15, 95)

    # CNN + LLM agreement
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
            "primary": "cnn+vision-llm+fft+exif",
            "secondary": "heuristics",
            "fft_debug": round(fft, 1),
            "cnn_fake": round(cnn["fake"], 1),
            "exif_debug": exif["authenticity_score"],
        }
    }
