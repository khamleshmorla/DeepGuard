"""
Hugging Face AI Image Detector Engine
Uses local Hugging Face image classification pipelines.
These models are specifically trained to detect DALL-E 3, Midjourney, Stable Diffusion, etc.

IMPORTANT: This implementation executes models locally in RAM to prevent latency and timeout issues
previously experienced with the HF Inference API.
"""
import os
import threading
from PIL import Image

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


# Multiple models for ensemble voting
HF_MODELS = [
    {
        "name": "umm-maybe/AI-image-detector",
        "fake_label": "artificial",
        "real_label": "human",
    },
    {
        "name": "Ateeqq/ai-vs-human-image-detector",
        "fake_label": "ai",
        "real_label": "hum",
    },
    {
        "name": "haywoodsloan/ai-image-detector-deploy",
        "fake_label": "artificial",
        "real_label": "real",
    },
]

# Thread-safe pipeline cache
_pipelines = {}
_pipeline_lock = threading.Lock()

def _get_pipeline(model_name):
    """Lazily initialize and cache the HF pipeline to prevent reloading memory per request."""
    global _pipelines
    if model_name in _pipelines:
        return _pipelines[model_name]
        
    with _pipeline_lock:
        # Double check inside lock
        if model_name not in _pipelines:
            print(f"📥 Loading local HF model into memory: {model_name}...")
            try:
                # pipeline downloads model if not present locally, then loads to RAM
                pipe = pipeline("image-classification", model=model_name)
                _pipelines[model_name] = pipe
                print(f"✅ Loaded {model_name} successfully.")
            except Exception as e:
                print(f"❌ Failed to load {model_name}: {e}")
                _pipelines[model_name] = None
                
    return _pipelines[model_name]


def _query_local_model(model_name, image):
    """Run local image classification pipeline and return classification results."""
    pipe = _get_pipeline(model_name)
    if pipe is None:
        return None
        
    try:
        results = pipe(image)
        return results
    except Exception as e:
        print(f"HF local model {model_name} failed inference: {e}")
        return None


def _extract_fake_score(results, fake_label, real_label):
    """Extract the 'fake/AI' probability from local HF classification output."""
    if not results or not isinstance(results, list):
        return None

    fake_score = None
    real_score = None

    for item in results:
        label = item.get("label", "").lower().strip()
        score = item.get("score", 0)

        if fake_label.lower() in label:
            fake_score = score * 100
        elif real_label.lower() in label:
            real_score = score * 100

    if fake_score is not None:
        return fake_score
    if real_score is not None:
        return 100 - real_score

    return None


def run_hf_ai_detector(file_path):
    """
    Run ensemble of Hugging Face AI-image-detector models LOCALLY.
    Returns dict with verdict, confidence, model_scores, explanation.
    """
    if not TRANSFORMERS_AVAILABLE:
        return {
            "verdict": "UNKNOWN",
            "confidence": 50,
            "model_scores": [],
            "explanation": "Transformers library not installed. Cannot run local models."
        }

    try:
        image = Image.open(file_path).convert("RGB")
    except Exception as e:
        return {
            "verdict": "UNKNOWN",
            "confidence": 50,
            "model_scores": [],
            "explanation": f"Failed to read image for HF local pipelines: {e}"
        }

    scores = []
    model_details = []

    for model_cfg in HF_MODELS:
        name = model_cfg["name"]
        results = _query_local_model(name, image)

        if results is None:
            model_details.append({"model": name, "status": "failed", "score": None})
            continue

        fake_pct = _extract_fake_score(results, model_cfg["fake_label"], model_cfg["real_label"])

        if fake_pct is not None:
            scores.append(fake_pct)
            model_details.append({
                "model": name,
                "status": "ok",
                "score": round(fake_pct, 1),
                "raw": results
            })
            short_name = name.split("/")[-1]
            print(f"HF Local [{short_name}]: AI={round(fake_pct, 1)}%")
        else:
            model_details.append({"model": name, "status": "parse_error", "score": None, "raw": results})

    if not scores:
        return {
            "verdict": "UNKNOWN",
            "confidence": 50,
            "model_scores": model_details,
            "explanation": "All local HF models failed or returned unparseable results."
        }

    avg_score = sum(scores) / len(scores)
    max_score = max(scores)

    if avg_score >= 60 or max_score >= 80:
        verdict = "FAKE"
        confidence = int(min(max(avg_score, max_score), 99))
    elif avg_score <= 35:
        verdict = "REAL"
        confidence = int(100 - avg_score)
    else:
        verdict = "UNCERTAIN"
        confidence = 50

    model_summary_parts = []
    for d in model_details:
        if d["status"] == "ok":
            short_name = d["model"].split("/")[-1]
            model_summary_parts.append(f"{short_name}={d['score']}%")
    model_summary = ", ".join(model_summary_parts)

    explanation = (
        f"Local Ensemble of {len(scores)} HF models: "
        f"avg AI score={round(avg_score, 1)}%, "
        f"max={round(max_score, 1)}%. "
        f"Models: {model_summary}"
    )

    return {
        "verdict": verdict,
        "confidence": confidence,
        "model_scores": model_details,
        "explanation": explanation,
    }
