# ML Pipeline Documentation

Complete guide for training and using the deepfake detection model.

## Model Architecture

DeepGuard uses a CNN-based architecture with transfer learning:

```
EfficientNet-B0 (pretrained on ImageNet)
    ↓
Global Average Pooling
    ↓
Dropout (0.2)
    ↓
Linear Layer (1280 → 1)
    ↓
Sigmoid Activation
    ↓
Output: Probability [0, 1]
```

- **0** = REAL (authentic content)
- **1** = FAKE (AI-generated/manipulated)

## Dataset Preparation

### Folder Structure

```
data/
├── train/
│   ├── real/           # 70% of real images
│   │   ├── img001.jpg
│   │   ├── img002.jpg
│   │   └── ...
│   └── fake/           # 70% of fake images
│       ├── img001.jpg
│       └── ...
├── val/
│   ├── real/           # 15% of real images
│   └── fake/           # 15% of fake images
└── test/
    ├── real/           # 15% of real images
    └── fake/           # 15% of fake images
```

### Recommended Datasets

1. **FaceForensics++** (Academic license required)
   - 1000 original videos
   - 4000 manipulated videos (4 methods)
   - Download: https://github.com/ondyari/FaceForensics

2. **Celeb-DF v2** (Public)
   - 590 real celebrity videos
   - 5639 deepfake videos
   - Download: https://github.com/yuezunli/celeb-deepfakeforensics

3. **DFDC Preview** (Public)
   - 5000 videos from Facebook's challenge
   - Download: https://ai.facebook.com/datasets/dfdc/

### Dataset Download Script

Create `ml/download_dataset.py`:

```python
"""
Script to download and prepare datasets.
Note: Some datasets require registration/academic access.
"""

import os
import requests
import zipfile
from pathlib import Path

def download_sample_dataset(output_dir: str = "data"):
    """
    Download a small sample dataset for testing.
    For production, use FaceForensics++ or Celeb-DF.
    """
    
    # Create directories
    Path(f"{output_dir}/train/real").mkdir(parents=True, exist_ok=True)
    Path(f"{output_dir}/train/fake").mkdir(parents=True, exist_ok=True)
    Path(f"{output_dir}/val/real").mkdir(parents=True, exist_ok=True)
    Path(f"{output_dir}/val/fake").mkdir(parents=True, exist_ok=True)
    
    print("Dataset directories created!")
    print("\nTo train the model, add images to:")
    print(f"  - {output_dir}/train/real/ (authentic images)")
    print(f"  - {output_dir}/train/fake/ (deepfake images)")
    print(f"  - {output_dir}/val/real/")
    print(f"  - {output_dir}/val/fake/")
    
    print("\nRecommended datasets:")
    print("1. FaceForensics++: https://github.com/ondyari/FaceForensics")
    print("2. Celeb-DF v2: https://github.com/yuezunli/celeb-deepfakeforensics")
    print("3. DFDC: https://ai.facebook.com/datasets/dfdc/")

def extract_frames_from_videos(video_dir: str, output_dir: str, frames_per_video: int = 10):
    """Extract frames from video files for training."""
    import cv2
    
    for video_file in os.listdir(video_dir):
        if not video_file.endswith(('.mp4', '.avi', '.mov')):
            continue
            
        video_path = os.path.join(video_dir, video_file)
        cap = cv2.VideoCapture(video_path)
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_interval = max(1, total_frames // frames_per_video)
        
        frame_count = 0
        saved_count = 0
        
        while cap.isOpened() and saved_count < frames_per_video:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                output_path = os.path.join(
                    output_dir, 
                    f"{os.path.splitext(video_file)[0]}_frame{saved_count:03d}.jpg"
                )
                cv2.imwrite(output_path, frame)
                saved_count += 1
            
            frame_count += 1
        
        cap.release()
        print(f"Extracted {saved_count} frames from {video_file}")

if __name__ == "__main__":
    download_sample_dataset()
```

## Training

### Basic Training

```bash
cd backend
python -m ml.train
```

### Training with Custom Parameters

```python
from ml.train import train_model

model = train_model(
    train_dir="data/train",
    val_dir="data/val",
    epochs=20,
    batch_size=32,
    learning_rate=0.0001,
    save_path="models/deepfake_v2.pth"
)
```

### Training Configuration

Create `ml/config.py`:

```python
"""Training configuration."""

class TrainConfig:
    # Data
    TRAIN_DIR = "data/train"
    VAL_DIR = "data/val"
    TEST_DIR = "data/test"
    
    # Model
    MODEL_NAME = "efficientnet_b0"  # Options: efficientnet_b0, resnet50, resnet18
    PRETRAINED = True
    NUM_CLASSES = 1  # Binary classification
    
    # Training
    EPOCHS = 20
    BATCH_SIZE = 32
    LEARNING_RATE = 0.001
    WEIGHT_DECAY = 1e-4
    
    # Scheduler
    SCHEDULER = "reduce_on_plateau"
    SCHEDULER_PATIENCE = 3
    SCHEDULER_FACTOR = 0.5
    
    # Augmentation
    USE_AUGMENTATION = True
    RANDOM_CROP = True
    HORIZONTAL_FLIP = True
    COLOR_JITTER = True
    
    # Hardware
    USE_GPU = True
    NUM_WORKERS = 4
    
    # Paths
    CHECKPOINT_DIR = "checkpoints"
    MODEL_SAVE_PATH = "models/deepfake_detector.pth"
    
    # Early stopping
    EARLY_STOPPING = True
    PATIENCE = 5
```

