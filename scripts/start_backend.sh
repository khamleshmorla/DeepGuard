#!/bin/bash

echo "🚀 Setting up DeepGuard Backend Locally..."

# Navigate to backend directory
cd "$(dirname "$0")/../backend"

# 1. Create Virtual Environment if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists."
fi

# 2. Activate Venv
source venv/bin/activate

# 3. Install Dependencies
echo "⬇️ Installing/Updating dependencies..."
pip install -r requirements.txt

# 4. Check for model file (optional but good)
MODEL_DIR="app/models"
# We know model loading is handled by cnn.py with a try-except fallback, so non-critical if missing.

# 5. Run Server
echo "🔥 Starting FastAPI server..."
echo "👉 API will be available at http://localhost:8000"
echo "👉 Press CTRL+C to stop"

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
