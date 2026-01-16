import os
import base64
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-1.5-pro"
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


# ✅ ADD THIS FUNCTION (THIS FIXES THE CRASH)
def run_vision_llm(image_bytes: bytes) -> dict:
    """
    Compatibility wrapper used by orchestrator.
    """
    return analyze_image_with_gemini(image_bytes)
