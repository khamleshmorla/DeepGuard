FROM python:3.11-slim

WORKDIR /app

# System deps for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the transformer models to the image for fast ensemble startup
RUN python3 -c "from transformers import pipeline; \
    pipeline('image-classification', model='Ateeqq/ai-vs-human-image-detector'); \
    pipeline('image-classification', model='haywoodsloan/ai-image-detector-deploy'); \
    pipeline('image-classification', model='umm-maybe/AI-image-detector')"

# Copy app
COPY app ./app

# Expose port (HF Spaces expects 7860)
EXPOSE 7860

# Run server on port 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
