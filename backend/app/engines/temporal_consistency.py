import numpy as np

def temporal_consistency(cnn_scores, fft_scores):
    cnn_var = np.std(cnn_scores)
    fft_var = np.std(fft_scores)

    # lower variance = more stable = more REAL
    score = 100 - (cnn_var * 1.5 + fft_var * 2)

    return max(0, min(100, score))
