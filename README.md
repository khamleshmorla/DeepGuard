# DeepGuard - Advanced Deepfake Detection System

DeepGuard is a production-grade security solution designed to detect AI-generated media (deepfakes) with high precision. By combining a modern React frontend with a robust Python/FastAPI backend and custom machine learning models, DeepGuard offers real-time analysis for both images and videos.

![DeepGuard Dashboard](https://img.shields.io/badge/Status-Production-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Backend-FastAPI%20%2B%20PyTorch-3776AB?style=flat-square&logo=python)
![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite-61DAFB?style=flat-square&logo=react)

## 🚀 Key Features

*   **Multi-Modal Detection**: Analyzes both static images and video steams.
*   **Ensemble Analysis**: Utilizes a combination of CNNs, heavy artifact analysis, and temporal consistency checks for video.
*   **Real-Time Processing**: optimized inference pipeline for low-latency results.
*   **Secure API**: Fully authenticated endpoints with comprehensive history logs.
*   **Modern UI**: Responsive dashboard built with Tailwind CSS and Radix UI.

## 🛠️ Architecture

The system is split into two primary components:

1.  **Frontend (`/src`)**: A React Single Page Application (SPA) utilizing Vite for build tooling. It handles user authentication, file uploads, and visualization of detection results.
2.  **Backend (`/backend`)**: A FastAPI service that exposes REST endpoints. It manages the ML inference pipeline, processes media files using OpenCV/Pillow, and utilizes PyTorch for model execution.

## 🏁 Getting Started

### Prerequisites

*   **Node.js**: v18 or higher
*   **Python**: v3.10 or higher
*   **CUDA Toolkit** (Optional): For GPU prediction acceleration

### Installation & Setup

#### 1. Backend Setup

Initialize the Python environment and install dependencies:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Start the API server:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

#### 2. Frontend Setup

Install Node.js dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Navigate to `http://localhost:8080` to access the application.

## 🧠 Machine Learning Pipeline

Our detection engine uses a specialized EfficientNet-B0 backbone fine-tuned on the FaceForensics++ dataset.

*   **Preprocessing**: Face extraction via Haar Cascades / MTCNN.
*   **Inference**: Frame-by-frame analysis with temporal aggregation for video files.
*   **Scoring**: Probability outputs are normalized to a 0-100% confidence scale.

## 🔒 Security & Privacy

DeepGuard processes all media in a transient manner. Uploaded files are analyzed in a temporary storage buffer and flushed immediately after inference to ensure user privacy.

## 🤝 Contributing

We welcome contributions! Please follow standard GitHub flow:

1.  Fork the repository
2.  Create a feature branch (`git checkout -b feature/amazing-feature`)
3.  Commit your changes (`git commit -m 'Add amazing feature'`)
4.  Push to the branch (`git push origin feature/amazing-feature`)
5.  Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
