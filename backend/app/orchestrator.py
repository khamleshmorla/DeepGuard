from app.engines.vision_llm import run_vision_llm
from app.engines.heuristics import image_heuristics, video_heuristics
from app.engines.cnn import run_cnn
from app.engines.fft_detector import fft_score
from app.engines.exif_detector import extract_exif_authenticity


def orchestrate_detection(
    file_path: str,
    file_type: str,
    original_path: str
) -> dict:
    """
    DeepGuard forensic orchestration (FFT + EXIF calibrated).
    """

    # -----------------------------
    # 1️⃣ Vision LLM
    # -----------------------------
    llm_result = run_vision_llm(file_path, file_type)
    llm = llm_result.get("signals", {
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
        "face": 50, "texture": 50, "artifact": 50, "fake": 50
    }

    # -----------------------------
    # 4️⃣ FFT
    # -----------------------------
    fft = fft_score(file_path) if file_type == "image" else 50

    # -----------------------------
    # 5️⃣ EXIF (ORIGINAL FILE ONLY)
    # -----------------------------
    exif = extract_exif_authenticity(original_path) if file_type == "image" else {
        "authenticity_score": 0
    }

    print(f"📊 FFT score: {fft:.1f}")
    print(f"🧠 CNN fake: {cnn['fake']:.1f}")
    print(f"📸 EXIF authenticity score: {exif['authenticity_score']}")

    # -----------------------------
    # 6️⃣ Signal Fusion
    # -----------------------------
    facial = cnn["face"] * 0.6 + llm["facialAnalysis"] * 0.25 + heur["facialAnalysis"] * 0.15
    artifact = max(cnn["artifact"], llm["artifactDetection"], heur["artifactDetection"])
    temporal = llm["temporalConsistency"] * 0.6 + heur["temporalConsistency"] * 0.4
    metadata = heur["metadataAnalysis"]

    merged = {
        "facialAnalysis": int(round(facial)),
        "artifactDetection": int(round(artifact)),
        "temporalConsistency": int(round(temporal)),
        "metadataAnalysis": int(round(metadata)),
    }

    confidence = int(sum(merged.values()) / 4)

    # -----------------------------
    # 7️⃣ FINAL CALIBRATION
    # -----------------------------
    if artifact >= 85 or cnn["fake"] >= 85:
        verdict = "FAKE"
        confidence = max(confidence, 85)

    elif exif["authenticity_score"] >= 70 and fft < 40:
        verdict = "REAL"
        confidence = min(confidence + 20, 95)

    elif confidence >= 65:
        verdict = "FAKE"

    else:
        verdict = "REAL"

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
