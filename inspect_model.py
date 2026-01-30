import torch
import os

MODEL_PATH = "backend/app/models/deepguard_video_cnn.pth"

try:
    state = torch.load(MODEL_PATH, map_location="cpu")
    print(f"Shape of head.3.weight: {state['head.3.weight'].shape}")
    print(f"Shape of head.0.weight: {state['head.0.weight'].shape}")
except Exception as e:
    print(f"Error: {e}")
