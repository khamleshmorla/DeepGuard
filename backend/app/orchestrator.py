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
    DeepGuard forensic orchestration (production-grade).

    Signal trust hierarchy:
    1. EXIF  → provenance (highest trust for REAL)
    2. FFT   → physics-based GAN artifacts
    3. CNN   → statistical patterns (support only, no hard veto)
    4. Vision LLM → semantic reasoning
    5. Heuristics → support only
    """

    # -------------------------------------------------
    # 1️⃣ Vision LLM (semantic reasoning)
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
    heur = (
        image_heuristics(file_path)
        if file_type == "image"
        else video_heuristics(file_path)
    )

    # -------------------------------------------------
    # 3️⃣ CNN (support signal only)
    # -------------------------------------------------
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

    # -------------------------------------------------
    # 4️⃣ FFT (frequency-domain analysis)
    # -------------------------------------------------
    fft = fft_score(file_path) if file_type == "image" else 50

    # -------------------------------------------------
    # 5️⃣ EXIF (ORIGINAL FILE ONLY)
    # -------------------------------------------------
    exif = (
        extract_exif_authenticity(original_path)
        if file_type == "image"
        else {"authenticity_score": 0}
    )

    # -------------------------------------------------
    # DEBUG LOGS (keep during calibration phase)
    # -------------------------------------------------
    print(f"📊 FFT score: {fft:.1f}")
    print(f"🧠 CNN fake: {cnn['fake']:.1f}")
    print(f"📸 EXIF authenticity score: {exif['authenticity_score']}")

    # -------------------------------------------------
    # 6️⃣ Signal Fusion (scores only — no verdict yet)
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
    # 7️⃣ FINAL DECISION LOGIC (CORRECT & CALIBRATED)
    # -------------------------------------------------

    # ✅ STRONG REAL (camera original, full EXIF)
    if exif["authenticity_score"] >= 70 and fft < 40:
        verdict = "REAL"
        confidence = max(85, min(base_confidence + 20, 95))

    # ✅ LIKELY REAL (phone photos / exported images)
    elif exif["authenticity_score"] >= 45 and fft < 35:
        verdict = "REAL"
        confidence = max(80, min(base_confidence + 10, 90))

    # ❌ STRONG FAKE (GAN frequency signature)
    elif fft >= 80:
        verdict = "FAKE"
        confidence = max(base_confidence, 90)

    # ❌ STRONG FAKE (multi-signal agreement)
    elif artifact >= 85 and fft >= 60:
        verdict = "FAKE"
        confidence = max(base_confidence, 85)

    # ⚠️ WEAK FAKE (no REAL indicators present)
    elif base_confidence >= 65:
        verdict = "FAKE"
        confidence = base_confidence

    # ✅ DEFAULT REAL
    else:
        verdict = "REAL"
        confidence = base_confidence

    # -------------------------------------------------
    # 8️⃣ FINAL RESPONSE
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
