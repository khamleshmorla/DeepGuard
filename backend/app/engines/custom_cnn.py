import torch
import torch.nn as nn
import timm
from torchvision import transforms
from PIL import Image
import threading

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_PATH = "app/models/deepguard_video_cnn.pth"

# -------------------------------
# Custom Model Architecture
# -------------------------------
class CustomEfficientNet(nn.Module):
    def __init__(self):
        super().__init__()
        # Load backbone without classifier
        self.backbone = timm.create_model('efficientnet_b0', pretrained=False, num_classes=0)
        
        # Reconstruction of the head based on state dict shapes
        # head.0: [256, 1280] -> Linear
        # head.3: [1, 256] -> Linear
        self.head = nn.Sequential(
            nn.Linear(1280, 256),
            nn.ReLU(),
            nn.Dropout(0.3), # Standard dropout guess
            nn.Linear(256, 1)
        )

    def forward(self, x):
        features = self.backbone(x)
        logits = self.head(features)
        return torch.sigmoid(logits)

# -------------------------------
# Load model once (Thread-safe)
# -------------------------------
_model = None
_model_lock = threading.Lock()

def load_custom_model():
    global _model
    with _model_lock:
        if _model is None:
            model = CustomEfficientNet()
            try:
                state_dict = torch.load(MODEL_PATH, map_location=DEVICE)
                model.load_state_dict(state_dict)
                model.eval()
                model.to(DEVICE)
                _model = model
                print("✅ Custom Kaggle Model loaded successfully")
            except FileNotFoundError:
                print(f"❌ Custom model not found at {MODEL_PATH}")
                return None
            except Exception as e:
                print(f"❌ Failed to load custom model: {e}")
                return None
    return _model

# -------------------------------
# Preprocessing
# -------------------------------
_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# -------------------------------
# Inference
# -------------------------------
def run_custom_cnn(image_path: str) -> float:
    """
    Returns fake probability (0-100).
    """
    model = load_custom_model()
    if model is None:
        return 50.0  # Neutral if failed

    try:
        with Image.open(image_path) as img:
            image = img.convert("RGB")
            x = _transform(image).unsqueeze(0).to(DEVICE)
            
        with torch.no_grad():
            out = model(x)
            prob = out.item() * 100
            
        return prob
    except Exception as e:
        print(f"⚠️ Custom CNN failed: {e}")
        return 50.0
