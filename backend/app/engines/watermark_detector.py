import pytesseract
from PIL import Image

KEYWORDS = [
    "deepfake",
    "faceswap",
    "face swap",
    "ai generated",
    "this video is",
    "generated",
    "synthesized"
]


def detect_watermark(image_path: str) -> bool:
    """
    Detect visible AI/deepfake watermarks via OCR.
    """
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img).lower()
        return any(k in text for k in KEYWORDS)
    except Exception:
        return False
