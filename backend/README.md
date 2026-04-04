---
title: DeepGuard - Deepfake Detection
emoji: 🛡️
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: true
license: mit
app_port: 7860
---

# DeepGuard Backend API

Advanced Deepfake Detection System powered by PyTorch, EfficientNet, FFT analysis, and Gemini Vision.

## API Endpoints

- `GET /` — Health check
- `GET /health` — Service health
- `GET /docs` — Swagger UI
- `POST /api/predict` — Upload image/video for deepfake analysis
