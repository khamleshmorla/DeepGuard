# Large-Scale Deepfake Detection ML Training Pipeline

A comprehensive, research-grade ML training system designed to train robust deepfake detection models using hundreds of thousands (lakhs) of free, publicly available samples from Kaggle and academic sources.

## Table of Contents

1. [Core Objectives](#core-objectives)
2. [Dataset Strategy](#dataset-strategy)
3. [Data Infrastructure](#data-infrastructure)
4. [Preprocessing Pipeline](#preprocessing-pipeline)
5. [Data Augmentation](#data-augmentation)
6. [Model Architecture](#model-architecture)
7. [Training Strategy](#training-strategy)
8. [Video-Level Inference](#video-level-inference)
9. [Evaluation Protocol](#evaluation-protocol)
10. [Model Versioning](#model-versioning)
11. [Implementation Files](#implementation-files)

---

## Core Objectives

Build an AI model that:
- ✅ Detects REAL vs FAKE images and videos
- ✅ Outputs probabilistic confidence scores (0-1)
- ✅ Generalizes across different datasets and generators
- ✅ Handles compression, blur, resizing, social-media quality
- ✅ Avoids dataset bias and shortcut learning

### Constraints
- 🚫 Never claim "perfect" or "100% accurate"
- 🚫 Never overfit to a single dataset
- 🚫 Never retrain on user input in real time
- ✅ Aim for robust, explainable, probabilistic output

---

## Dataset Strategy

> **Target: 10+ Lakh (1,000,000+) Samples for Robust Training**

### Tier 1: Primary Datasets (Kaggle - Immediate Access)

| Dataset | Samples | Type | Direct Link |
|---------|---------|------|-------------|
| **FaceForensics++** | **1,800,000+ frames** | Video frames | [Kaggle](https://www.kaggle.com/datasets/sorokin/faceforensics) |
| **Celeb-DF v2** | **590,000+ frames** | Celebrity deepfakes | [Kaggle](https://www.kaggle.com/datasets/reubensuju/celeb-df-v2) |
| **DFDC Full Dataset** | **470,000+ videos** | Facebook Challenge | [Kaggle](https://www.kaggle.com/c/deepfake-detection-challenge/data) |
| **140k Real and Fake Faces** | **140,000 images** | StyleGAN generated | [Kaggle](https://www.kaggle.com/datasets/xhlulu/140k-real-and-fake-faces) |
| **1M Fake Faces** | **1,000,000 images** | GAN-generated | [Kaggle](https://www.kaggle.com/datasets/tunguz/1-million-fake-faces) |
| **Deepfake and Real Images** | **200,000 images** | Mixed sources | [Kaggle](https://www.kaggle.com/datasets/manjilkarki/deepfake-and-real-images) |
| **Real vs Fake Face Detection** | **100,000 images** | Binary classification | [Kaggle](https://www.kaggle.com/datasets/ciplab/real-and-fake-face-detection) |

### Tier 2: Extended Datasets (Academic/Research)

| Dataset | Samples | Description | Access |
|---------|---------|-------------|--------|
| **ForgeryNet** | **2,900,000 images** | Largest forgery dataset | [GitHub](https://github.com/yinan0616/ForgeryNet) |
| **DeeperForensics-1.0** | **60,000 videos** | High-quality deepfakes | [GitHub](https://github.com/EndlessSora/DeeperForensics-1.0) |
| **WildDeepfake** | **7,314 videos** | In-the-wild deepfakes | [GitHub](https://github.com/deepfakeinthewild/deepfake-in-the-wild) |
| **OpenForensics** | **115,000 images** | Multi-face scenarios | [GitHub](https://sites.google.com/view/ltnghia/research/openforensics) |
| **DFGC 2021** | **50,000 videos** | Competition dataset | [GitHub](https://github.com/bomb2peng/DFGC_starterkit) |

### Tier 3: Supplementary GAN Datasets

| Dataset | Samples | Generator | Link |
|---------|---------|-----------|------|
| **StyleGAN2 Faces** | **70,000 images** | StyleGAN2 | [Kaggle](https://www.kaggle.com/datasets/arnaud58/flickrfaceshq-dataset-ffhq) |
| **This Person Does Not Exist** | **100,000+ images** | StyleGAN | Scrape-able |
| **AI Generated Faces** | **50,000 images** | Various GANs | [Kaggle](https://www.kaggle.com/datasets/cashutosh/ai-generated-faces) |
| **GAN Face Database** | **80,000 images** | ProGAN/StyleGAN | [Kaggle](https://www.kaggle.com/datasets/selfishgene/synthetic-faces-high-quality-sfhq-part-1) |

### Tier 4: Real Face Datasets (For Balance)

| Dataset | Samples | Description | Link |
|---------|---------|-------------|------|
| **FFHQ (Flickr-Faces-HQ)** | **70,000 images** | High-quality real faces | [Kaggle](https://www.kaggle.com/datasets/arnaud58/flickrfaceshq-dataset-ffhq) |
| **CelebA** | **200,000 images** | Celebrity faces | [Kaggle](https://www.kaggle.com/datasets/jessicali9530/celeba-dataset) |
| **LFW (Labeled Faces in Wild)** | **13,000 images** | Unconstrained faces | [Kaggle](https://www.kaggle.com/datasets/jessicali9530/lfw-dataset) |
| **VGGFace2** | **3,300,000 images** | Large-scale faces | [Research](https://www.robots.ox.ac.uk/~vgg/data/vgg_face2/) |

---

### Total Sample Count Summary

| Category | Estimated Samples |
|----------|-------------------|
| **Fake Images/Frames** | ~5,500,000 |
| **Real Images/Frames** | ~4,000,000 |
| **Total Available** | **~9,500,000 (95+ Lakhs)** |

---

### Dataset Download Script

```bash
#!/bin/bash
# download_datasets.sh - Automated dataset download from Kaggle

# Prerequisites: pip install kaggle
# Set up: ~/.kaggle/kaggle.json with your API key

# Create directories
mkdir -p data/raw/{faceforensics,celebdf,dfdc,140k_faces,1m_fake,real_faces}

# Download Tier 1 datasets
echo "Downloading FaceForensics++..."
kaggle datasets download -d sorokin/faceforensics -p data/raw/faceforensics --unzip

echo "Downloading Celeb-DF v2..."
kaggle datasets download -d reubensuju/celeb-df-v2 -p data/raw/celebdf --unzip

echo "Downloading 140k Real and Fake Faces..."
kaggle datasets download -d xhlulu/140k-real-and-fake-faces -p data/raw/140k_faces --unzip

echo "Downloading 1M Fake Faces..."
kaggle datasets download -d tunguz/1-million-fake-faces -p data/raw/1m_fake --unzip

echo "Downloading CelebA (Real Faces)..."
kaggle datasets download -d jessicali9530/celeba-dataset -p data/raw/real_faces --unzip

echo "Downloading FFHQ (Real Faces)..."
kaggle datasets download -d arnaud58/flickrfaceshq-dataset-ffhq -p data/raw/real_faces --unzip

echo "All downloads complete!"
```

---

### Dataset Unification Pipeline

```python
# ml/data/unify_datasets.py

import os
import shutil
from pathlib import Path
from tqdm import tqdm
import json
import hashlib

class DatasetUnifier:
    """Unify multiple datasets into a single training structure."""
    
    def __init__(self, output_dir: str = "data/unified"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create structure
        (self.output_dir / "train" / "real").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "train" / "fake").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "val" / "real").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "val" / "fake").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "test" / "real").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "test" / "fake").mkdir(parents=True, exist_ok=True)
        
        self.metadata = {"sources": {}, "statistics": {}}
        self.file_counter = {"real": 0, "fake": 0}
    
    def add_dataset(
        self,
        source_dir: str,
        dataset_name: str,
        real_subdir: str = "real",
        fake_subdir: str = "fake",
        split_ratio: tuple = (0.8, 0.1, 0.1)  # train, val, test
    ):
        """Add a dataset to the unified structure."""
        source = Path(source_dir)
        
        for label in ["real", "fake"]:
            subdir = real_subdir if label == "real" else fake_subdir
            label_dir = source / subdir
            
            if not label_dir.exists():
                print(f"Warning: {label_dir} not found, skipping...")
                continue
            
            files = list(label_dir.glob("*.jpg")) + \
                    list(label_dir.glob("*.jpeg")) + \
                    list(label_dir.glob("*.png"))
            
            print(f"Processing {len(files)} {label} files from {dataset_name}...")
            
            # Shuffle and split
            import random
            random.shuffle(files)
            
            n_train = int(len(files) * split_ratio[0])
            n_val = int(len(files) * split_ratio[1])
            
            splits = {
                "train": files[:n_train],
                "val": files[n_train:n_train + n_val],
                "test": files[n_train + n_val:]
            }
            
            for split_name, split_files in splits.items():
                for f in tqdm(split_files, desc=f"{split_name}/{label}"):
                    self._copy_file(f, split_name, label, dataset_name)
    
    def _copy_file(self, src: Path, split: str, label: str, source_name: str):
        """Copy file with unique naming."""
        self.file_counter[label] += 1
        new_name = f"{source_name}_{label}_{self.file_counter[label]:08d}{src.suffix}"
        dst = self.output_dir / split / label / new_name
        shutil.copy2(src, dst)
        
        # Track metadata
        file_hash = hashlib.md5(dst.read_bytes()).hexdigest()[:8]
        self.metadata["sources"][new_name] = {
            "original": str(src),
            "source_dataset": source_name,
            "hash": file_hash
        }
    
    def save_metadata(self):
        """Save dataset metadata."""
        # Count statistics
        for split in ["train", "val", "test"]:
            self.metadata["statistics"][split] = {
                "real": len(list((self.output_dir / split / "real").glob("*"))),
                "fake": len(list((self.output_dir / split / "fake").glob("*")))
            }
        
        with open(self.output_dir / "metadata.json", "w") as f:
            json.dump(self.metadata, f, indent=2)
        
        print("\n=== Dataset Statistics ===")
        total = 0
        for split, counts in self.metadata["statistics"].items():
            split_total = counts["real"] + counts["fake"]
            total += split_total
            print(f"{split}: {counts['real']:,} real + {counts['fake']:,} fake = {split_total:,}")
        print(f"Total: {total:,} samples")


# Usage example
if __name__ == "__main__":
    unifier = DatasetUnifier("data/unified")
    
    # Add datasets
    unifier.add_dataset("data/raw/140k_faces", "140k", "real", "fake")
    unifier.add_dataset("data/raw/faceforensics", "ff++", "original", "manipulated")
    unifier.add_dataset("data/raw/celebdf", "celebdf", "Celeb-real", "Celeb-synthesis")
    unifier.add_dataset("data/raw/real_faces/celeba", "celeba", "img_align_celeba", None)
    
    unifier.save_metadata()
```

---

### Label Encoding
- **REAL = 0** (authentic content)
- **FAKE = 1** (AI-generated/manipulated)

### Source Tracking

```json
{
  "ff++_real_00000001.jpg": {
    "original": "data/raw/faceforensics/original/000_003/frame_045.jpg",
    "source_dataset": "ff++",
    "hash": "a1b2c3d4"
  },
  "140k_fake_00000001.jpg": {
    "original": "data/raw/140k_faces/fake/stylegan_001234.jpg",
    "source_dataset": "140k",
    "hash": "e5f6g7h8"
  }
}
```

---

## Data Infrastructure

### Large-Scale Data Handling (Lakhs of Files)

#### Streaming Data Loading

```python
# ml/data/streaming_dataset.py

import torch
from torch.utils.data import IterableDataset, DataLoader
import os
from pathlib import Path
from PIL import Image
import json
from typing import Generator, Tuple
import hashlib

class StreamingDeepfakeDataset(IterableDataset):
    """
    Memory-efficient streaming dataset for handling lakhs of images.
    Uses lazy loading and sharding for distributed training.
    """
    
    def __init__(
        self,
        data_dir: str,
        transform=None,
        shard_id: int = 0,
        num_shards: int = 1,
        shuffle_buffer_size: int = 10000,
        skip_corrupted: bool = True
    ):
        self.data_dir = Path(data_dir)
        self.transform = transform
        self.shard_id = shard_id
        self.num_shards = num_shards
        self.shuffle_buffer_size = shuffle_buffer_size
        self.skip_corrupted = skip_corrupted
        
        # Build file index lazily
        self.index_file = self.data_dir / ".file_index.json"
        self._file_list = None
        
    @property
    def file_list(self) -> list:
        if self._file_list is None:
            self._file_list = self._build_or_load_index()
        return self._file_list
    
    def _build_or_load_index(self) -> list:
        """Build or load file index for efficient access."""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                return json.load(f)
        
        print(f"Building file index for {self.data_dir}...")
        files = []
        
        for label, class_name in [(0, 'real'), (1, 'fake')]:
            class_dir = self.data_dir / class_name
            if not class_dir.exists():
                continue
                
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
                for file_path in class_dir.glob(ext):
                    files.append({
                        'path': str(file_path.relative_to(self.data_dir)),
                        'label': label
                    })
        
        # Save index
        with open(self.index_file, 'w') as f:
            json.dump(files, f)
        
        print(f"Indexed {len(files)} files")
        return files
    
    def _shard_files(self) -> list:
        """Get files for this shard."""
        total = len(self.file_list)
        per_shard = total // self.num_shards
        start = self.shard_id * per_shard
        end = start + per_shard if self.shard_id < self.num_shards - 1 else total
        return self.file_list[start:end]
    
    def _load_image(self, file_info: dict) -> Tuple[Image.Image, int]:
        """Load and validate an image."""
        path = self.data_dir / file_info['path']
        try:
            image = Image.open(path).convert('RGB')
            return image, file_info['label']
        except Exception as e:
            if self.skip_corrupted:
                print(f"Skipping corrupted file: {path} - {e}")
                return None, None
            raise
    
    def __iter__(self) -> Generator:
        import random
        
        files = self._shard_files()
        random.shuffle(files)
        
        buffer = []
        
        for file_info in files:
            result = self._load_image(file_info)
            if result[0] is None:
                continue
            
            image, label = result
            if self.transform:
                image = self.transform(image)
            
            buffer.append((image, label))
            
            # Shuffle buffer when full
            if len(buffer) >= self.shuffle_buffer_size:
                random.shuffle(buffer)
                while len(buffer) > self.shuffle_buffer_size // 2:
                    yield buffer.pop()
        
        # Yield remaining items
        random.shuffle(buffer)
        for item in buffer:
            yield item
    
    def __len__(self):
        return len(self.file_list) // self.num_shards


def create_streaming_dataloader(
    data_dir: str,
    batch_size: int = 32,
    num_workers: int = 4,
    transform=None,
    **kwargs
) -> DataLoader:
    """Create an efficient streaming dataloader."""
    dataset = StreamingDeepfakeDataset(
        data_dir=data_dir,
        transform=transform,
        **kwargs
    )
    
    return DataLoader(
        dataset,
        batch_size=batch_size,
        num_workers=num_workers,
        pin_memory=True,
        prefetch_factor=2
    )
```

#### Dataset Sharding for Distributed Training

```python
# ml/data/sharding.py

import os
import json
from pathlib import Path
from typing import List, Dict
import hashlib

class DatasetShardManager:
    """Manage dataset sharding for large-scale distributed training."""
    
    def __init__(self, data_dir: str, num_shards: int = 8):
        self.data_dir = Path(data_dir)
        self.num_shards = num_shards
        self.shard_dir = self.data_dir / "shards"
        
    def create_shards(self):
        """Create balanced shards from the dataset."""
        self.shard_dir.mkdir(exist_ok=True)
        
        # Collect all files
        real_files = list((self.data_dir / "real").glob("*.*"))
        fake_files = list((self.data_dir / "fake").glob("*.*"))
        
        print(f"Total: {len(real_files)} real, {len(fake_files)} fake")
        
        # Create balanced shards
        for shard_id in range(self.num_shards):
            shard_manifest = {
                "shard_id": shard_id,
                "files": []
            }
            
            # Distribute files
            for files, label in [(real_files, 0), (fake_files, 1)]:
                per_shard = len(files) // self.num_shards
                start = shard_id * per_shard
                end = start + per_shard if shard_id < self.num_shards - 1 else len(files)
                
                for f in files[start:end]:
                    shard_manifest["files"].append({
                        "path": str(f.relative_to(self.data_dir)),
                        "label": label
                    })
            
            # Save manifest
            manifest_path = self.shard_dir / f"shard_{shard_id:03d}.json"
            with open(manifest_path, 'w') as f:
                json.dump(shard_manifest, f)
            
            print(f"Shard {shard_id}: {len(shard_manifest['files'])} files")
    
    def load_shard(self, shard_id: int) -> List[Dict]:
        """Load a specific shard."""
        manifest_path = self.shard_dir / f"shard_{shard_id:03d}.json"
        with open(manifest_path, 'r') as f:
            return json.load(f)["files"]
```

#### Automatic Corruption Detection

```python
# ml/data/quality_check.py

from PIL import Image
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def check_image_integrity(file_path: Path) -> dict:
    """Check if an image file is valid and uncorrupted."""
    try:
        with Image.open(file_path) as img:
            img.verify()
        
        # Re-open to get properties (verify() leaves file in unusable state)
        with Image.open(file_path) as img:
            width, height = img.size
            mode = img.mode
        
        return {
            "path": str(file_path),
            "valid": True,
            "width": width,
            "height": height,
            "mode": mode
        }
    except Exception as e:
        return {
            "path": str(file_path),
            "valid": False,
            "error": str(e)
        }

def validate_dataset(data_dir: str, num_workers: int = 8) -> dict:
    """Validate all images in a dataset directory."""
    data_path = Path(data_dir)
    all_files = list(data_path.rglob("*.jpg")) + \
                list(data_path.rglob("*.jpeg")) + \
                list(data_path.rglob("*.png"))
    
    print(f"Validating {len(all_files)} files...")
    
    results = {"valid": [], "invalid": []}
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(check_image_integrity, f): f for f in all_files}
        
        for future in tqdm(as_completed(futures), total=len(futures)):
            result = future.result()
            if result["valid"]:
                results["valid"].append(result)
            else:
                results["invalid"].append(result)
    
    # Save report
    report_path = data_path / "validation_report.json"
    with open(report_path, 'w') as f:
        json.dump({
            "total_files": len(all_files),
            "valid_count": len(results["valid"]),
            "invalid_count": len(results["invalid"]),
            "invalid_files": results["invalid"]
        }, f, indent=2)
    
    print(f"Valid: {len(results['valid'])}, Invalid: {len(results['invalid'])}")
    print(f"Report saved to {report_path}")
    
    return results
```

---

## Preprocessing Pipeline

### Face Detection & Cropping

```python
# ml/preprocessing/face_detection.py

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
import mediapipe as mp
from PIL import Image

class FaceDetector:
    """Multi-backend face detector with quality filtering."""
    
    def __init__(self, backend: str = "mediapipe", min_confidence: float = 0.7):
        self.backend = backend
        self.min_confidence = min_confidence
        
        if backend == "mediapipe":
            self.mp_face = mp.solutions.face_detection
            self.detector = self.mp_face.FaceDetection(
                model_selection=1,  # Full range model
                min_detection_confidence=min_confidence
            )
        elif backend == "opencv":
            self.cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
        elif backend == "retinaface":
            # Requires: pip install retinaface
            from retinaface import RetinaFace
            self.detector = RetinaFace
    
    def detect_faces(self, image: np.ndarray) -> List[dict]:
        """Detect faces in an image."""
        if self.backend == "mediapipe":
            return self._detect_mediapipe(image)
        elif self.backend == "opencv":
            return self._detect_opencv(image)
        elif self.backend == "retinaface":
            return self._detect_retinaface(image)
    
    def _detect_mediapipe(self, image: np.ndarray) -> List[dict]:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.detector.process(rgb)
        
        if not results.detections:
            return []
        
        h, w = image.shape[:2]
        faces = []
        
        for detection in results.detections:
            bbox = detection.location_data.relative_bounding_box
            faces.append({
                'bbox': (
                    int(bbox.xmin * w),
                    int(bbox.ymin * h),
                    int(bbox.width * w),
                    int(bbox.height * h)
                ),
                'confidence': detection.score[0]
            })
        
        return faces
    
    def _detect_opencv(self, image: np.ndarray) -> List[dict]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.cascade.detectMultiScale(gray, 1.1, 4)
        
        return [{'bbox': tuple(face), 'confidence': 0.8} for face in faces]
    
    def _detect_retinaface(self, image: np.ndarray) -> List[dict]:
        results = self.detector.detect_faces(image)
        
        faces = []
        for key, face in results.items():
            box = face['facial_area']
            faces.append({
                'bbox': (box[0], box[1], box[2] - box[0], box[3] - box[1]),
                'confidence': face['score']
            })
        
        return faces
    
    def crop_face(
        self,
        image: np.ndarray,
        bbox: Tuple[int, int, int, int],
        margin: float = 0.3,
        target_size: Tuple[int, int] = (224, 224)
    ) -> np.ndarray:
        """Crop face with margin and resize."""
        h, w = image.shape[:2]
        x, y, fw, fh = bbox
        
        # Add margin
        margin_x = int(fw * margin)
        margin_y = int(fh * margin)
        
        x1 = max(0, x - margin_x)
        y1 = max(0, y - margin_y)
        x2 = min(w, x + fw + margin_x)
        y2 = min(h, y + fh + margin_y)
        
        # Crop and resize
        face = image[y1:y2, x1:x2]
        face = cv2.resize(face, target_size)
        
        return face


class QualityFilter:
    """Filter out low-quality face crops."""
    
    def __init__(
        self,
        min_size: int = 64,
        blur_threshold: float = 100.0,
        min_brightness: float = 30.0,
        max_brightness: float = 220.0
    ):
        self.min_size = min_size
        self.blur_threshold = blur_threshold
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness
    
    def is_quality_face(self, face: np.ndarray) -> Tuple[bool, dict]:
        """Check if face crop meets quality standards."""
        h, w = face.shape[:2]
        
        # Size check
        if min(h, w) < self.min_size:
            return False, {"reason": "too_small"}
        
        # Blur detection (Laplacian variance)
        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        if blur_score < self.blur_threshold:
            return False, {"reason": "too_blurry", "blur_score": blur_score}
        
        # Brightness check
        brightness = np.mean(gray)
        
        if brightness < self.min_brightness:
            return False, {"reason": "too_dark", "brightness": brightness}
        if brightness > self.max_brightness:
            return False, {"reason": "too_bright", "brightness": brightness}
        
        return True, {
            "blur_score": blur_score,
            "brightness": brightness
        }
```

### Video Frame Sampling

```python
# ml/preprocessing/video_sampler.py

import cv2
import numpy as np
from pathlib import Path
from typing import List, Generator
import hashlib

class IntelligentFrameSampler:
    """
    Intelligent video frame sampling with temporal coverage
    and quality-aware selection.
    """
    
    def __init__(
        self,
        max_frames: int = 40,
        min_scene_change: float = 0.3,
        quality_threshold: float = 100.0
    ):
        self.max_frames = max_frames
        self.min_scene_change = min_scene_change
        self.quality_threshold = quality_threshold
    
    def sample_video(self, video_path: str) -> Generator[np.ndarray, None, None]:
        """Sample frames with temporal distribution and quality filtering."""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        if total_frames == 0:
            cap.release()
            return
        
        # Calculate frame indices for even temporal distribution
        if total_frames <= self.max_frames:
            frame_indices = list(range(total_frames))
        else:
            # Ensure start, middle, end coverage
            frame_indices = self._get_temporal_indices(total_frames)
        
        prev_frame = None
        sampled_count = 0
        
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            
            if not ret:
                continue
            
            # Quality check
            if not self._is_quality_frame(frame):
                continue
            
            # Scene change detection (avoid similar frames)
            if prev_frame is not None:
                if not self._is_scene_change(prev_frame, frame):
                    continue
            
            prev_frame = frame.copy()
            sampled_count += 1
            
            yield frame
            
            if sampled_count >= self.max_frames:
                break
        
        cap.release()
    
    def _get_temporal_indices(self, total: int) -> List[int]:
        """Get frame indices with temporal coverage."""
        indices = []
        
        # Divide into segments
        segment_size = total // self.max_frames
        
        for i in range(self.max_frames):
            start = i * segment_size
            # Pick middle of each segment
            idx = start + segment_size // 2
            indices.append(min(idx, total - 1))
        
        return indices
    
    def _is_quality_frame(self, frame: np.ndarray) -> bool:
        """Check frame quality."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        return blur_score >= self.quality_threshold
    
    def _is_scene_change(self, prev: np.ndarray, curr: np.ndarray) -> bool:
        """Detect if there's significant change between frames."""
        prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY)
        
        diff = cv2.absdiff(prev_gray, curr_gray)
        change_ratio = np.mean(diff) / 255.0
        
        return change_ratio >= self.min_scene_change


def extract_and_save_frames(
    video_dir: str,
    output_dir: str,
    frames_per_video: int = 25,
    label: int = 0
) -> dict:
    """Extract frames from all videos in a directory."""
    video_path = Path(video_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    sampler = IntelligentFrameSampler(max_frames=frames_per_video)
    stats = {"videos": 0, "frames": 0, "errors": []}
    
    for video_file in video_path.glob("*"):
        if video_file.suffix.lower() not in ['.mp4', '.avi', '.mov', '.webm']:
            continue
        
        try:
            video_hash = hashlib.md5(video_file.stem.encode()).hexdigest()[:8]
            
            for i, frame in enumerate(sampler.sample_video(str(video_file))):
                output_name = f"{video_hash}_frame{i:03d}.jpg"
                cv2.imwrite(str(output_path / output_name), frame)
                stats["frames"] += 1
            
            stats["videos"] += 1
            
        except Exception as e:
            stats["errors"].append({"file": str(video_file), "error": str(e)})
    
    return stats
```

---

## Data Augmentation

### Realistic Augmentation Pipeline

```python
# ml/augmentation/transforms.py

import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2
import numpy as np

def get_training_transforms(image_size: int = 224) -> A.Compose:
    """
    Realistic augmentations simulating social media artifacts.
    These help the model generalize to real-world compressed media.
    """
    return A.Compose([
        # Resize with various interpolation methods
        A.OneOf([
            A.Resize(image_size, image_size, interpolation=cv2.INTER_LINEAR),
            A.Resize(image_size, image_size, interpolation=cv2.INTER_CUBIC),
            A.Resize(image_size, image_size, interpolation=cv2.INTER_LANCZOS4),
        ], p=1.0),
        
        # Geometric transforms
        A.HorizontalFlip(p=0.5),
        A.ShiftScaleRotate(
            shift_limit=0.1,
            scale_limit=0.15,
            rotate_limit=15,
            border_mode=cv2.BORDER_REFLECT,
            p=0.5
        ),
        
        # Compression artifacts (CRITICAL for social media)
        A.OneOf([
            A.ImageCompression(quality_lower=20, quality_upper=80, p=1.0),
            A.Downscale(scale_min=0.25, scale_max=0.5, p=1.0),
        ], p=0.6),
        
        # Blur (motion, gaussian, median)
        A.OneOf([
            A.GaussianBlur(blur_limit=(3, 7), p=1.0),
            A.MotionBlur(blur_limit=(3, 7), p=1.0),
            A.MedianBlur(blur_limit=5, p=1.0),
        ], p=0.4),
        
        # Noise
        A.OneOf([
            A.GaussNoise(var_limit=(10, 50), p=1.0),
            A.ISONoise(color_shift=(0.01, 0.05), intensity=(0.1, 0.5), p=1.0),
        ], p=0.3),
        
        # Color/brightness adjustments
        A.OneOf([
            A.RandomBrightnessContrast(
                brightness_limit=0.2,
                contrast_limit=0.2,
                p=1.0
            ),
            A.HueSaturationValue(
                hue_shift_limit=10,
                sat_shift_limit=20,
                val_shift_limit=20,
                p=1.0
            ),
            A.RGBShift(r_shift_limit=15, g_shift_limit=15, b_shift_limit=15, p=1.0),
        ], p=0.5),
        
        # Random crop and pad
        A.RandomResizedCrop(
            height=image_size,
            width=image_size,
            scale=(0.8, 1.0),
            ratio=(0.9, 1.1),
            p=0.3
        ),
        
        # Normalize for ImageNet pretrained models
        A.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
        
        ToTensorV2()
    ])


def get_validation_transforms(image_size: int = 224) -> A.Compose:
    """Validation/test transforms - minimal processing."""
    return A.Compose([
        A.Resize(image_size, image_size),
        A.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
        ToTensorV2()
    ])


def get_tta_transforms(image_size: int = 224) -> list:
    """Test-time augmentation transforms."""
    base = A.Compose([
        A.Resize(image_size, image_size),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ToTensorV2()
    ])
    
    return [
        base,
        A.Compose([A.HorizontalFlip(p=1.0), *base.transforms]),
        A.Compose([
            A.Resize(int(image_size * 1.1), int(image_size * 1.1)),
            A.CenterCrop(image_size, image_size),
            *base.transforms[-2:]
        ]),
    ]
```

---

## Model Architecture

### Modern Backbone Options

```python
# ml/models/backbones.py

import torch
import torch.nn as nn
import timm
from typing import Optional, Tuple

class DeepfakeDetector(nn.Module):
    """
    Flexible deepfake detector supporting multiple modern backbones.
    
    Supported backbones:
    - DINOv2 (preferred for self-supervised features)
    - EfficientNet-V2
    - ConvNeXt
    - Vision Transformer (ViT)
    """
    
    def __init__(
        self,
        backbone: str = "dinov2_vits14",
        pretrained: bool = True,
        freeze_backbone: bool = True,
        dropout: float = 0.3
    ):
        super().__init__()
        
        self.backbone_name = backbone
        self.freeze_backbone = freeze_backbone
        
        # Create backbone
        if backbone.startswith("dinov2"):
            self.backbone, self.num_features = self._create_dinov2(backbone, pretrained)
        elif backbone.startswith("efficientnet"):
            self.backbone, self.num_features = self._create_efficientnet(backbone, pretrained)
        elif backbone.startswith("convnext"):
            self.backbone, self.num_features = self._create_convnext(backbone, pretrained)
        elif backbone.startswith("vit"):
            self.backbone, self.num_features = self._create_vit(backbone, pretrained)
        else:
            raise ValueError(f"Unknown backbone: {backbone}")
        
        # Freeze backbone if requested
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False
        
        # Forensic classification head
        self.classifier = nn.Sequential(
            nn.LayerNorm(self.num_features),
            nn.Dropout(dropout),
            nn.Linear(self.num_features, 512),
            nn.GELU(),
            nn.Dropout(dropout / 2),
            nn.Linear(512, 128),
            nn.GELU(),
            nn.Linear(128, 1)
        )
    
    def _create_dinov2(self, name: str, pretrained: bool) -> Tuple[nn.Module, int]:
        """Create DINOv2 backbone."""
        model = torch.hub.load('facebookresearch/dinov2', name)
        # DINOv2 output dimensions by model size
        dims = {
            "dinov2_vits14": 384,
            "dinov2_vitb14": 768,
            "dinov2_vitl14": 1024,
            "dinov2_vitg14": 1536
        }
        return model, dims.get(name, 384)
    
    def _create_efficientnet(self, name: str, pretrained: bool) -> Tuple[nn.Module, int]:
        """Create EfficientNet-V2 backbone."""
        model = timm.create_model(
            name,
            pretrained=pretrained,
            num_classes=0  # Remove classifier
        )
        num_features = model.num_features
        return model, num_features
    
    def _create_convnext(self, name: str, pretrained: bool) -> Tuple[nn.Module, int]:
        """Create ConvNeXt backbone."""
        model = timm.create_model(
            name,
            pretrained=pretrained,
            num_classes=0
        )
        return model, model.num_features
    
    def _create_vit(self, name: str, pretrained: bool) -> Tuple[nn.Module, int]:
        """Create Vision Transformer backbone."""
        model = timm.create_model(
            name,
            pretrained=pretrained,
            num_classes=0
        )
        return model, model.num_features
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.backbone(x)
        logits = self.classifier(features)
        return logits
    
    def unfreeze_top_layers(self, num_layers: int = 4):
        """Unfreeze top N layers for fine-tuning."""
        if hasattr(self.backbone, 'blocks'):
            # Transformer-based
            for block in self.backbone.blocks[-num_layers:]:
                for param in block.parameters():
                    param.requires_grad = True
        elif hasattr(self.backbone, 'stages'):
            # ConvNeXt/EfficientNet
            for stage in list(self.backbone.stages)[-num_layers:]:
                for param in stage.parameters():
                    param.requires_grad = True
    
    def predict_proba(self, x: torch.Tensor) -> torch.Tensor:
        """Return probability of FAKE."""
        with torch.no_grad():
            logits = self.forward(x)
            return torch.sigmoid(logits)


def get_model(
    backbone: str = "efficientnetv2_s",
    pretrained: bool = True,
    **kwargs
) -> DeepfakeDetector:
    """Factory function to create detector."""
    return DeepfakeDetector(
        backbone=backbone,
        pretrained=pretrained,
        **kwargs
    )
```

---

## Training Strategy

### Large-Scale Training Script

```python
# ml/training/trainer.py

import torch
import torch.nn as nn
import torch.optim as optim
from torch.cuda.amp import GradScaler, autocast
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from tqdm import tqdm
import json
import logging

from ml.models.backbones import DeepfakeDetector
from ml.data.streaming_dataset import create_streaming_dataloader
from ml.augmentation.transforms import get_training_transforms, get_validation_transforms

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LargeScaleTrainer:
    """
    Production-grade trainer for large-scale deepfake detection.
    
    Features:
    - Mixed precision training (AMP)
    - Gradient accumulation for large effective batch sizes
    - Cosine annealing with warm restarts
    - Class-weighted loss for imbalanced data
    - Automatic checkpointing
    - Training phases (frozen → partial → full)
    """
    
    def __init__(
        self,
        model: DeepfakeDetector,
        train_dir: str,
        val_dir: str,
        output_dir: str = "outputs",
        batch_size: int = 32,
        accumulation_steps: int = 4,
        learning_rate: float = 1e-4,
        weight_decay: float = 0.01,
        num_epochs: int = 30,
        warmup_epochs: int = 2,
        image_size: int = 224,
        num_workers: int = 8,
        class_weights: Optional[torch.Tensor] = None,
        early_stopping_patience: int = 7,
        use_amp: bool = True,
        device: str = "cuda"
    ):
        self.model = model.to(device)
        self.device = device
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.batch_size = batch_size
        self.accumulation_steps = accumulation_steps
        self.effective_batch_size = batch_size * accumulation_steps
        self.num_epochs = num_epochs
        self.use_amp = use_amp
        self.early_stopping_patience = early_stopping_patience
        
        # Data loaders
        self.train_loader = create_streaming_dataloader(
            train_dir,
            batch_size=batch_size,
            num_workers=num_workers,
            transform=get_training_transforms(image_size)
        )
        self.val_loader = create_streaming_dataloader(
            val_dir,
            batch_size=batch_size,
            num_workers=num_workers,
            transform=get_validation_transforms(image_size)
        )
        
        # Loss function with class weights
        if class_weights is not None:
            pos_weight = class_weights[1] / class_weights[0]
            self.criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
        else:
            self.criterion = nn.BCEWithLogitsLoss()
        
        # Optimizer
        self.optimizer = optim.AdamW(
            filter(lambda p: p.requires_grad, model.parameters()),
            lr=learning_rate,
            weight_decay=weight_decay
        )
        
        # Scheduler with warm restarts
        self.scheduler = CosineAnnealingWarmRestarts(
            self.optimizer,
            T_0=5,  # Restart every 5 epochs
            T_mult=2,  # Double period after each restart
            eta_min=learning_rate * 0.01
        )
        
        # Mixed precision
        self.scaler = GradScaler() if use_amp else None
        
        # Training state
        self.current_epoch = 0
        self.best_val_auc = 0.0
        self.epochs_without_improvement = 0
        self.history = {
            "train_loss": [], "val_loss": [],
            "train_acc": [], "val_acc": [],
            "val_auc": [], "learning_rates": []
        }
    
    def train_epoch(self) -> Dict[str, float]:
        """Train for one epoch with gradient accumulation."""
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        self.optimizer.zero_grad()
        
        pbar = tqdm(self.train_loader, desc=f"Epoch {self.current_epoch + 1}")
        
        for batch_idx, (images, labels) in enumerate(pbar):
            images = images.to(self.device)
            labels = labels.float().to(self.device)
            
            # Forward pass with mixed precision
            with autocast(enabled=self.use_amp):
                outputs = self.model(images).squeeze()
                loss = self.criterion(outputs, labels)
                loss = loss / self.accumulation_steps
            
            # Backward pass
            if self.use_amp:
                self.scaler.scale(loss).backward()
            else:
                loss.backward()
            
            # Update weights every accumulation_steps
            if (batch_idx + 1) % self.accumulation_steps == 0:
                if self.use_amp:
                    self.scaler.unscale_(self.optimizer)
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                else:
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                    self.optimizer.step()
                
                self.optimizer.zero_grad()
            
            # Metrics
            total_loss += loss.item() * self.accumulation_steps
            predictions = (torch.sigmoid(outputs) > 0.5).float()
            correct += (predictions == labels).sum().item()
            total += labels.size(0)
            
            pbar.set_postfix({
                "loss": f"{loss.item() * self.accumulation_steps:.4f}",
                "acc": f"{correct / total:.4f}"
            })
        
        return {
            "loss": total_loss / len(self.train_loader),
            "accuracy": correct / total
        }
    
    @torch.no_grad()
    def validate(self) -> Dict[str, float]:
        """Validate the model."""
        self.model.eval()
        total_loss = 0.0
        all_labels = []
        all_probs = []
        
        for images, labels in tqdm(self.val_loader, desc="Validating"):
            images = images.to(self.device)
            labels = labels.float().to(self.device)
            
            outputs = self.model(images).squeeze()
            loss = self.criterion(outputs, labels)
            
            total_loss += loss.item()
            probs = torch.sigmoid(outputs)
            
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
        
        all_labels = np.array(all_labels)
        all_probs = np.array(all_probs)
        
        # Calculate metrics
        from sklearn.metrics import accuracy_score, roc_auc_score
        
        predictions = (all_probs > 0.5).astype(int)
        accuracy = accuracy_score(all_labels, predictions)
        
        try:
            auc = roc_auc_score(all_labels, all_probs)
        except ValueError:
            auc = 0.5
        
        return {
            "loss": total_loss / len(self.val_loader),
            "accuracy": accuracy,
            "auc": auc
        }
    
    def train(self, training_phases: list = None):
        """
        Full training loop with optional phased training.
        
        Phases:
        1. Train head only (backbone frozen)
        2. Unfreeze top layers, train at lower LR
        3. Full fine-tuning at very low LR
        """
        if training_phases is None:
            training_phases = [
                {"epochs": 10, "unfreeze": 0, "lr_mult": 1.0},
                {"epochs": 10, "unfreeze": 4, "lr_mult": 0.1},
                {"epochs": 10, "unfreeze": -1, "lr_mult": 0.01}  # -1 = all
            ]
        
        total_epochs = sum(p["epochs"] for p in training_phases)
        
        for phase_idx, phase in enumerate(training_phases):
            logger.info(f"\n{'='*50}")
            logger.info(f"Phase {phase_idx + 1}/{len(training_phases)}")
            logger.info(f"Epochs: {phase['epochs']}, Unfreeze: {phase['unfreeze']}")
            logger.info(f"{'='*50}\n")
            
            # Adjust model freezing
            if phase["unfreeze"] == -1:
                for param in self.model.parameters():
                    param.requires_grad = True
            elif phase["unfreeze"] > 0:
                self.model.unfreeze_top_layers(phase["unfreeze"])
            
            # Adjust learning rate
            for pg in self.optimizer.param_groups:
                pg["lr"] = pg["lr"] * phase["lr_mult"]
            
            # Train for this phase
            for epoch in range(phase["epochs"]):
                self.current_epoch += 1
                
                train_metrics = self.train_epoch()
                val_metrics = self.validate()
                
                # Update scheduler
                self.scheduler.step()
                current_lr = self.optimizer.param_groups[0]["lr"]
                
                # Log metrics
                self.history["train_loss"].append(train_metrics["loss"])
                self.history["train_acc"].append(train_metrics["accuracy"])
                self.history["val_loss"].append(val_metrics["loss"])
                self.history["val_acc"].append(val_metrics["accuracy"])
                self.history["val_auc"].append(val_metrics["auc"])
                self.history["learning_rates"].append(current_lr)
                
                logger.info(
                    f"Epoch {self.current_epoch}/{total_epochs} | "
                    f"Train Loss: {train_metrics['loss']:.4f} | "
                    f"Val Loss: {val_metrics['loss']:.4f} | "
                    f"Val AUC: {val_metrics['auc']:.4f} | "
                    f"LR: {current_lr:.2e}"
                )
                
                # Save best model
                if val_metrics["auc"] > self.best_val_auc:
                    self.best_val_auc = val_metrics["auc"]
                    self.epochs_without_improvement = 0
                    self.save_checkpoint("best_model.pth")
                    logger.info(f"✓ New best model saved (AUC: {self.best_val_auc:.4f})")
                else:
                    self.epochs_without_improvement += 1
                
                # Early stopping
                if self.epochs_without_improvement >= self.early_stopping_patience:
                    logger.info(f"Early stopping after {self.current_epoch} epochs")
                    break
        
        # Save final model and history
        self.save_checkpoint("final_model.pth")
        self.save_history()
        
        return self.best_val_auc
    
    def save_checkpoint(self, filename: str):
        """Save model checkpoint."""
        torch.save({
            "epoch": self.current_epoch,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "scheduler_state_dict": self.scheduler.state_dict(),
            "best_val_auc": self.best_val_auc,
            "history": self.history
        }, self.output_dir / filename)
    
    def save_history(self):
        """Save training history."""
        with open(self.output_dir / "training_history.json", "w") as f:
            json.dump(self.history, f, indent=2)


def train_deepfake_model(
    train_dir: str,
    val_dir: str,
    backbone: str = "efficientnetv2_s",
    output_dir: str = "outputs",
    **kwargs
) -> float:
    """Main training entry point."""
    
    logger.info(f"Initializing model with backbone: {backbone}")
    model = DeepfakeDetector(backbone=backbone, freeze_backbone=True)
    
    trainer = LargeScaleTrainer(
        model=model,
        train_dir=train_dir,
        val_dir=val_dir,
        output_dir=output_dir,
        **kwargs
    )
    
    best_auc = trainer.train()
    logger.info(f"\nTraining complete! Best AUC: {best_auc:.4f}")
    
    return best_auc
```

---

## Video-Level Inference

### Frame Aggregation Strategy

```python
# ml/inference/video_inference.py

import torch
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
import cv2

from ml.models.backbones import DeepfakeDetector
from ml.preprocessing.video_sampler import IntelligentFrameSampler
from ml.augmentation.transforms import get_validation_transforms

@dataclass
class VideoVerdict:
    """Video-level deepfake detection result."""
    label: str  # "REAL" or "FAKE"
    confidence: float  # 0-1 probability
    per_frame_scores: List[float]
    frame_count: int
    uncertainty: float
    recommendation: str


class VideoForensicAnalyzer:
    """
    Video-level deepfake detection with intelligent frame aggregation.
    
    Uses mean probability with confidence smoothing, NOT majority vote.
    """
    
    def __init__(
        self,
        model: DeepfakeDetector,
        device: str = "cuda",
        max_frames: int = 40,
        batch_size: int = 16,
        uncertainty_threshold: float = 0.15
    ):
        self.model = model.to(device)
        self.model.eval()
        self.device = device
        self.max_frames = max_frames
        self.batch_size = batch_size
        self.uncertainty_threshold = uncertainty_threshold
        
        self.sampler = IntelligentFrameSampler(max_frames=max_frames)
        self.transform = get_validation_transforms()
    
    @torch.no_grad()
    def analyze_video(self, video_path: str) -> VideoVerdict:
        """Analyze a video for deepfake detection."""
        
        # Sample frames
        frames = list(self.sampler.sample_video(video_path))
        
        if len(frames) == 0:
            return VideoVerdict(
                label="UNKNOWN",
                confidence=0.0,
                per_frame_scores=[],
                frame_count=0,
                uncertainty=1.0,
                recommendation="Video could not be processed"
            )
        
        # Process frames in batches
        all_probs = []
        
        for i in range(0, len(frames), self.batch_size):
            batch_frames = frames[i:i + self.batch_size]
            
            # Transform and stack
            batch_tensors = []
            for frame in batch_frames:
                # Convert BGR to RGB
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                transformed = self.transform(image=rgb)["image"]
                batch_tensors.append(transformed)
            
            batch = torch.stack(batch_tensors).to(self.device)
            
            # Get predictions
            logits = self.model(batch).squeeze()
            probs = torch.sigmoid(logits).cpu().numpy()
            
            if probs.ndim == 0:
                probs = [probs.item()]
            
            all_probs.extend(probs)
        
        # Aggregate predictions
        return self._aggregate_predictions(all_probs)
    
    def _aggregate_predictions(self, probs: List[float]) -> VideoVerdict:
        """
        Aggregate frame-level predictions to video-level verdict.
        Uses mean with confidence smoothing.
        """
        probs = np.array(probs)
        
        # Mean probability (NOT majority vote)
        mean_prob = np.mean(probs)
        
        # Uncertainty estimation
        std_prob = np.std(probs)
        confidence_range = np.max(probs) - np.min(probs)
        uncertainty = (std_prob + confidence_range / 2) / 2
        
        # Confidence smoothing: reduce confidence if uncertainty is high
        if uncertainty > self.uncertainty_threshold:
            # Pull towards 0.5 when uncertain
            smoothing_factor = min(uncertainty / 0.5, 0.3)
            mean_prob = mean_prob * (1 - smoothing_factor) + 0.5 * smoothing_factor
        
        # Final decision
        label = "FAKE" if mean_prob >= 0.5 else "REAL"
        
        # Convert to confidence (distance from 0.5)
        confidence = abs(mean_prob - 0.5) * 2
        
        # Recommendation based on uncertainty
        if uncertainty > 0.25:
            recommendation = "UNCERTAIN — MIXED SIGNALS. Human review recommended."
        elif confidence > 0.8:
            recommendation = f"High confidence {label} detection."
        elif confidence > 0.6:
            recommendation = f"Moderate confidence {label} detection. Review suggested."
        else:
            recommendation = f"Low confidence {label} detection. Manual verification required."
        
        return VideoVerdict(
            label=label,
            confidence=float(confidence),
            per_frame_scores=probs.tolist(),
            frame_count=len(probs),
            uncertainty=float(uncertainty),
            recommendation=recommendation
        )


def analyze_video_file(
    video_path: str,
    model_path: str,
    backbone: str = "efficientnetv2_s"
) -> dict:
    """Convenience function for video analysis."""
    
    # Load model
    model = DeepfakeDetector(backbone=backbone)
    checkpoint = torch.load(model_path, map_location="cpu")
    model.load_state_dict(checkpoint["model_state_dict"])
    
    # Create analyzer
    device = "cuda" if torch.cuda.is_available() else "cpu"
    analyzer = VideoForensicAnalyzer(model, device=device)
    
    # Analyze
    verdict = analyzer.analyze_video(video_path)
    
    return {
        "label": verdict.label,
        "confidence": verdict.confidence,
        "frame_count": verdict.frame_count,
        "uncertainty": verdict.uncertainty,
        "recommendation": verdict.recommendation
    }
```

---

## Evaluation Protocol

### Cross-Dataset Evaluation

```python
# ml/evaluation/evaluator.py

import torch
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix,
    precision_recall_curve, roc_curve
)
from typing import Dict, List, Tuple
import json
from pathlib import Path
from tqdm import tqdm

class CrossDatasetEvaluator:
    """
    Comprehensive model evaluation with cross-dataset testing.
    
    This is CRITICAL for proving true generalization.
    Train on Dataset A, test on Dataset B.
    """
    
    def __init__(self, model, device: str = "cuda"):
        self.model = model.to(device)
        self.model.eval()
        self.device = device
    
    @torch.no_grad()
    def evaluate_dataset(
        self,
        data_loader,
        dataset_name: str = "test"
    ) -> Dict:
        """Evaluate model on a dataset."""
        all_labels = []
        all_probs = []
        all_preds = []
        
        for images, labels in tqdm(data_loader, desc=f"Evaluating {dataset_name}"):
            images = images.to(self.device)
            
            logits = self.model(images).squeeze()
            probs = torch.sigmoid(logits).cpu().numpy()
            
            if probs.ndim == 0:
                probs = [probs.item()]
            
            preds = (np.array(probs) > 0.5).astype(int)
            
            all_labels.extend(labels.numpy())
            all_probs.extend(probs)
            all_preds.extend(preds)
        
        return self._compute_metrics(
            np.array(all_labels),
            np.array(all_probs),
            np.array(all_preds),
            dataset_name
        )
    
    def _compute_metrics(
        self,
        labels: np.ndarray,
        probs: np.ndarray,
        preds: np.ndarray,
        dataset_name: str
    ) -> Dict:
        """Compute comprehensive metrics."""
        
        metrics = {
            "dataset": dataset_name,
            "n_samples": len(labels),
            "accuracy": accuracy_score(labels, preds),
            "precision": precision_score(labels, preds, zero_division=0),
            "recall": recall_score(labels, preds, zero_division=0),
            "f1_score": f1_score(labels, preds, zero_division=0),
        }
        
        # AUC-ROC
        try:
            metrics["roc_auc"] = roc_auc_score(labels, probs)
        except ValueError:
            metrics["roc_auc"] = 0.5
        
        # Confusion matrix
        cm = confusion_matrix(labels, preds)
        tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
        
        metrics["confusion_matrix"] = {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp)
        }
        
        # Per-class accuracy
        metrics["real_accuracy"] = tn / (tn + fp) if (tn + fp) > 0 else 0
        metrics["fake_accuracy"] = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        return metrics
    
    def cross_dataset_evaluation(
        self,
        datasets: Dict[str, any],  # name -> dataloader
        output_dir: str = "evaluation_results"
    ) -> Dict:
        """
        Evaluate model across multiple datasets to prove generalization.
        
        Args:
            datasets: Dictionary mapping dataset names to dataloaders
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        all_results = {}
        
        for name, loader in datasets.items():
            print(f"\n{'='*50}")
            print(f"Evaluating on: {name}")
            print(f"{'='*50}")
            
            metrics = self.evaluate_dataset(loader, name)
            all_results[name] = metrics
            
            print(f"Accuracy: {metrics['accuracy']:.4f}")
            print(f"Precision: {metrics['precision']:.4f}")
            print(f"Recall: {metrics['recall']:.4f}")
            print(f"F1 Score: {metrics['f1_score']:.4f}")
            print(f"ROC-AUC: {metrics['roc_auc']:.4f}")
        
        # Compute cross-dataset summary
        summary = self._compute_summary(all_results)
        all_results["summary"] = summary
        
        # Save results
        with open(output_path / "evaluation_results.json", "w") as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n{'='*50}")
        print("Cross-Dataset Summary")
        print(f"{'='*50}")
        print(f"Mean Accuracy: {summary['mean_accuracy']:.4f} ± {summary['std_accuracy']:.4f}")
        print(f"Mean AUC: {summary['mean_auc']:.4f} ± {summary['std_auc']:.4f}")
        print(f"Generalization Gap: {summary['generalization_gap']:.4f}")
        
        return all_results
    
    def _compute_summary(self, results: Dict) -> Dict:
        """Compute summary statistics across datasets."""
        accuracies = [r["accuracy"] for r in results.values()]
        aucs = [r["roc_auc"] for r in results.values()]
        
        return {
            "mean_accuracy": np.mean(accuracies),
            "std_accuracy": np.std(accuracies),
            "min_accuracy": np.min(accuracies),
            "max_accuracy": np.max(accuracies),
            "mean_auc": np.mean(aucs),
            "std_auc": np.std(aucs),
            "generalization_gap": np.max(accuracies) - np.min(accuracies)
        }
```

---

## Model Versioning

### Version Management System

```python
# ml/versioning/model_registry.py

import torch
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
import shutil

class ModelRegistry:
    """
    Production model versioning and registry system.
    
    Features:
    - Semantic versioning
    - Metadata tracking
    - Rollback support
    - A/B testing support
    """
    
    def __init__(self, registry_dir: str = "model_registry"):
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.registry_dir / "registry.json"
        
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {"models": {}, "active_model": None, "history": []}
    
    def _save_registry(self):
        with open(self.metadata_file, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def register_model(
        self,
        model_path: str,
        version: str,
        description: str,
        training_config: Dict,
        evaluation_metrics: Dict,
        datasets_used: List[str],
        backbone: str
    ) -> str:
        """Register a new model version."""
        
        # Generate model hash
        with open(model_path, 'rb') as f:
            model_hash = hashlib.sha256(f.read()).hexdigest()[:12]
        
        version_id = f"v{version}-{model_hash}"
        
        # Copy model to registry
        model_dest = self.registry_dir / f"{version_id}.pth"
        shutil.copy(model_path, model_dest)
        
        # Create metadata
        metadata = {
            "version_id": version_id,
            "version": version,
            "description": description,
            "registered_at": datetime.now().isoformat(),
            "model_path": str(model_dest),
            "model_hash": model_hash,
            "backbone": backbone,
            "training_config": training_config,
            "evaluation_metrics": evaluation_metrics,
            "datasets_used": datasets_used,
            "is_active": False,
            "deployment_count": 0
        }
        
        self.registry["models"][version_id] = metadata
        self._save_registry()
        
        return version_id
    
    def activate_model(self, version_id: str):
        """Set a model as the active production model."""
        if version_id not in self.registry["models"]:
            raise ValueError(f"Model {version_id} not found")
        
        # Deactivate current model
        if self.registry["active_model"]:
            self.registry["models"][self.registry["active_model"]]["is_active"] = False
        
        # Activate new model
        self.registry["models"][version_id]["is_active"] = True
        self.registry["models"][version_id]["deployment_count"] += 1
        self.registry["active_model"] = version_id
        
        # Log activation
        self.registry["history"].append({
            "action": "activate",
            "version_id": version_id,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save_registry()
    
    def rollback(self, steps: int = 1) -> Optional[str]:
        """Rollback to a previous model version."""
        activations = [
            h for h in self.registry["history"]
            if h["action"] == "activate"
        ]
        
        if len(activations) <= steps:
            return None
        
        target = activations[-(steps + 1)]
        self.activate_model(target["version_id"])
        
        self.registry["history"].append({
            "action": "rollback",
            "to_version": target["version_id"],
            "steps": steps,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save_registry()
        return target["version_id"]
    
    def get_active_model(self) -> Optional[Dict]:
        """Get the currently active model."""
        if not self.registry["active_model"]:
            return None
        return self.registry["models"][self.registry["active_model"]]
    
    def load_model(self, version_id: str = None) -> torch.nn.Module:
        """Load a model by version ID (or active model if None)."""
        if version_id is None:
            version_id = self.registry["active_model"]
        
        if version_id is None:
            raise ValueError("No active model and no version specified")
        
        metadata = self.registry["models"][version_id]
        
        from ml.models.backbones import DeepfakeDetector
        model = DeepfakeDetector(backbone=metadata["backbone"])
        
        checkpoint = torch.load(metadata["model_path"], map_location="cpu")
        model.load_state_dict(checkpoint["model_state_dict"])
        
        return model
    
    def list_models(self) -> List[Dict]:
        """List all registered models."""
        return list(self.registry["models"].values())
    
    def compare_models(self, version_ids: List[str]) -> Dict:
        """Compare metrics between model versions."""
        comparisons = {}
        
        for vid in version_ids:
            if vid not in self.registry["models"]:
                continue
            metrics = self.registry["models"][vid]["evaluation_metrics"]
            comparisons[vid] = metrics
        
        return comparisons
```

---

## Implementation Files

### Project Structure

```
ml/
├── __init__.py
├── config.py                    # Training configuration
├── data/
│   ├── __init__.py
│   ├── streaming_dataset.py     # Memory-efficient data loading
│   ├── sharding.py              # Dataset sharding
│   └── quality_check.py         # Corruption detection
├── preprocessing/
│   ├── __init__.py
│   ├── face_detection.py        # Face detection & cropping
│   └── video_sampler.py         # Intelligent frame sampling
├── augmentation/
│   ├── __init__.py
│   └── transforms.py            # Data augmentation
├── models/
│   ├── __init__.py
│   └── backbones.py             # Model architectures
├── training/
│   ├── __init__.py
│   └── trainer.py               # Large-scale trainer
├── inference/
│   ├── __init__.py
│   └── video_inference.py       # Video-level inference
├── evaluation/
│   ├── __init__.py
│   └── evaluator.py             # Cross-dataset evaluation
├── versioning/
│   ├── __init__.py
│   └── model_registry.py        # Model versioning
└── scripts/
    ├── download_datasets.py     # Dataset download
    ├── prepare_data.py          # Data preparation
    ├── train.py                 # Training entry point
    ├── evaluate.py              # Evaluation entry point
    └── export_onnx.py           # ONNX export
```

### Quick Start Commands

```bash
# 1. Prepare datasets
python -m ml.scripts.download_datasets --output data/raw
python -m ml.scripts.prepare_data --input data/raw --output data/processed

# 2. Validate data quality
python -c "from ml.data.quality_check import validate_dataset; validate_dataset('data/processed/train')"

# 3. Train model
python -m ml.scripts.train \
    --train-dir data/processed/train \
    --val-dir data/processed/val \
    --backbone efficientnetv2_s \
    --epochs 30 \
    --batch-size 32 \
    --output outputs/run_001

# 4. Evaluate
python -m ml.scripts.evaluate \
    --model outputs/run_001/best_model.pth \
    --test-dirs data/faceforensics/test data/celebdf/test data/dfdc/test

# 5. Register model
python -c "
from ml.versioning.model_registry import ModelRegistry
registry = ModelRegistry()
registry.register_model(
    'outputs/run_001/best_model.pth',
    version='1.0.0',
    description='Initial production model',
    training_config={'epochs': 30, 'backbone': 'efficientnetv2_s'},
    evaluation_metrics={'accuracy': 0.92, 'auc': 0.96},
    datasets_used=['FaceForensics++', 'Celeb-DF', 'DFDC'],
    backbone='efficientnetv2_s'
)
"
```

---

## Summary

This ML pipeline provides:

✅ **Large-scale data handling** - Streaming, sharding, corruption detection  
✅ **Modern architectures** - DINOv2, EfficientNet-V2, ConvNeXt, ViT  
✅ **Realistic augmentation** - Social media compression, blur, noise  
✅ **Phased training** - Frozen → partial → full fine-tuning  
✅ **Video-level inference** - Frame aggregation with uncertainty estimation  
✅ **Cross-dataset evaluation** - True generalization testing  
✅ **Production versioning** - Registry, rollback, deployment tracking  

The system is designed to train on **lakhs of samples** while avoiding:
- Dataset overfitting
- Shortcut learning
- Over-confident predictions

This produces research-grade models suitable for real-world deployment.
