#!/bin/bash
# ==========================================================
# DeepGuard → Hugging Face Spaces Deployment Script
# ==========================================================
# This script deploys the backend to Hugging Face Spaces
# and provides instructions for frontend deployment on Vercel.
#
# Prerequisites:
#   1. Install HF CLI:  pip install huggingface_hub[cli]
#   2. Login to HF:     hf login
#   3. Install Git LFS: brew install git-lfs  (macOS)
# ==========================================================

set -e

# ---- CONFIG ----
HF_USERNAME="${1:-YOUR_HF_USERNAME}"
SPACE_NAME="${2:-deepguard-backend}"
BACKEND_DIR="$(cd "$(dirname "$0")/.." && pwd)/backend"

echo ""
echo "🛡️  DeepGuard → Hugging Face Spaces Deployment"
echo "================================================"
echo "  HF Username  : $HF_USERNAME"
echo "  Space Name   : $SPACE_NAME"
echo "  Backend Dir  : $BACKEND_DIR"
echo "================================================"
echo ""

# ---- STEP 1: Validate ----
if [ "$HF_USERNAME" = "YOUR_HF_USERNAME" ]; then
    echo "❌ Usage: ./deploy_hf.sh <hf_username> [space_name]"
    echo "   Example: ./deploy_hf.sh khamlesh deepguard-backend"
    exit 1
fi

if ! command -v hf &> /dev/null; then
    echo "❌ hf not found. Install it with:"
    echo "   pip install huggingface_hub[cli]"
    exit 1
fi

if ! command -v git-lfs &> /dev/null; then
    echo "❌ git-lfs not found. Install it with:"
    echo "   brew install git-lfs"
    exit 1
fi

# ---- STEP 2: Create HF Space (if not exists) ----
echo "📦 Creating Hugging Face Space..."
hf repo create "$HF_USERNAME/$SPACE_NAME" --repo-type space --space-sdk docker 2>/dev/null || echo "   (Space may already exist, continuing...)"

# ---- STEP 3: Clone the Space ----
TEMP_DIR=$(mktemp -d)
echo "📥 Cloning Space to temp directory..."
git clone "https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME" "$TEMP_DIR/space"
cd "$TEMP_DIR/space"

# ---- STEP 4: Initialize Git LFS for model files ----
echo "📎 Setting up Git LFS for model files..."
git lfs install
git lfs track "*.pth"
git add .gitattributes

# ---- STEP 5: Copy backend files ----
echo "📋 Copying backend files..."

# Copy README.md (with HF Space metadata)
cp "$BACKEND_DIR/README.md" ./README.md

# Copy Dockerfile
cp "$BACKEND_DIR/Dockerfile" ./Dockerfile

# Copy requirements.txt
cp "$BACKEND_DIR/requirements.txt" ./requirements.txt

# Copy app directory (including models)
cp -r "$BACKEND_DIR/app" ./app

# Remove __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
# Remove .DS_Store files
find . -name ".DS_Store" -delete 2>/dev/null || true

# ---- STEP 6: Commit and push ----
echo "🚀 Pushing to Hugging Face Spaces..."
git add -A
git commit -m "🛡️ Deploy DeepGuard backend to HF Spaces"
git push

# ---- STEP 7: Cleanup ----
echo "🧹 Cleaning up temp directory..."
rm -rf "$TEMP_DIR"

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo "================================================"
echo "  🌐 Backend URL:  https://$HF_USERNAME-$SPACE_NAME.hf.space"
echo "  📖 Swagger Docs: https://$HF_USERNAME-$SPACE_NAME.hf.space/docs"
echo "  📊 Space Page:   https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME"
echo "================================================"
echo ""
echo "⚠️  NEXT STEPS:"
echo "  1. Set your GEMINI_API_KEY as a Space Secret:"
echo "     → Go to https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME/settings"
echo "     → Add secret: GEMINI_API_KEY = your_key"
echo ""
echo "  2. Update your frontend VITE_API_URL:"
echo "     → In .env or Vercel dashboard, set:"
echo "     → VITE_API_URL=https://$HF_USERNAME-$SPACE_NAME.hf.space"
echo ""
echo "  3. Deploy frontend to Vercel:"
echo "     → npx vercel --prod"
echo "================================================"
