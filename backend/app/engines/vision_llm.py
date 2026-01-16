import os
import base64
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ FIXED: Vision-capable model
MODEL_NAME = "gemini-1.5-pro-vision"
model = genai.GenerativeModel(MODEL_NAME)


def analyze_image_with_gemini(image_bytes: bytes) -> dict:
    prompt = """
You are a digital media forensics expert.

Analyze this image for signs of AI-generated or manipulated content.

Focus on:
- Facial symmetry anomalies
- Eye reflection consistency
- Skin texture artifacts
- Lighting and shadow coherence
- Hair and background blending
- Compression artifacts

Respond STRICTLY in this JSON format:
{
  "verdict": "REAL or FAKE",
  "confidence": number from 0 to 100,
  "explanation": "short forensic explanation (2-3 lines)"
}
"""

    response = model.generate_content(
        [
            prompt,
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_bytes).decode()
            }
        ]
    )

    text = response.text.strip()

    try:
        import json
        return json.loads(text)
    except Exception:
        return {
            "verdict": "FAKE",
            "confidence": 50,
            "explanation": "Gemini response parsing failed."
        }


def run_vision_llm(file_path: str, file_type: str) -> dict:
    """
    Orchestrator-compatible Gemini Vision entrypoint.
    """

    if file_type != "image":
        return {
            "verdict": "UNKNOWN",
            "confidence": 0,
            "explanation": "Vision LLM skipped for non-image input."
        }

    with open(file_path, "rb") as f:
        image_bytes = f.read()

    return analyze_image_with_gemini(image_bytes)
