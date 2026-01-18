import cv2
import numpy as np


def fft_score(image_path: str) -> float:
    """
    Frequency-domain anomaly score.
    Returns a value in [0, 100].
    Higher = more likely AI-generated.

    Phase 1: OBSERVATION ONLY
    """

    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return 50.0

        img = cv2.resize(img, (256, 256))

        # -----------------------------
        # FFT
        # -----------------------------
        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)
        magnitude = np.log(np.abs(fshift) + 1)

        h, w = magnitude.shape
        cy, cx = h // 2, w // 2

        # -----------------------------
        # PURE NUMPY MASK (NO OPENCV)
        # -----------------------------
        y, x = np.ogrid[:h, :w]
        distance = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)

        radius = min(h, w) // 6

        low_freq_mask = distance <= radius
        high_freq_mask = distance > radius

        low_freq_energy = magnitude[low_freq_mask].mean()
        high_freq_energy = magnitude[high_freq_mask].mean()

        ratio = high_freq_energy / (low_freq_energy + 1e-6)

        # -----------------------------
        # Ratio → Score mapping
        # -----------------------------
        score = (ratio - 1.15) * 60 + 50
        score = float(np.clip(score, 0, 100))

        return score

    except Exception as e:
        print("⚠️ FFT failed safely:", e)
        return 50.0
