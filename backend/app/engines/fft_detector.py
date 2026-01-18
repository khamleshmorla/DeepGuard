import cv2
import numpy as np

def fft_score(image_path: str) -> float:
    """
    Frequency-domain anomaly score.
    Returns a value in [0, 100].
    Higher = more likely AI-generated.
    """

    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return 50.0

        img = cv2.resize(img, (256, 256))

        # FFT
        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)
        magnitude = np.log(np.abs(fshift) + 1)

        h, w = magnitude.shape
        cy, cx = h // 2, w // 2

        # Separate low vs high frequency
        radius = min(h, w) // 6
        mask = np.ones_like(magnitude, dtype=np.uint8)
        cv2.circle(mask, (cx, cy), radius, 0, -1)

        high_freq_energy = magnitude[mask == 1].mean()
        low_freq_energy = magnitude[mask == 0].mean()

        ratio = high_freq_energy / (low_freq_energy + 1e-6)

        # Normalize ratio → score
        score = (ratio - 1.15) * 60 + 50
        return float(np.clip(score, 0, 100))

    except Exception as e:
        print("⚠️ FFT failed:", e)
        return 50.0
