# 🏁 QuantumEAR — Project Final Report

## 💎 Executive Summary

QuantumEAR is a high-fidelity, hybrid quantum-classical mobile application designed to identify AI-generated voice deepfakes. By combining traditional Deep Learning (ResNet-18) with Quantum Variational Circuits (ZZFeatureMap), the app detects spectral anomalies that are imperceptible to the human ear but characteristic of AI synthesis.

---

## 🛠️ Technical Implementation

### 1. Hybrid Neural Engine
- **Classical Frontend**: ResNet-18 extracts 512 high-level features from Mel-Spectrograms.
- **Quantum Backend**: A 4-qubit ZZFeatureMap encodes the most significant features into a Hilbert space, followed by a RealAmplitudes variational circuit for classification.
- **Sub-perceptual Analysis**: Calculates spectral entropy across 1024-sample windows to find "stitching" artifacts common in AI voice cloning.

### 2. Premium Android Interface
- **Visualizer**: High-performance canvas-based waveform viewer with "High Entropy" highlighting.
- **Trust Meter**: A circular, color-coded gauge (Green to Red) with custom SVG animations and haptic feedback triggers.
- **Navigation**: Next.js 14 App Router with glassmorphism design and smooth Framer Motion transitions.

### 3. Native Connectivity
- **Capacitor.js**: Wraps the web application into a native Android container.
- **Persistence**: Supabase PostgreSQL backend for history synchronization.
- **API**: FastAPI with asynchronous background workers for high-speed inference.

---

## 🚀 Quick Start Guide

### Step 1: Initialize Backend
```bash
cd api
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Step 2: Initialize Frontend
```bash
cd app
npm install
npm run dev
```

### Step 3: Android APK Generation
```bash
cd app
npm run build
npx cap sync android
# Open in Android Studio to build the signed APK
npx cap open android
```

---

## 📂 Key Files Created

| File | Purpose |
|------|---------|
| `models/quantum_classifier.py` | Hybrid QNN Core Logic |
| `utils/entropy.py` | Spectral Entropy Algorithms |
| `app/src/app/page.tsx` | Main Dashboard & Analysis Flow |
| `app/capacitor.config.ts` | Android Deployment Config |
| `scripts/test_pipeline.py` | End-to-end Logic Validator |
| `docs/API.md` | Full Technical Documentation |

---

**Developed for the Advanced Agentic Coding Project.**
*Status: Ready for Production.*
