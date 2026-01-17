import torch
import torch.nn as nn
import timm
from torchvision import transforms
from PIL import Image
import numpy as np
import os

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_PATH = "app/models/deepguard_multhead_celebdf_final.pth"


# -------------------------------
# Multi-head CNN architecture
# -------------------------------
class DeepGuardMultiHead(nn.Module):
    def __init__(self, backbone="efficientnet_b0"):
        super().__init__()

        self.backbone = timm.create_model(
            backbone,
            pretrained=False,
            num_classes=0
        )

        feat_dim = self.backbone.num_features

        def make_head():
            return nn.Sequential(
                nn.Linear(feat_dim, 256),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(256, 1)
            )

        self.face_head = make_head()
        self.texture_head = make_head()
        self.artifact_head = make_head()
        self.final_head = make_head()

    def forward(self, x):
        feats = self.backbone(x)
        return {
            "face": torch.sigmoid(self.face_head(feats)),
            "texture": torch.sigmoid(self.texture_head(feats)),
            "artifact": torch.sigmoid(self.artifact_head(feats)),
            "final": torch.sigmoid(self.final_head(feats)),
        }


# -------------------------------
# Load model once
# -------------------------------
_model = None

def load_model():
    global _model
    if _model is None:
        model = DeepGuardMultiHead()
        model.load_state_dict(
            torch.load(MODEL_PATH, map_location=DEVICE)
        )
        model.eval()
        model.to(DEVICE)
        _model = model
        print("✅ DeepGuard CNN loaded successfully")
    return _model


# -------------------------------
# Preprocessing
# -------------------------------
_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),   # uses NumPy internally
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# -------------------------------
# Public inference function
# -------------------------------
def run_cnn(image_path: str) -> dict:
    model = load_model()

    image = Image.open(image_path).convert("RGB")

    try:
        x = _transform(image).unsqueeze(0).to(DEVICE)
    except Exception as e:
        # Absolute safety fallback
        print("⚠️ CNN preprocessing failed:", e)
        return {
            "face": 50,
            "texture": 50,
            "artifact": 50,
            "fake": 50,
        }

    with torch.no_grad():
        out = model(x)

    return {
        "face": float(out["face"].item() * 100),
        "texture": float(out["texture"].item() * 100),
        "artifact": float(out["artifact"].item() * 100),
        "fake": float(out["final"].item() * 100),
    }
