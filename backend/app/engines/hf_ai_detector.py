"""
Hugging Face AI Image Detector Engine (Local Ensemble)
Uses an ensemble of 3 locally-loaded transformer models for FAST and ACCURATE inference.
- Ateeqq/ai-vs-human-image-detector (SigLIP)
- umm-maybe/AI-image-detector (ViT)
- haywoodsloan/ai-image-detector-deploy (Swinv2)

This provides the same 'voting' logic as the API ensemble but runs locally.
Note: Explicitly uses AutoImageProcessor and Mean/Std normalization to match HF API.
"""
import os
import requests
import time
import torch
from PIL import Image
from transformers import AutoImageProcessor

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
        "weight": 0.8
    }
]

# Global cache for pipeline objects and processors
_ensemble_pipelines = {}
_ensemble_processors = {}
_ensemble_loaded = False


def _load_ensemble():
    """Load all 3 models into memory. Called once at startup."""
    global _ensemble_pipelines, _ensemble_processors, _ensemble_loaded

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
            # Pre-load processor for exact normalization match
            _ensemble_processors[m_id] = AutoImageProcessor.from_pretrained(m_id)
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
    Run local ensemble inference with explicit normalization.
    Returns dict with verdict, confidence, model_scores, explanation.
    """
    if not _ensemble_pipelines:
        _load_ensemble()

    try:
        # Debug logging for image quality check
        with Image.open(file_path) as img_check:
            print(f"🖼️ Detector reading: {file_path.split('/')[-1]} | Size: {img_check.size} | Mode: {img_check.mode}")
        raw_img = Image.open(file_path).convert("RGB")
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
            
            # Explicit normalization to match HF API exactly
            processor = _ensemble_processors.get(m_id)
            if not processor:
                processor = AutoImageProcessor.from_pretrained(m_id)
                _ensemble_processors[m_id] = processor

            inputs = processor(images=raw_img, return_tensors="pt")
            model = _ensemble_pipelines[m_id].model
            
            with torch.no_grad():
                outputs = model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
                
                # Map probabilities back to labels using model config
                results = []
                for i, prob in enumerate(probs[0]):
                    results.append({
                        "label": model.config.id2label[i], 
                        "score": float(prob)
                    })

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
    # Weighted average calculation
    weight_sum = sum(c["weight"] for c in MODELS_TO_LOAD if c["id"] in _ensemble_pipelines)
    avg_score = sum(scores) / (weight_sum if weight_sum > 0 else 1)
    max_score = max(scores) if scores else 0

    # Thresholding (FUSION context relies on this being passed back faithfully)
    if avg_score >= 60 or max_score >= 82:
        verdict = "FAKE"
        confidence = int(min(max(avg_score, max_score), 99))
    elif avg_score <= 30:
        verdict = "REAL"
        confidence = int(100 - avg_score)
    else:
        verdict = "UNCERTAIN"
        confidence = 50

    model_summary = ", ".join([f"{d['model']}={d['score']}%" for d in details])
    explanation = f"Local Ensemble ({total_time}s): AI Avg={round(avg_score, 1)}%. Models: {model_summary}"

    return {
        "verdict": verdict,
        "confidence": int(confidence),
        "avg_score": round(avg_score, 1),
        "max_score": round(max_score, 1),
        "model_scores": details,
        "explanation": explanation,
    }
