from app.engines.vision_llm import run_vision_llm
from app.engines.heuristics import image_heuristics, video_heuristics
from app.engines.cnn import predict_image_cnn
from app.engines.heuristics import apply_cnn_signal



def orchestrate_detection(file_path: str, file_type: str) -> dict:
    """
    Combines:
    - Vision LLM (primary)
    - Heuristics (support)
    - CNN (optional, currently neutral)

    Returns Lovable-compatible forensic details.
    """

    # 1️⃣ Vision LLM (primary)
    llm_result = run_vision_llm(file_path, file_type)

    # 2️⃣ Heuristics (support)
    if file_type == "image":
        heuristic_details = image_heuristics(file_path)
    else:
        heuristic_details = video_heuristics(file_path)

    # 3️⃣ CNN (optional / stub)
    cnn_score = predict_image_cnn(file_path)
    heuristic_details = apply_cnn_signal(heuristic_details, cnn_score)

    # 4️⃣ Merge signals (Vision LLM dominates)
    merged_details = {
        "facialAnalysis": int(
            (llm_result["signals"]["facialAnalysis"] * 0.7 +
             heuristic_details["facialAnalysis"] * 0.3)
        ),
        "temporalConsistency": int(
            (llm_result["signals"]["temporalConsistency"] * 0.7 +
             heuristic_details["temporalConsistency"] * 0.3)
        ),
        "artifactDetection": int(
            (llm_result["signals"]["artifactDetection"] * 0.7 +
             heuristic_details["artifactDetection"] * 0.3)
        ),
        "metadataAnalysis": int(
            (llm_result["signals"]["metadataAnalysis"] * 0.7 +
             heuristic_details["metadataAnalysis"] * 0.3)
        ),
    }

    final_confidence = int(sum(merged_details.values()) / len(merged_details))
    final_verdict = "FAKE" if final_confidence >= 60 else "REAL"

    return {
        "verdict": final_verdict,
        "confidence": final_confidence,
        "details": merged_details,
        "engine": {
            "primary": "vision-llm",
            "secondary": "cnn-efficientnet"
        }
    }