### Advanced Training Script

Create `ml/train_advanced.py`:

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import ReduceLROnPlateau, CosineAnnealingLR
from torchvision import models, transforms
import os
from datetime import datetime
import json
from tqdm import tqdm

from dataset import DeepfakeDataset
from config import TrainConfig

class Trainer:
    def __init__(self, config: TrainConfig = TrainConfig()):
        self.config = config
        self.device = torch.device(
            "cuda" if config.USE_GPU and torch.cuda.is_available() else "cpu"
        )
        print(f"Using device: {self.device}")
        
        self.model = self._build_model()
        self.criterion = nn.BCELoss()
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=config.LEARNING_RATE,
            weight_decay=config.WEIGHT_DECAY
        )
        self.scheduler = ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            patience=config.SCHEDULER_PATIENCE,
            factor=config.SCHEDULER_FACTOR
        )
        
        self.train_loader = self._get_dataloader(config.TRAIN_DIR, is_train=True)
        self.val_loader = self._get_dataloader(config.VAL_DIR, is_train=False)
        
        self.best_val_acc = 0.0
        self.best_val_loss = float('inf')
        self.epochs_without_improvement = 0
        self.history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}
    
    def _build_model(self):
        """Build the model architecture."""
        if self.config.MODEL_NAME == "efficientnet_b0":
            model = models.efficientnet_b0(
                weights=models.EfficientNet_B0_Weights.DEFAULT if self.config.PRETRAINED else None
            )
            num_features = model.classifier[1].in_features
            model.classifier = nn.Sequential(
                nn.Dropout(p=0.3),
                nn.Linear(num_features, 256),
                nn.ReLU(),
                nn.Dropout(p=0.2),
                nn.Linear(256, 1),
                nn.Sigmoid()
            )
        elif self.config.MODEL_NAME == "resnet50":
            model = models.resnet50(
                weights=models.ResNet50_Weights.DEFAULT if self.config.PRETRAINED else None
            )
            num_features = model.fc.in_features
            model.fc = nn.Sequential(
                nn.Linear(num_features, 256),
                nn.ReLU(),
                nn.Dropout(p=0.3),
                nn.Linear(256, 1),
                nn.Sigmoid()
            )
        else:
            raise ValueError(f"Unknown model: {self.config.MODEL_NAME}")
        
        return model.to(self.device)
    
    def _get_transforms(self, is_train: bool):
        """Get data transforms."""
        if is_train and self.config.USE_AUGMENTATION:
            return transforms.Compose([
                transforms.Resize((256, 256)),
                transforms.RandomCrop(224),
                transforms.RandomHorizontalFlip(),
                transforms.RandomRotation(15),
                transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
        else:
            return transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
    
    def _get_dataloader(self, data_dir: str, is_train: bool):
        """Create a dataloader."""
        dataset = DeepfakeDataset(data_dir, transform=self._get_transforms(is_train))
        return DataLoader(
            dataset,
            batch_size=self.config.BATCH_SIZE,
            shuffle=is_train,
            num_workers=self.config.NUM_WORKERS,
            pin_memory=True
        )
    
    def train_epoch(self):
        """Train for one epoch."""
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(self.train_loader, desc="Training")
        for images, labels in pbar:
            images = images.to(self.device)
            labels = labels.float().to(self.device)
            
            self.optimizer.zero_grad()
            outputs = self.model(images).squeeze()
            loss = self.criterion(outputs, labels)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item() * images.size(0)
            predictions = (outputs > 0.5).float()
            correct += (predictions == labels).sum().item()
            total += labels.size(0)
            
            pbar.set_postfix({"loss": loss.item(), "acc": correct / total})
        
        return total_loss / total, correct / total
    
    def validate(self):
        """Validate the model."""
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in tqdm(self.val_loader, desc="Validating"):
                images = images.to(self.device)
                labels = labels.float().to(self.device)
                
                outputs = self.model(images).squeeze()
                loss = self.criterion(outputs, labels)
                
                total_loss += loss.item() * images.size(0)
                predictions = (outputs > 0.5).float()
                correct += (predictions == labels).sum().item()
                total += labels.size(0)
        
        return total_loss / total, correct / total
    
    def train(self):
        """Full training loop."""
        print(f"Starting training for {self.config.EPOCHS} epochs...")
        
        for epoch in range(self.config.EPOCHS):
            print(f"\nEpoch {epoch + 1}/{self.config.EPOCHS}")
            
            train_loss, train_acc = self.train_epoch()
            val_loss, val_acc = self.validate()
            
            self.scheduler.step(val_loss)
            
            # Record history
            self.history["train_loss"].append(train_loss)
            self.history["train_acc"].append(train_acc)
            self.history["val_loss"].append(val_loss)
            self.history["val_acc"].append(val_acc)
            
            print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
            print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
            
            # Save best model
            if val_acc > self.best_val_acc:
                self.best_val_acc = val_acc
                self.best_val_loss = val_loss
                self.epochs_without_improvement = 0
                self.save_model()
                print(f"✓ Saved best model with val_acc: {val_acc:.4f}")
            else:
                self.epochs_without_improvement += 1
            
            # Early stopping
            if self.config.EARLY_STOPPING and self.epochs_without_improvement >= self.config.PATIENCE:
                print(f"Early stopping after {epoch + 1} epochs")
                break
        
        self.save_history()
        print(f"\nTraining complete! Best val_acc: {self.best_val_acc:.4f}")
        return self.model
    
    def save_model(self):
        """Save model checkpoint."""
        os.makedirs(os.path.dirname(self.config.MODEL_SAVE_PATH), exist_ok=True)
        torch.save({
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "best_val_acc": self.best_val_acc,
            "config": {
                "model_name": self.config.MODEL_NAME,
                "epochs": self.config.EPOCHS,
                "batch_size": self.config.BATCH_SIZE,
                "learning_rate": self.config.LEARNING_RATE
            }
        }, self.config.MODEL_SAVE_PATH)
    
    def save_history(self):
        """Save training history."""
        os.makedirs(self.config.CHECKPOINT_DIR, exist_ok=True)
        history_path = os.path.join(
            self.config.CHECKPOINT_DIR,
            f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(history_path, "w") as f:
            json.dump(self.history, f, indent=2)
        print(f"History saved to {history_path}")

if __name__ == "__main__":
    trainer = Trainer()
    trainer.train()
```

## Inference

### Single Image Prediction

```python
from app.models.detector import DeepfakeDetector
from PIL import Image

detector = DeepfakeDetector(model_path="models/deepfake_detector.pth")

image = Image.open("test_image.jpg")
result = detector.predict(image)

print(f"Verdict: {result['verdict']}")
print(f"Confidence: {result['confidence']}%")
```

### Batch Prediction

```python
import os
from pathlib import Path

def predict_folder(folder_path: str, detector: DeepfakeDetector):
    results = []
    for img_file in Path(folder_path).glob("*.jpg"):
        image = Image.open(img_file)
        result = detector.predict(image)
        result["file"] = img_file.name
        results.append(result)
    return results

results = predict_folder("test_images/", detector)
for r in results:
    print(f"{r['file']}: {r['verdict']} ({r['confidence']}%)")
```

## Model Evaluation

Create `ml/evaluate.py`:

```python
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, confusion_matrix
)
import numpy as np
from tqdm import tqdm

def evaluate_model(model, test_loader, device):
    """Comprehensive model evaluation."""
    model.eval()
    
    all_labels = []
    all_predictions = []
    all_probabilities = []
    
    with torch.no_grad():
        for images, labels in tqdm(test_loader, desc="Evaluating"):
            images = images.to(device)
            outputs = model(images).squeeze().cpu()
            
            all_labels.extend(labels.numpy())
            all_probabilities.extend(outputs.numpy())
            all_predictions.extend((outputs > 0.5).numpy().astype(int))
    
    # Calculate metrics
    metrics = {
        "accuracy": accuracy_score(all_labels, all_predictions),
        "precision": precision_score(all_labels, all_predictions),
        "recall": recall_score(all_labels, all_predictions),
        "f1": f1_score(all_labels, all_predictions),
        "auc_roc": roc_auc_score(all_labels, all_probabilities),
        "confusion_matrix": confusion_matrix(all_labels, all_predictions).tolist()
    }
    
    print("\n=== Evaluation Results ===")
    print(f"Accuracy:  {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall:    {metrics['recall']:.4f}")
    print(f"F1 Score:  {metrics['f1']:.4f}")
    print(f"AUC-ROC:   {metrics['auc_roc']:.4f}")
    print(f"\nConfusion Matrix:")
    print(f"  TN: {metrics['confusion_matrix'][0][0]}, FP: {metrics['confusion_matrix'][0][1]}")
    print(f"  FN: {metrics['confusion_matrix'][1][0]}, TP: {metrics['confusion_matrix'][1][1]}")
    
    return metrics
```

## Performance Optimization

### For CPU (no GPU)

```python
# Use smaller batch size
BATCH_SIZE = 8

# Use fewer workers
NUM_WORKERS = 2

# Use smaller model
MODEL_NAME = "resnet18"  # Instead of efficientnet_b0

# Reduce image size
transforms.Resize((160, 160))  # Instead of 224x224
```

### For GPU

```python
# Enable mixed precision training
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

for images, labels in train_loader:
    with autocast():
        outputs = model(images)
        loss = criterion(outputs, labels)
    
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

## Export Model for Production

```python
# Export to ONNX for faster inference
import torch.onnx

dummy_input = torch.randn(1, 3, 224, 224)
torch.onnx.export(
    model,
    dummy_input,
    "models/deepfake_detector.onnx",
    input_names=["image"],
    output_names=["probability"],
    dynamic_axes={"image": {0: "batch_size"}}
)
```
