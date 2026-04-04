"""
Hugging Face AI Image Detector Engine (Local Ensemble)
Uses an ensemble of 3 locally-loaded transformer models for FAST and ACCURATE inference.
- Ateeqq/ai-vs-human-image-detector (SigLIP)
- umm-maybe/AI-image-detector (ViT)
- haywoodsloan/ai-image-detector-deploy (Swinv2)

This provides the same 'voting' logic as the API ensemble but runs in ~1-2 seconds.
"""
import os
import requests
import time
from PIL import Image

# ================================================================
# ENSEMBLE CONFIGURATION
# ================================================================
MODELS_TO_LOAD = [
    {
        "id": "Ateeqq/ai-vs-human-image-detector",
        "fake_label": "ai",
        "real_label": "hum",
        "weight": 1.0
    },
    {
        "id": "haywoodsloan/ai-image-detector-deploy",
        "fake_label": "artificial",
        "real_label": "real",
        "weight": 1.0
    },
    {
        "id": "umm-maybe/AI-image-detector",
        "fake_label": "artificial",
        "real_label": "human",
        "weight": 0.8  # Slight lower weight for umm-maybe as it can be jumpy
    }
]

# Global cache for pipeline objects
_ensemble_pipelines = {}
_ensemble_loaded = False


def _load_ensemble():
    """Load all 3 models into memory. Called once at startup."""
    global _ensemble_pipelines, _ensemble_loaded

    if _ensemble_loaded:
        return True

    from transformers import pipeline
    print("🛡️ Loading DeepGuard AI Ensemble (3 Models)...")
    
    for cfg in MODELS_TO_LOAD:
        m_id = cfg["id"]
        try:
            print(f"  → Loading {m_id.split('/')[-1]}...")
            start = time.time()
            _ensemble_pipelines[m_id] = pipeline(
                "image-classification",
                model=m_id,
                device=-1  # CPU
            )
            print(f"    ✅ Done ({round(time.time() - start, 1)}s)")
        except Exception as e:
            print(f"    ❌ Failed to load {m_id}: {e}")

    _ensemble_loaded = True
    return len(_ensemble_pipelines) > 0


def _extract_score(results, fake_label, real_label):
    """Extract probability from model results."""
    fake_score = None
    real_score = None

    for item in results:
        label = item.get("label", "").lower().strip()
        score = item.get("score", 0) * 100
        if fake_label.lower() in label:
            fake_score = score
        elif real_label.lower() in label:
            real_score = score

    if fake_score is not None:
        return fake_score
    if real_score is not None:
        return 100 - real_score
    return 50  # Neutral fallback


# ================================================================
# MAIN ENTRY POINT
# ================================================================

# Eagerly try to load local ensemble at import time
try:
    _load_ensemble()
except Exception as e:
    print(f"⚠️ Ensemble eager load failed (might be build time): {e}")


def run_hf_ai_detector(file_path):
    """
    Run local ensemble inference.
    Returns dict with verdict, confidence, model_scores, explanation.
    """
    if not _ensemble_pipelines:
        # Emergency attempt if not loaded
        _load_ensemble()

    try:
        img = Image.open(file_path).convert("RGB")
    except Exception as e:
        return {"verdict": "UNKNOWN", "confidence": 50, "explanation": f"Read error: {e}"}

    scores = []
    details = []
    start_total = time.time()

    for cfg in MODELS_TO_LOAD:
        m_id = cfg["id"]
        if m_id not in _ensemble_pipelines:
            continue

        try:
            start_m = time.time()
            results = _ensemble_pipelines[m_id](img)
            score = _extract_score(results, cfg["fake_label"], cfg["real_label"])
            elapsed = round(time.time() - start_m, 2)
            
            scores.append(score * cfg["weight"])
            details.append({
                "model": m_id.split("/")[-1],
                "score": round(score, 1),
                "time": elapsed
            })
            print(f"Ensemble [{m_id.split('/')[-1]}]: AI={round(score, 1)}% ({elapsed}s)")
        except Exception as e:
            print(f"Model {m_id} inference error: {e}")

    if not scores:
        return {
            "verdict": "UNKNOWN",
            "confidence": 50,
            "explanation": "Local ensemble failed to provide signal."
        }

    total_time = round(time.time() - start_total, 2)
    avg_score = sum(scores) / sum(c["weight"] for c in MODELS_TO_LOAD if c["id"] in _ensemble_pipelines)
    max_score = max(scores)

    # Thresholding
    if avg_score >= 60 or max_score >= 85:
        verdict = "FAKE"
        confidence = int(min(max(avg_score, max_score), 99))
    elif avg_score <= 35:
        verdict = "REAL"
        confidence = int(100 - avg_score)
    else:
        verdict = "UNCERTAIN"
        confidence = 50

    model_summary = ", ".join([f"{d['model']}={d['score']}%" for d in details])
    explanation = f"Local Ensemble ({total_time}s): AI Avg={round(avg_score, 1)}%. Models: {model_summary}"

    return {
        "verdict": verdict,
        "confidence": confidence,
        "model_scores": details,
        "explanation": explanation,
    }
