from PIL import Image
from PIL.ExifTags import TAGS


def extract_exif_authenticity(image_path: str) -> dict:
    """
    Extract EXIF-based authenticity signals.
    Returns a score in [0, 100].
    Higher = more likely REAL camera photo.
    """

    signals = {
        "has_exif": False,
        "has_camera_make": False,
        "has_camera_model": False,
        "has_timestamp": False,
        "has_gps": False,
        "authenticity_score": 0,
    }

    try:
        with Image.open(image_path) as img:
            exif = img._getexif()

        if not exif:
            return signals

        signals["has_exif"] = True

        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)

            if tag == "Make":
                signals["has_camera_make"] = True
            elif tag == "Model":
                signals["has_camera_model"] = True
            elif tag == "DateTime":
                signals["has_timestamp"] = True
            elif tag == "GPSInfo":
                signals["has_gps"] = True

        # Scoring (conservative & explainable)
        score = 0
        if signals["has_exif"]:
            score += 30
        if signals["has_camera_make"]:
            score += 25
        if signals["has_camera_model"]:
            score += 15
        if signals["has_timestamp"]:
            score += 15
        if signals["has_gps"]:
            score += 15

        signals["authenticity_score"] = min(score, 100)

        return signals

    except Exception as e:
        print("⚠️ EXIF extraction failed:", e)
        return signals
