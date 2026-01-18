import cv2
import numpy as np


def detect_watermark(image_path: str) -> bool:
    """
    Lightweight watermark detection without OCR.
    Detects high-contrast text-like overlays.
    """

    try:
        img = cv2.imread(image_path)
        if img is None:
            return False

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Edge detection (text creates strong edges)
        edges = cv2.Canny(gray, 100, 200)

        h, w = edges.shape
        corner_regions = [
            edges[0:int(h*0.25), 0:int(w*0.25)],         # top-left
            edges[0:int(h*0.25), int(w*0.75):w],         # top-right
            edges[int(h*0.75):h, 0:int(w*0.25)],         # bottom-left
            edges[int(h*0.75):h, int(w*0.75):w],         # bottom-right
        ]

        for region in corner_regions:
            density = np.sum(region > 0) / region.size
            if density > 0.08:  # tuned threshold
                return True

        return False

    except Exception:
        return False
