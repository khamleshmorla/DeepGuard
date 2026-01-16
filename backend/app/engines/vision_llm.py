import os
import json

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except Exception:
    GENAI_AVAILABLE = False


def run_vision_llm(file_path: str, file_type: str) -> dict:
    """
    Gemini Vision – Lovable-style forensic analysis
    - Guilty until proven innocent
    - Structured signals
    - Rule-based verdict
    - NEVER crashes backend
    """

    # ---------------- SAFE DEFAULT ----------------
    base_signals = {
        "facialAnalysis": 50,
        "temporalConsistency": 50,
        "artifactDetection": 50,
        "metadataAnalysis": 50,
    }

    if file_type != "image":
        return {
            "signals": base_signals,
            "verdict": "UNKNOWN",
            "confidence": 50,
            "explanation": "Vision LLM skipped for non-image input."
        }

    if not GENAI_AVAILABLE:
        return {
            "signals": base_signals,
            "verdict": "UNKNOWN",
            "confidence": 50,
            "explanation": "Gemini SDK unavailable."
        }

    try:
        # ---------------- LOAD IMAGE ----------------
        with open(file_path, "rb") as f:
            image_bytes = f.read()

        # ---------------- INIT CLIENT ----------------
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        # ---------------- FORENSIC SYSTEM PROMPT ----------------
        prompt = """
You are a digital media forensics expert.

Default assumption: FAKE (guilty until proven innocent).

Analyze the image carefully.

RED FLAGS (cause FAKE):
- Eye reflection inconsistency
- Over-smooth or waxy skin
- Hair boundary artifacts
- Warped or repeating background
- GAN/compression artifacts

AUTHENTICITY MARKERS (support REAL):
- Natural skin imperfections
- Asymmetry in face
- Uneven lighting
- Minor motion blur or noise
- Camera-consistent compression

Rules:
- If ANY red flag is present → FAKE
- REAL only if 3 or more authenticity markers AND zero red flags

Respond STRICTLY in valid JSON:

{
  "facialAnalysis": number 0-100,
  "temporalConsistency": number 0-100,
  "artifactDetection": number 0-100,
  "metadataAnalysis": number 0-100,
  "redFlags": ["string"],
  "authenticityMarkers": ["string"],
  "verdict": "REAL or FAKE",
  "explanation": "human-readable reasoning"
}
"""

        # ---------------- GEMINI VISION CALL ----------------
        response = client.models.generate_content(
            model="gemini-1.5-pro",
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(image_bytes, mime_type="image/jpeg"),
                        types.Part.from_text(prompt),
                    ],
                )
            ],
        )

        raw_text = response.text.strip()

        # ---------------- PARSE JSON ----------------
        data = json.loads(raw_text)

        signals = {
            "facialAnalysis": int(data.get("facialAnalysis", 50)),
            "temporalConsistency": int(data.get("temporalConsistency", 50)),
            "artifactDetection": int(data.get("artifactDetection", 50)),
            "metadataAnalysis": int(data.get("metadataAnalysis", 50)),
        }

        red_flags = data.get("redFlags", [])
        authenticity = data.get("authenticityMarkers", [])
        verdict = data.get("verdict", "FAKE")
        explanation = data.get("explanation", "")

        # ---------------- RULE-BASED CONFIDENCE ----------------
        if verdict == "FAKE":
            confidence = min(
                100,
                60 + len(red_flags) * 10 + signals["artifactDetection"] // 10
            )
        else:
            confidence = min(
                100,
                70 + len(authenticity) * 5
            )

        return {
            "signals": signals,
            "verdict": verdict,
            "confidence": confidence,
            "explanation": explanation,
            "detectedTechniques": red_flags,
            "authenticityMarkers": authenticity,
        }

    except Exception as e:
        # ---------------- ABSOLUTE SAFETY ----------------
        return {
            "signals": base_signals,
            "verdict": "UNKNOWN",
            "confidence": 50,
            "explanation": f"Vision LLM failed safely: {str(e)}"
        }
