# 🔊 QuantumEAR — Quantum-Enhanced Audio Recognition

> A hybrid quantum-classical application that detects AI-generated voice deepfakes by analyzing sub-perceptual spectral artifacts.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Next.js](https://img.shields.io/badge/Next.js-14+-black)
![Qiskit](https://img.shields.io/badge/Qiskit-1.0+-purple)
![Android](https://img.shields.io/badge/Android-APK-green)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Running Locally](#running-locally)
- [Building Android APK](#building-android-apk)
- [API Documentation](#api-documentation)
- [Quantum Pipeline](#quantum-pipeline)

---

## 🔍 Overview

QuantumEAR uses a hybrid quantum-classical neural network to detect synthetic (AI-generated) audio with unprecedented accuracy. The system works by:

1. **Preprocessing** — Converting audio files (.wav/.mp3) into Mel-Spectrograms
2. **Feature Extraction** — Using a pre-trained ResNet-18 to extract high-level features
3. **Quantum Encoding** — Mapping features to quantum states via ZZFeatureMap
4. **Classification** — Using RealAmplitudes variational circuit for binary classification

### Mathematical Foundation

The quantum state preparation follows:

```
φ(x) = U_Φ(x) |0⟩^⊗n
```

Where `Φ(x)` represents the non-linear audio features encoded into quantum states.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│                 Android APK (Capacitor)          │
│  ┌────────────────────────────────────────────┐  │
│  │         Next.js 14+ Frontend               │  │
│  │  ┌──────┐ ┌──────────┐ ┌──────────────┐   │  │
│  │  │ Drop │ │ Waveform │ │ Trust Meter  │   │  │
│  │  │ Zone │ │ Viewer   │ │ (0-100%)     │   │  │
│  │  └──────┘ └──────────┘ └──────────────┘   │  │
│  │  ┌──────────────────────────────────────┐  │  │
│  │  │         Scan History Table           │  │  │
│  │  └──────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
                        │ HTTP/WebSocket
                        ▼
┌──────────────────────────────────────────────────┐
│              FastAPI Backend                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │ Audio    │→ │ ResNet   │→ │ Quantum      │   │
│  │ Preproc  │  │ Feature  │  │ Classifier   │   │
│  │ (librosa)│  │ Extract  │  │ (Qiskit)     │   │
│  └──────────┘  └──────────┘  └──────────────┘   │
│                       │                           │
│                       ▼                           │
│              ┌──────────────┐                    │
│              │   Supabase   │                    │
│              │   Database   │                    │
│              └──────────────┘                    │
└──────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer       | Technology                                    |
|-------------|-----------------------------------------------|
| Frontend    | Next.js 14+, Tailwind CSS, Framer Motion      |
| Backend     | FastAPI (Python 3.10+)                        |
| ML/AI       | PyTorch (ResNet-18), librosa                  |
| Quantum     | Qiskit, qiskit-machine-learning               |
| Database    | Supabase (PostgreSQL + Auth)                  |
| Mobile      | Capacitor.js (Android APK wrapper)            |
| Charts      | Chart.js, WaveSurfer.js                       |

---

## 📁 Project Structure

```
Quantumear/
├── app/                          # Next.js Frontend
│   ├── src/
│   │   ├── app/                  # Next.js App Router
│   │   │   ├── page.tsx          # Dashboard (main page)
│   │   │   ├── history/
│   │   │   │   └── page.tsx      # Scan history page
│   │   │   ├── layout.tsx        # Root layout
│   │   │   └── globals.css       # Global styles
│   │   ├── components/
│   │   │   ├── DropZone.tsx      # Audio file upload
│   │   │   ├── WaveformViewer.tsx# Interactive waveform
│   │   │   ├── TrustMeter.tsx    # Circular gauge
│   │   │   ├── ProgressBar.tsx   # Upload progress
│   │   │   ├── Navbar.tsx        # Navigation
│   │   │   └── ScanHistory.tsx   # History table
│   │   ├── lib/
│   │   │   ├── api.ts            # API client
│   │   │   └── supabase.ts       # Supabase client
│   │   └── types/
│   │       └── index.ts          # TypeScript types
│   ├── capacitor.config.ts       # Capacitor config
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── next.config.mjs
│   └── tsconfig.json
│
├── api/                          # FastAPI Backend
│   ├── main.py                   # FastAPI app entry
│   ├── routers/
│   │   ├── audio.py              # Audio upload & analysis
│   │   └── history.py            # Scan history CRUD
│   ├── requirements.txt
│   └── Dockerfile
│
├── models/                       # Quantum Neural Network
│   ├── quantum_classifier.py     # Hybrid QNN with TorchConnector
│   ├── feature_extractor.py      # ResNet-18 feature extraction
│   └── config.py                 # Model configuration
│
├── utils/                        # Audio Processing
│   ├── audio_processor.py        # Normalization & conversion
│   ├── spectrogram.py            # Mel-spectrogram generation
│   └── entropy.py                # Spectral entropy calculation
│
├── docs/                         # Documentation
│   ├── API.md                    # API documentation
│   ├── QUANTUM_PIPELINE.md       # Quantum circuit documentation
│   └── ANDROID_BUILD.md          # Android build guide
│
└── README.md                     # This file
```

---

## 🚀 Setup & Installation

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- Android Studio (for APK builds)
- Java JDK 17+

### Backend Setup

```bash
cd api
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd app
npm install
npm run dev
```

### Supabase Setup

1. Create a new Supabase project at [supabase.com](https://supabase.com)
2. Run the SQL migration in `docs/supabase_schema.sql`
3. Copy your project URL and anon key to `.env.local`

---

## 📱 Building Android APK

```bash
cd app
npm run build
npx cap sync android
npx cap open android
# Build APK from Android Studio
```

See [docs/ANDROID_BUILD.md](docs/ANDROID_BUILD.md) for detailed instructions.

---

## 📡 API Documentation

### `POST /api/analyze`

Upload and analyze an audio file.

**Request**: `multipart/form-data` with audio file (.wav or .mp3)

**Response**:
```json
{
  "id": "uuid",
  "filename": "sample.wav",
  "trust_score": 87.3,
  "label": "organic",
  "entropy_regions": [[1.2, 2.4], [5.1, 5.8]],
  "spectrogram_url": "/spectrograms/uuid.png",
  "processing_time_ms": 1234,
  "quantum_features": [0.12, -0.45, 0.78, 0.33]
}
```

### `GET /api/history`

Retrieve scan history for the current session.

### `GET /api/health`

Health check endpoint.

See [docs/API.md](docs/API.md) for complete API documentation.

---

## ⚛️ Quantum Pipeline

The hybrid quantum-classical pipeline uses:

1. **ZZFeatureMap** — Encodes classical features into quantum states using entanglement
2. **RealAmplitudes** — Parameterized variational circuit for classification
3. **TorchConnector** — Bridges Qiskit quantum circuits with PyTorch autograd

See [docs/QUANTUM_PIPELINE.md](docs/QUANTUM_PIPELINE.md) for the full mathematical specification.

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

Built with ❤️ and quantum bits.
