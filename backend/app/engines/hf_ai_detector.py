"""
Hugging Face AI Image Detector Engine
Uses dedicated AI-vs-Real image classification models via the free HF Inference API.
These models are specifically trained to detect DALL-E 3, Midjourney, Stable Diffusion, etc.
"""
import os
import requests
import time


# Multiple models for ensemble voting
HF_MODELS = [
    {
        "name": "Ateeqq/ai-vs-human-image-detector",
        "fake_label": "ai",
        "real_label": "human",
    },
    {
        "name": "dima806/ai_vs_real_image_detection",
        "fake_label": "ai",
        "real_label": "real",
    },
    {
        "name": "prithivMLmods/Deep-Fake-Detector-v2-Model",
        "fake_label": "Fake",
        "real_label": "Real",
    },
]


def _query_hf_model(model_name, image_bytes, token):
    """Send image bytes to HF Inference API and return classification results."""
    url = "https://api-inference.huggingface.co/models/" + model_name
    headers = {"Authorization": "Bearer " + token}

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
        print("HF model " + model_name + " returned status " + str(resp.status_code))
        return None
    except Exception as e:
        print("HF model " + model_name + " failed: " + str(e))
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


def run_hf_ai_detector(file_path):
    """
    Run ensemble of Hugging Face AI-image-detector models.
    Returns dict with verdict, confidence, model_scores, explanation.
    """
    token = os.getenv("HF_TOKEN", "")

    if not token:
        print("ERROR: HF_TOKEN is empty or not set!")
        return {
            "verdict": "UNKNOWN",
            "confidence": 50,
            "model_scores": [],
            "explanation": "HF_TOKEN not set in .env"
        }
    else:
        print("HF_TOKEN loaded: " + token[:10] + "...")

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

    scores = []
    model_details = []

    for model_cfg in HF_MODELS:
        name = model_cfg["name"]
        results = _query_hf_model(name, image_bytes, token)

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
            print("HF [" + short_name + "]: AI=" + str(round(fake_pct, 1)) + "%")
        else:
            model_details.append({"model": name, "status": "parse_error", "score": None, "raw": results})

    if not scores:
        return {
            "verdict": "UNKNOWN",
            "confidence": 50,
            "model_scores": model_details,
            "explanation": "All HF models failed or returned unparseable results."
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
            model_summary_parts.append(short_name + "=" + str(d["score"]) + "%")
    model_summary = ", ".join(model_summary_parts)

    explanation = (
        "Ensemble of " + str(len(scores)) + " HF models: "
        "avg AI score=" + str(round(avg_score, 1)) + "%, "
        "max=" + str(round(max_score, 1)) + "%. "
        "Models: " + model_summary
    )

    return {
        "verdict": verdict,
        "confidence": confidence,
        "model_scores": model_details,
        "explanation": explanation,
    }
