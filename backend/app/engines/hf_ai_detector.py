"""
Hugging Face AI Image Detector Engine
Uses a locally-loaded transformer model for FAST inference (~1-2 seconds),
with API fallback if the local model fails to load.

Primary model: Ateeqq/ai-vs-human-image-detector (SigLIP-based, 99.97% on DALL-E)
"""
import os
import requests
import time
from PIL import Image

# ================================================================
# LOCAL MODEL (fast path — loaded once at startup, reused forever)
# ================================================================
_local_classifier = None
_local_model_loaded = False
_local_load_error = None

LOCAL_MODEL_NAME = "Ateeqq/ai-vs-human-image-detector"
LOCAL_FAKE_LABEL = "ai"
LOCAL_REAL_LABEL = "hum"


def _load_local_model():
    """Load the transformer model into memory. Called once at startup."""
    global _local_classifier, _local_model_loaded, _local_load_error

    if _local_model_loaded:
        return _local_classifier is not None

    try:
        from transformers import pipeline
        print("Loading local AI detector model: " + LOCAL_MODEL_NAME + "...")
        start = time.time()
        _local_classifier = pipeline(
            "image-classification",
            model=LOCAL_MODEL_NAME,
            device=-1,  # CPU only (no GPU needed)
        )
        elapsed = round(time.time() - start, 1)
        print("Local AI detector loaded in " + str(elapsed) + "s")
        _local_model_loaded = True
        return True
    except Exception as e:
        _local_load_error = str(e)
        _local_model_loaded = True  # Don't retry
        print("Failed to load local model: " + str(e))
        print("Will fall back to HF API calls.")
        return False


def _run_local_model(file_path):
    """Run the locally-loaded model. Returns (fake_score, raw_results) or (None, None)."""
    if _local_classifier is None:
        return None, None

    try:
        img = Image.open(file_path).convert("RGB")
        results = _local_classifier(img)

        # Extract scores
        fake_score = None
        for item in results:
            label = item.get("label", "").lower().strip()
            score = item.get("score", 0) * 100
            if LOCAL_FAKE_LABEL in label:
                fake_score = score
            elif LOCAL_REAL_LABEL in label and fake_score is None:
                fake_score = 100 - score

        return fake_score, results
    except Exception as e:
        print("Local model inference failed: " + str(e))
        return None, None


# ================================================================
# API MODELS (fallback — slower but works if local model fails)
# ================================================================
API_MODELS = [
    {
        "name": "umm-maybe/AI-image-detector",
        "fake_label": "artificial",
        "real_label": "human",
    },
    {
        "name": "haywoodsloan/ai-image-detector-deploy",
        "fake_label": "artificial",
        "real_label": "real",
    },
]

HF_API_BASE = "https://router.huggingface.co/hf-inference/models/"


def _query_hf_api(model_name, image_bytes, token):
    """Send image bytes to HF Inference API and return classification results."""
    url = HF_API_BASE + model_name
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "image/jpeg",
    }

    try:
        resp = requests.post(url, headers=headers, data=image_bytes, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 503:
            body = resp.json()
            wait_time = body.get("estimated_time", 20)
            print("HF model " + model_name + " is loading, waiting...")
            time.sleep(min(wait_time, 30))
            resp2 = requests.post(url, headers=headers, data=image_bytes, timeout=60)
            if resp2.status_code == 200:
                return resp2.json()
        print("HF API " + model_name + " returned status " + str(resp.status_code))
        return None
    except Exception as e:
        print("HF API " + model_name + " failed: " + str(e))
        return None


def _extract_fake_score(results, fake_label, real_label):
    """Extract the 'fake/AI' probability from HF classification output."""
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


# ================================================================
# MAIN ENTRY POINT (same interface — orchestrator doesn't change)
# ================================================================

# Eagerly try to load local model at import time
_load_local_model()


def run_hf_ai_detector(file_path):
    """
    Run AI-image detection.
    - Fast path: local model (~1-2 seconds)
    - Slow path: HF API calls (~15-30 seconds, only if local model failed to load)

    Returns dict with verdict, confidence, model_scores, explanation.
    """

    scores = []
    model_details = []

    # ---- FAST PATH: Local model ----
    if _local_classifier is not None:
        start = time.time()
        fake_pct, raw = _run_local_model(file_path)
        elapsed = round(time.time() - start, 1)

        if fake_pct is not None:
            scores.append(fake_pct)
            model_details.append({
                "model": LOCAL_MODEL_NAME,
                "status": "ok",
                "score": round(fake_pct, 1),
                "source": "local",
            })
            print("LOCAL [" + LOCAL_MODEL_NAME.split("/")[-1] + "]: AI=" + str(round(fake_pct, 1)) + "% (" + str(elapsed) + "s)")

    # ---- SLOW PATH: API models (only if local model failed or as secondary vote) ----
    if not scores:
        # Local model didn't work — use API as fallback
        token = os.getenv("HF_TOKEN", "")
        if not token:
            print("ERROR: HF_TOKEN not set and local model unavailable!")
            return {
                "verdict": "UNKNOWN",
                "confidence": 50,
                "model_scores": [],
                "explanation": "Local model unavailable and HF_TOKEN not set."
            }

        try:
            with open(file_path, "rb") as f:
                image_bytes = f.read()
        except Exception as e:
            return {
                "verdict": "UNKNOWN",
                "confidence": 50,
                "model_scores": [],
                "explanation": "Failed to read image: " + str(e)
            }

        print("Using API fallback (local model unavailable)...")
        for model_cfg in API_MODELS:
            name = model_cfg["name"]
            results = _query_hf_api(name, image_bytes, token)

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
                    "source": "api",
                })
                short_name = name.split("/")[-1]
                print("API [" + short_name + "]: AI=" + str(round(fake_pct, 1)) + "%")

    # ---- VERDICT ----
    if not scores:
        return {
            "verdict": "UNKNOWN",
            "confidence": 50,
            "model_scores": model_details,
            "explanation": "All detection methods failed."
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
            src = d.get("source", "?")
            model_summary_parts.append(short_name + "=" + str(d["score"]) + "% [" + src + "]")
    model_summary = ", ".join(model_summary_parts)

    explanation = (
        str(len(scores)) + " model(s): "
        "avg AI=" + str(round(avg_score, 1)) + "%, "
        "max=" + str(round(max_score, 1)) + "%. "
        + model_summary
    )

    return {
        "verdict": verdict,
        "confidence": confidence,
        "model_scores": model_details,
        "explanation": explanation,
    }
