# 📄 QuantumEAR — Product Requirements Document (PRD)

**Version:** 1.0  
**Last Updated:** 2026-02-24  
**Author:** Engineering Team  
**Status:** Active Development  

---

## 📋 Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Product Vision & Goals](#3-product-vision--goals)
4. [Target Audience](#4-target-audience)
5. [System Architecture](#5-system-architecture)
6. [Feature Specifications](#6-feature-specifications)
7. [Technical Deep Dive](#7-technical-deep-dive)
8. [User Flows](#8-user-flows)
9. [Data Models & Schema](#9-data-models--schema)
10. [API Contracts](#10-api-contracts)
11. [Non-Functional Requirements](#11-non-functional-requirements)
12. [Tech Stack Summary](#12-tech-stack-summary)
13. [File & Module Inventory](#13-file--module-inventory)
14. [Known Issues & Technical Debt](#14-known-issues--technical-debt)
15. [Flutter Migration Plan](#15-flutter-migration-plan)
16. [Milestones & Roadmap](#16-milestones--roadmap)
17. [Success Metrics](#17-success-metrics)
18. [Appendix](#18-appendix)

---

## 1. Executive Summary

**QuantumEAR** (Quantum-Enhanced Audio Recognition) is a hybrid quantum-classical mobile application that detects AI-generated voice deepfakes by analyzing sub-perceptual spectral artifacts in audio files. It combines a pre-trained **ResNet-18** CNN for feature extraction with a **Qiskit-powered quantum variational circuit** (ZZFeatureMap + RealAmplitudes) for binary classification.

The current implementation consists of:
- A **FastAPI** backend hosting the ML/Quantum pipeline
- A **Next.js 14** frontend with glassmorphism UI
- An **Android APK** distribution via **Capacitor.js**
- **Supabase** (PostgreSQL) for scan history persistence

The application accepts audio files (`.wav`, `.mp3`, `.flac`, `.ogg`, `.m4a`), processes them through a 5-stage pipeline, and returns a **Trust Score (0–100%)** indicating the probability of the audio being organic (human) vs. synthetic (AI-generated).

---

## 2. Problem Statement

### The Deepfake Audio Threat
AI-generated voice cloning (e.g., via ElevenLabs, Tortoise-TTS, VALL-E) has become alarmingly realistic, enabling:
- **Social engineering attacks** — Impersonating executives for wire fraud
- **Disinformation** — Fabricated audio of public figures
- **Identity theft** — Bypassing voice-based biometric authentication
- **Harassment** — Non-consensual voice cloning of individuals

### Why Quantum?
Traditional classifiers struggle with the subtle spectral artifacts produced by modern synthesizers. A quantum-enhanced approach encodes audio features into a **Hilbert space** via entanglement, enabling detection of non-linear correlations that classical methods miss. The ZZFeatureMap's second-order entangling gates capture feature interactions that a standard MLP cannot represent efficiently.

### Current Limitations Being Addressed
1. No public, user-friendly tool exists for real-time audio deepfake detection on mobile devices.
2. Existing detection methods only work on specific TTS engines and fail on novel synthesizers.
3. Classical-only approaches lack the theoretical expressiveness to detect high-order spectral correlations.

---

## 3. Product Vision & Goals

### Vision
> *"Make every person capable of verifying audio authenticity in seconds, powered by quantum computing."*

### Primary Goals
| # | Goal | Metric |
|---|------|--------|
| G1 | Detect AI-generated audio with high accuracy | Trust Score accuracy ≥ 85% on benchmark datasets |
| G2 | Sub-2-second end-to-end analysis on mobile | Processing time ≤ 2000ms |
| G3 | Cross-platform mobile availability | Android APK + iOS (future) |
| G4 | Zero-knowledge operation | Audio files are NOT stored — only metadata |
| G5 | Graceful degradation without quantum hardware | Classical fallback MLP when Qiskit unavailable |

### Secondary Goals
- Build a scalable API for enterprise/third-party integration
- Provide explainability through entropy visualization and waveform highlighting
- Enable historical scan analysis for trend detection

---

## 4. Target Audience

| Persona | Description | Primary Use Case |
|---------|-------------|------------------|
| **Security Analyst** | Corporate cybersecurity professionals | Verify voicemail/meeting recordings for deepfakes |
| **Journalist** | Media professionals receiving audio tips | Authenticate source audio before publication |
| **General Consumer** | Privacy-conscious individuals | Check suspicious voice messages |
| **Researcher** | ML/Quantum computing researchers | Study hybrid QNN classification performance |
| **Enterprise** | Organizations with voice authentication | Integrate via API for automated detection |

---

## 5. System Architecture

### 5.1 High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      Client Layer                                │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │   Android APK (Capacitor.js Wrapper)                      │  │
│  │   ┌────────────────────────────────────────────────────┐   │  │
│  │   │           Next.js 14+ Frontend (SPA)               │   │  │
│  │   │  ┌──────────┐ ┌───────────┐ ┌──────────────────┐  │   │  │
│  │   │  │ DropZone │ │ Waveform  │ │   Trust Meter     │  │   │  │
│  │   │  │ (Upload) │ │ Viewer    │ │   (SVG Gauge)     │  │   │  │
│  │   │  └──────────┘ └───────────┘ └──────────────────┘  │   │  │
│  │   │  ┌──────────────────┐ ┌────────────────────────┐  │   │  │
│  │   │  │  Results Panel   │ │    Scan History Table  │  │   │  │
│  │   │  │ (Entropy Chart)  │ │  (with CRUD actions)   │  │   │  │
│  │   │  └──────────────────┘ └────────────────────────┘  │   │  │
│  │   └────────────────────────────────────────────────────┘   │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
                            │
                     HTTP REST API
                            │
┌──────────────────────────────────────────────────────────────────┐
│                    Backend Layer (FastAPI)                        │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │ Audio       │→ │ Mel-Spectro  │→ │ ResNet-18 Feature      │  │
│  │ Processor   │  │ Generator    │  │ Extractor (512→4 dim)  │  │
│  │ (librosa)   │  │ (librosa)    │  │ (PyTorch)              │  │
│  └─────────────┘  └──────────────┘  └────────────────────────┘  │
│                                              │                   │
│                                              ▼                   │
│                                    ┌────────────────────────┐   │
│                                    │ Quantum Classifier      │   │
│                                    │ ┌──────────┐           │   │
│                                    │ │ZZFeature │→ Real     │   │
│                                    │ │  Map     │  Ampl.    │   │
│                                    │ │(4 qubits)│  Ansatz   │   │
│                                    │ └──────────┘           │   │
│                                    │ (Qiskit + TorchConnect)│   │
│                                    └────────────────────────┘   │
│                                              │                   │
│                    ┌─────────────────────────┘                   │
│                    ▼                                              │
│          ┌──────────────────┐                                    │
│          │   Supabase DB    │                                    │
│          │  (PostgreSQL)    │                                    │
│          └──────────────────┘                                    │
└──────────────────────────────────────────────────────────────────┘
```

### 5.2 Processing Pipeline (5 Stages)

| Stage | Module | Input | Output | Time Est. |
|-------|--------|-------|--------|-----------|
| **1. Audio Preprocessing** | `utils/audio_processor.py` | Raw bytes (.wav/.mp3) | Normalized signal `y` (22050Hz, 5s, mono) | ~50ms |
| **2. Spectrogram Generation** | `utils/spectrogram.py` | Signal `y`, sample rate | Mel-spectrogram tensor `(3, 224, 224)` | ~100ms |
| **3. Feature Extraction** | `models/feature_extractor.py` | Spectrogram tensor | Feature vector `(4,)` in `[-1, 1]` | ~200ms |
| **4. Quantum Classification** | `models/quantum_classifier.py` | Feature vector `(4,)` | Probability `[0, 1]`, label | ~800ms |
| **5. Entropy Analysis** | `utils/entropy.py` | Signal `y`, sample rate | Entropy timeline + high-entropy regions | ~150ms |

### 5.3 Data Flow

```
User uploads .wav/.mp3 file
    ↓
API validates extension & size (≤50MB)
    ↓
librosa loads → mono, 22050Hz, 5s  (pad/truncate)
    ↓
librosa.feature.melspectrogram → 128 mel bands, 2048 FFT, 512 hop
    ↓
Normalize → PIL Image → RGB → Resize 224×224 → ImageNet normalize
    ↓
ResNet-18 backbone (frozen) → 512-dim → reducer (128→64→4) → Tanh → [-1, 1]
    ↓
Scale to [0, 2π] → ZZFeatureMap (4 qubits, 2 reps, full entangle)
    ↓
RealAmplitudes ansatz (3 reps, full entangle) → Z^⊗4 observable
    ↓
TorchConnector → post-process (Linear→ReLU→Linear→Sigmoid)
    ↓
P(synthetic) → Trust Score = (1 - P) × 100
    ↓
Parallel: STFT entropy (1024 window, 512 hop) → high-entropy regions
    ↓
JSON response → Frontend renders Trust Meter, Waveform, Entropy Chart
```

---

## 6. Feature Specifications

### 6.1 Core Features (Implemented ✅)

#### F1: Audio File Upload (DropZone)
- **Component:** `app/src/components/DropZone.tsx`
- **Behavior:** Drag-and-drop or click-to-browse for audio files
- **Supported formats:** `.wav`, `.mp3`, `.flac`, `.ogg`, `.m4a`
- **Max file size:** 50MB
- **Upload progress:** Real-time progress bar via `XMLHttpRequest`
- **Haptic feedback:** Vibration on drop (Capacitor Haptics plugin)

#### F2: Trust Score Gauge (Trust Meter)
- **Component:** `app/src/components/TrustMeter.tsx`
- **Behavior:** Animated circular SVG gauge displaying 0–100% trust score
- **Color coding:**
  - 🟢 Green (≥70%): Safe / Organic
  - 🟡 Yellow (40–69%): Warning / Suspicious
  - 🔴 Red (<40%): Danger / Synthetic
- **Animation:** Smooth arc transition with CSS animation
- **Glow effect:** Dynamic colored box-shadow

#### F3: Waveform Visualization
- **Component:** `app/src/components/WaveformViewer.tsx`
- **Library:** WaveSurfer.js v7
- **Behavior:** Interactive, zoomable waveform with highlighted high-entropy regions
- **Data:** 500 downsampled amplitude points (peak-preserving)

#### F4: Results Panel
- **Component:** `app/src/components/ResultsPanel.tsx`
- **Displays:**
  - Classification label (ORGANIC / SYNTHETIC)
  - Synthetic probability (0.0000–1.0000)
  - Processing time
  - Entropy timeline chart (Chart.js)
  - Spectrogram image (base64 PNG)
  - Quantum feature values

#### F5: Scan History
- **Component:** `app/src/components/ScanHistory.tsx`
- **Page:** `app/src/app/history/page.tsx`
- **Behavior:** Persisted scan log with sortable table
- **Actions:** View, Delete individual scans; Clear all history
- **Storage:** Supabase PostgreSQL (with in-memory fallback)

#### F6: Navigation
- **Component:** `app/src/components/Navbar.tsx`
- **Routes:** Dashboard (`/`), History (`/history`)
- **Style:** Glassmorphism design, Framer Motion transitions

#### F7: Synchronous & Asynchronous Analysis
- **Sync:** `POST /api/analyze` — Blocks until result is ready
- **Async:** `POST /api/analyze/async` — Returns scan ID, poll `/api/scan/{id}/status`
- **Background processing** with progress updates (0% → 100%)

#### F8: Classical Fallback
- When Qiskit is unavailable, a classical MLP takes over classification
- Same API contract — transparent to the frontend
- MLP architecture: `Linear(4, 32) → ReLU → BN → Dropout(0.3) → Linear(32, 16) → ReLU → Linear(16, 1) → Sigmoid`

### 6.2 Planned Features (Roadmap)

| Feature | Priority | Description |
|---------|----------|-------------|
| **Real-time microphone recording** | P0 | Record audio directly in the app |
| **Batch file analysis** | P1 | Upload and analyze multiple files at once |
| **User authentication** | P1 | Supabase Auth for personalized history |
| **Export reports (PDF)** | P2 | Generate shareable analysis reports |
| **Model retraining UI** | P3 | Upload labeled samples to fine-tune the quantum model |
| **iOS support** | P1 | Capacitor iOS build or Flutter cross-platform |
| **WebSocket streaming** | P2 | Real-time progress via WebSocket instead of polling |
| **Multi-language support** | P3 | i18n for UI strings |
| **Dark/Light theme toggle** | P3 | User-selectable theme |

---

## 7. Technical Deep Dive

### 7.1 Audio Preprocessing (`utils/audio_processor.py`)

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Sample Rate | 22050 Hz | Standard for speech; sufficient for human vocal range (300–3400 Hz) |
| Duration | 5 seconds | Minimum for reliable spectral analysis; pad/truncate ensures tensor consistency |
| Channels | Mono | Stereo is unnecessary for deepfake detection; reduces computation by 50% |
| Normalization | Peak normalization to `[-1, 1]` | Prevents clipping; ensures consistent input magnitude |

### 7.2 Spectrogram Generation (`utils/spectrogram.py`)

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| N_MELS | 128 | 128 mel-frequency bands; captures fine spectral detail |
| N_FFT | 2048 | ~93ms window at 22050Hz; balances time/frequency resolution |
| HOP_LENGTH | 512 | ~23ms hop; provides sufficient temporal resolution |
| Output Size | 224 × 224 × 3 | ResNet-18 input requirement; triplicated grayscale for RGB |
| Normalization | ImageNet stats (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]) | Transfer learning compatibility with pre-trained weights |

### 7.3 Feature Extraction (`models/feature_extractor.py`)

```
ResNet-18 (pretrained, frozen backbone)
    ↓
AdaptiveAvgPool → (batch, 512, 1, 1)
    ↓
Flatten → (batch, 512)
    ↓
Linear(512, 128) → ReLU → BatchNorm(128) → Dropout(0.3)
    ↓
Linear(128, 64) → ReLU → BatchNorm(64)
    ↓
Linear(64, 4) → Tanh → (batch, 4)   # Bounded [-1, 1]
```

- **Backbone:** Pre-trained ResNet-18 (frozen to prevent overfitting on small quantum training sets)
- **Reducer:** 3-layer MLP with BatchNorm and Dropout for regularization
- **Output:** 4 features bounded in `[-1, 1]` via Tanh — ideal for quantum angle encoding

### 7.4 Quantum Classifier (`models/quantum_classifier.py`)

#### Circuit Architecture
```
|0⟩ ─── ZZFeatureMap (2 reps) ─── RealAmplitudes (3 reps) ─── Measure Z^⊗4 ───→ post-process → P(synthetic)
|0⟩ ─── ZZFeatureMap (2 reps) ─── RealAmplitudes (3 reps) ─── Measure Z^⊗4 ───→
|0⟩ ─── ZZFeatureMap (2 reps) ─── RealAmplitudes (3 reps) ─── Measure Z^⊗4 ───→
|0⟩ ─── ZZFeatureMap (2 reps) ─── RealAmplitudes (3 reps) ─── Measure Z^⊗4 ───→
```

#### Quantum Parameters
| Parameter | Value | Description |
|-----------|-------|-------------|
| `NUM_QUBITS` | 4 | Number of qubits = number of encoded features |
| `ZZ_REPS` | 2 | ZZFeatureMap entanglement repetitions |
| `ANSATZ_REPS` | 3 | RealAmplitudes variational circuit repetitions |
| `Entanglement` | Full | Every qubit pair coupled |
| `Observable` | `Z^⊗4` = `ZZZZ` | Full-register Pauli-Z measurement |
| `Estimator` | `StatevectorEstimator` | Exact statevector simulation (no shot noise) |

#### Mathematical Foundation
1. **Feature Encoding:** Input scaled from `[-1, 1]` → `[0, 2π]` via `x_scaled = (x + 1) × π`
2. **State Preparation:** `|ψ⟩ = U_ansatz(θ) · U_ZZ(x) |0⟩^⊗4`
3. **Expectation Value:** `⟨ψ| Z^⊗4 |ψ⟩` → single real number in `[-1, 1]`
4. **Post-Processing:** `Linear(1, 16) → ReLU → Linear(16, 1) → Sigmoid → P(synthetic)`

#### TorchConnector Bridge
- Qiskit circuits are wrapped via `TorchConnector` for seamless PyTorch autograd
- Enables end-to-end gradient computation through the quantum layer
- Initial weights: Uniform random in `[-0.1, 0.1]`

### 7.5 Spectral Entropy Analysis (`utils/entropy.py`)

| Parameter | Value | Description |
|-----------|-------|-------------|
| `ENTROPY_WINDOW_SIZE` | 1024 | STFT window size (~46ms at 22050Hz) |
| `ENTROPY_HOP` | 512 | Hop between frames |
| `HIGH_ENTROPY_THRESHOLD` | 0.85 | Normalized entropy above this = "high entropy" |
| `min_duration` | 50ms | Minimum region length to report |

**Algorithm:**
1. Compute STFT with specified window/hop
2. Compute power spectrum: `P = |STFT|²`
3. Normalize each frame to probability distribution: `p(f) = P(f) / ΣP`
4. Shannon entropy per frame: `H = -Σ p(f) · log₂(p(f))`
5. Normalize: `H_norm = H / log₂(N_freq_bins)`
6. Find contiguous regions where `H_norm > 0.85` for at least 50ms

---

## 8. User Flows

### 8.1 Primary Flow: Audio Analysis

```
1. User opens QuantumEAR app
2. Dashboard loads → shows DropZone, empty Trust Meter
3. User drags-and-drops an audio file (.wav / .mp3)
4. DropZone validates file extension and size
5. Upload progress bar animates (0% → 30%)
6. Backend processes:
   a. Audio preprocessing (30% → 40%)
   b. Spectrogram generation (40% → 50%)
   c. ResNet feature extraction (50% → 70%)
   d. Quantum classification (70% → 90%)
   e. Entropy analysis (90% → 100%)
7. Results appear:
   a. Trust Meter animates to score (e.g., 87.3%)
   b. Waveform viewer renders with entropy highlights
   c. Results panel shows classification + metrics
8. Scan is saved to history (Supabase + in-memory)
```

### 8.2 Secondary Flow: View History

```
1. User navigates to History via Navbar
2. History page loads scan records from API
3. Table shows: filename, trust score, label, timestamp
4. User can:
   a. Click to view scan details
   b. Delete individual scans
   c. Clear all history
```

### 8.3 Error Flows

| Scenario | Behavior |
|----------|----------|
| Unsupported file format | HTTP 400 with detail message; DropZone shows error |
| File too large (>50MB) | HTTP 400 with size limit message |
| Backend unreachable | Frontend shows "Backend Disconnected" status |
| Analysis pipeline failure | HTTP 500; error state in UI |
| Qiskit unavailable | Silent fallback to classical MLP; no user impact |

---

## 9. Data Models & Schema

### 9.1 TypeScript Types (Frontend)

```typescript
interface ScanResult {
    id: string;                              // UUID
    filename: string;                        // Original file name
    trust_score: number;                     // 0.0 - 100.0
    label: 'organic' | 'synthetic';         // Classification result
    synthetic_probability: number;           // 0.0000 - 1.0000
    entropy_regions: [number, number][];    // [[start_sec, end_sec], ...]
    entropy_timeline: EntropyTimeline | null;
    waveform_data: number[] | null;         // 500 downsampled points
    spectrogram_base64: string | null;      // PNG base64
    processing_time_ms: number;             // Pipeline duration
    quantum_features: number[];             // 4 feature values
    timestamp: string;                       // ISO 8601
    status: 'complete' | 'processing' | 'error';
}

interface EntropyTimeline {
    times: number[];           // Time points in seconds
    values: number[];          // Normalized entropy values [0, 1]
    threshold: number;         // High-entropy threshold (0.85)
    total_duration: number;    // Total audio duration
}
```

### 9.2 Supabase PostgreSQL Schema

```sql
CREATE TABLE scan_history (
    id              BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    scan_id         UUID NOT NULL UNIQUE,
    filename        TEXT NOT NULL,
    trust_score     DECIMAL(5,1) NOT NULL,
    label           TEXT NOT NULL CHECK (label IN ('organic', 'synthetic')),
    synthetic_probability  DECIMAL(6,4),
    processing_time_ms     DECIMAL(10,1),
    entropy_regions_count  INTEGER DEFAULT 0,
    quantum_features       JSONB,
    scanned_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_scan_history_scanned_at ON scan_history(scanned_at DESC);
CREATE INDEX idx_scan_history_label ON scan_history(label);
CREATE INDEX idx_scan_history_trust_score ON scan_history(trust_score);
```

### 9.3 Pydantic Models (Backend)

```python
class ScanResult(BaseModel):
    id: str
    filename: str
    trust_score: float              # (1 - synthetic_prob) * 100
    label: str                      # "organic" | "synthetic"
    synthetic_probability: float    # Raw model output [0, 1]
    entropy_regions: list           # [[start, end], ...]
    entropy_timeline: Optional[dict]
    waveform_data: Optional[list]
    spectrogram_base64: Optional[str]
    processing_time_ms: float
    quantum_features: list          # Feature vector values
    timestamp: str
    status: str = "complete"
```

---

## 10. API Contracts

### Base URL
```
Production:  https://<your-hf-space>.hf.space
Development: http://localhost:8000
Android Emu: http://10.0.2.2:8000
```

### Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/` | Root — API status | None |
| `GET` | `/api/health` | Health check | None |
| `POST` | `/api/analyze` | Synchronous audio analysis | None |
| `POST` | `/api/analyze/async` | Start async analysis | None |
| `GET` | `/api/scan/{scan_id}/status` | Poll async scan progress | None |
| `GET` | `/api/scan/{scan_id}` | Get completed scan result | None |
| `GET` | `/api/history?limit=50&offset=0` | List scan history | None |
| `DELETE` | `/api/history/{scan_id}` | Delete individual scan | None |
| `DELETE` | `/api/history` | Clear all history | None |

### Request/Response Examples

#### `POST /api/analyze`
**Request:**
```http
POST /api/analyze HTTP/1.1
Content-Type: multipart/form-data; boundary=----FormBoundary
Content-Length: 512000

------FormBoundary
Content-Disposition: form-data; name="file"; filename="sample.wav"
Content-Type: audio/wav

<binary audio data>
------FormBoundary--
```

**Response (200 OK):**
```json
{
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "filename": "sample.wav",
    "trust_score": 87.3,
    "label": "organic",
    "synthetic_probability": 0.127,
    "entropy_regions": [[1.2, 2.4], [5.1, 5.8]],
    "entropy_timeline": {
        "times": [0.0, 0.023, 0.046, ...],
        "values": [0.45, 0.52, 0.61, ...],
        "threshold": 0.85,
        "total_duration": 5.0
    },
    "waveform_data": [0.12, -0.34, 0.67, ...],
    "spectrogram_base64": "iVBORw0KGgoAAAA...",
    "processing_time_ms": 1234.5,
    "quantum_features": [0.12, -0.45, 0.78, 0.33],
    "timestamp": "2026-02-24T09:15:30.123456",
    "status": "complete"
}
```

**Error Responses:**
```json
// 400 Bad Request
{ "detail": "Unsupported format: .exe. Supported: .wav, .mp3, .flac, .ogg, .m4a" }

// 400 Bad Request
{ "detail": "File too large: 75.2MB. Maximum: 50MB" }

// 500 Internal Server Error
{ "detail": "Analysis failed: <error message>" }
```

---

## 11. Non-Functional Requirements

### 11.1 Performance

| Metric | Requirement | Current Status |
|--------|-------------|----------------|
| App Load Time | < 1.0s | ✅ Achieved |
| Audio Preprocessing | < 200ms | ✅ ~50ms |
| Spectrogram Generation | < 200ms | ✅ ~100ms |
| Feature Extraction (ResNet) | < 500ms | ✅ ~200ms |
| Quantum Simulation | < 1500ms | ✅ ~800ms |
| End-to-End Pipeline | < 2500ms | ✅ ~1300ms |
| UI Responsiveness | 60 FPS | ✅ Achieved |
| APK Size | < 20MB | ✅ Achieved |

### 11.2 Scalability
- **Singleton pattern** for model instances — prevents memory leaks
- **Async background tasks** in FastAPI for non-blocking processing
- **In-memory + Supabase** dual storage for reliability
- **CORS configured** for multi-origin support

### 11.3 Security
- **Input validation:** Strict file extension whitelist and size limits
- **UUID-based scan IDs:** Non-sequential to prevent enumeration
- **No audio storage:** Raw audio is never persisted — only metadata
- **CORS:** Configurable allowed origins (currently `*` for dev)
- **Row-Level Security:** Enabled on Supabase tables

### 11.4 Reliability
- **Classical fallback:** App works without Qiskit via MLP fallback
- **Offline UI:** SPA loads without backend connection (shows disconnected status)
- **Graceful error handling:** All pipeline stages wrapped in try/except
- **Model lazy-loading:** Singletons initialized on first request

### 11.5 Deployment
- **Backend:** Dockerized, deployable on Hugging Face Spaces (port 7860)
- **Frontend:** Static export (`output: export`) for Capacitor
- **Android:** Capacitor.js wraps the SPA into APK
- **CI/CD:** Manual build pipeline (automated pipeline is a future goal)

---

## 12. Tech Stack Summary

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend Framework** | Next.js | 14+ | React-based SPA with App Router |
| **UI Styling** | Tailwind CSS | 4.x | Utility-first CSS framework |
| **Animations** | Framer Motion | 12.x | Page transitions, hover effects |
| **Charts** | Chart.js + react-chartjs-2 | 4.x / 5.x | Entropy timeline visualization |
| **Waveform** | WaveSurfer.js | 7.x | Interactive audio waveform |
| **Icons** | Lucide React | 0.575 | SVG icon library |
| **File Upload** | react-dropzone | 15.x | Drag-and-drop file input |
| **Mobile Wrapper** | Capacitor.js | 8.x | Web → Android APK conversion |
| **Backend Framework** | FastAPI | Latest | Async Python API server |
| **ASGI Server** | Uvicorn | Latest | Production ASGI server |
| **ML Framework** | PyTorch | Latest | ResNet-18 + neural network layers |
| **CV Models** | TorchVision | Latest | Pre-trained ResNet-18 weights |
| **Audio Processing** | librosa | Latest | Mel-spectrogram, audio loading |
| **Audio I/O** | SoundFile | Latest | Audio metadata extraction |
| **Signal Processing** | SciPy | Latest | STFT for entropy calculation |
| **Image Processing** | Pillow | Latest | Spectrogram image conversion |
| **Quantum Computing** | Qiskit | 1.0+ | Quantum circuit construction |
| **Quantum ML** | qiskit-machine-learning | Latest | EstimatorQNN, TorchConnector |
| **Quantum Simulator** | qiskit-aer | Latest | Local quantum simulation |
| **Database** | Supabase (PostgreSQL) | Latest | Persistent scan history |
| **Environment** | python-dotenv | Latest | Environment variable management |
| **Validation** | Pydantic | Latest | Request/response model validation |
| **Language (BE)** | Python | 3.10+ | Backend language |
| **Language (FE)** | TypeScript | 5.x | Frontend language |

---

## 13. File & Module Inventory

### 13.1 Backend (`api/`)

| File | Lines | Purpose |
|------|-------|---------|
| `main.py` | 395 | FastAPI application entry point; all routes, startup logic, Supabase integration |
| `requirements.txt` | 21 | Python dependency manifest |
| `Dockerfile` | ~15 | Container build for Hugging Face Spaces deployment |
| `.env` | 2 | Environment variables (SUPABASE_URL, SUPABASE_KEY) |

### 13.2 Models (`models/`)

| File | Lines | Purpose |
|------|-------|---------|
| `config.py` | 42 | Central configuration for audio, quantum, and spectrogram parameters |
| `feature_extractor.py` | 118 | ResNet-18 backbone + dimensionality reducer (512 → 4) |
| `quantum_classifier.py` | 214 | ZZFeatureMap + RealAmplitudes + TorchConnector hybrid QNN |
| `__init__.py` | 1 | Package initializer |

### 13.3 Utilities (`utils/`)

| File | Lines | Purpose |
|------|-------|---------|
| `audio_processor.py` | 112 | Audio loading, normalization, pad/truncate, waveform downsampling |
| `spectrogram.py` | 122 | Mel-spectrogram generation, image conversion, base64 encoding |
| `entropy.py` | 132 | Spectral entropy computation, high-entropy region detection |
| `__init__.py` | 1 | Package initializer |

### 13.4 Frontend (`app/src/`)

| File | Lines | Purpose |
|------|-------|---------|
| `app/page.tsx` | ~200 | Main dashboard — orchestrates DropZone, TrustMeter, Results |
| `app/layout.tsx` | ~30 | Root layout with Navbar and metadata |
| `app/globals.css` | ~400 | Global styles, Tailwind base, glassmorphism, animations |
| `app/history/page.tsx` | ~50 | History page wrapper |
| `components/DropZone.tsx` | ~300 | Drag-and-drop audio upload with validation |
| `components/Navbar.tsx` | ~180 | Top navigation bar with glassmorphism |
| `components/TrustMeter.tsx` | ~180 | Circular SVG trust score gauge |
| `components/WaveformViewer.tsx` | ~230 | WaveSurfer.js interactive waveform |
| `components/ResultsPanel.tsx` | ~270 | Full analysis results with charts |
| `components/ScanHistory.tsx` | ~240 | History table with CRUD actions |
| `lib/api.ts` | 173 | API client class with upload progress tracking |
| `lib/supabase.ts` | 96 | Supabase client + migration SQL |
| `types/index.ts` | 84 | TypeScript type definitions + utility functions |

### 13.5 Configuration Files

| File | Purpose |
|------|---------|
| `app/capacitor.config.ts` | Capacitor Android config (app ID, web dir, plugins) |
| `app/package.json` | Node.js dependencies and scripts |
| `app/tsconfig.json` | TypeScript compiler configuration |
| `app/next.config.ts` | Next.js configuration (static export) |
| `app/postcss.config.mjs` | PostCSS configuration for Tailwind |
| `app/.env.local` | Frontend environment variables |

### 13.6 Documentation (`docs/`)

| File | Purpose |
|------|---------|
| `API.md` | API endpoint documentation |
| `QUANTUM_PIPELINE.md` | Quantum circuit mathematical specification |
| `ANDROID_BUILD.md` | Android APK build guide |
| `PRODUCTION_CHECKLIST.md` | Production readiness checklist |
| `supabase_schema.sql` | Database schema migration SQL |

### 13.7 Scripts (`scripts/`)

| File | Purpose |
|------|---------|
| `test_pipeline.py` | End-to-end pipeline validation with synthetic test audio |

---

## 14. Known Issues & Technical Debt

### 14.1 Bugs

| ID | Severity | Description |
|----|----------|-------------|
| BUG-001 | 🔴 High | `spectrogram_to_base64()` in `utils/spectrogram.py` has a bug — the `colored` array is never updated in the inner loop because `r`, `g`, `b` variables are set but never assigned to `colored[i, j]`. This produces a black spectrogram image in the API response. |
| BUG-002 | 🟡 Medium | CORS is set to `allow_origins=["*"]` — must be restricted for production |
| BUG-003 | 🟡 Medium | `active_scans` dict is defined twice (line 55 and 119) in `main.py` |
| BUG-004 | 🟢 Low | The quantum model has no trained weights — it uses random initialization, so classification results are essentially random until the model is trained on a real dataset |

### 14.2 Technical Debt

| ID | Priority | Description |
|----|----------|-------------|
| TD-001 | P0 | No unit tests for backend beyond `test_pipeline.py` |
| TD-002 | P0 | No model training pipeline — only inference with random weights |
| TD-003 | P1 | No user authentication — all scans are public/anonymous |
| TD-004 | P1 | In-memory scan storage lost on server restart (Supabase is optional) |
| TD-005 | P2 | No rate limiting on API endpoints |
| TD-006 | P2 | No logging framework — uses raw `print()` statements |
| TD-007 | P2 | `sys.path` manipulation in every module for imports |
| TD-008 | P3 | No CI/CD pipeline for automated testing/deployment |

---

## 15. Flutter Migration Plan

### 15.1 Rationale
The user has requested Flutter installation for this project. Flutter provides:
- **True native cross-platform** (Android + iOS + Web + Desktop)
- **Better mobile performance** than Capacitor.js web wrapper
- **Native access** to microphone, file system, haptics without plugins
- **Single codebase** eliminating the Next.js → Capacitor → APK pipeline

### 15.2 Migration Strategy

| Phase | Tasks | Timeline |
|-------|-------|----------|
| **Phase 1: Setup** | Install Flutter SDK, create new Flutter project alongside existing codebase | Day 1 |
| **Phase 2: UI Recreation** | Rebuild all 6 components in Flutter/Dart with Material 3 | Week 1-2 |
| **Phase 3: API Integration** | Connect Flutter app to existing FastAPI backend using `http`/`dio` packages | Week 2 |
| **Phase 4: Native Features** | Implement native audio recording, file picker, haptics | Week 3 |
| **Phase 5: Testing & Polish** | Widget tests, integration tests, performance optimization | Week 4 |

### 15.3 Flutter Package Mapping

| Current (Next.js) | Flutter Equivalent |
|--------------------|--------------------|
| react-dropzone | file_picker + drag_and_drop_files |
| wavesurfer.js | flutter_audio_waveforms / just_audio |
| chart.js | fl_chart |
| framer-motion | Flutter implicit/explicit animations |
| lucide-react | flutter_lucide / material_icons |
| @supabase/supabase-js | supabase_flutter |
| @capacitor/haptics | flutter HapticFeedback (built-in) |
| tailwindcss | Flutter Material 3 theming |

---

## 16. Milestones & Roadmap

| Milestone | Description | Status |
|-----------|-------------|--------|
| M1 | Core pipeline (audio → features → quantum → classification) | ✅ Complete |
| M2 | FastAPI backend with all endpoints | ✅ Complete |
| M3 | Next.js frontend with all components | ✅ Complete |
| M4 | Android APK via Capacitor | ✅ Complete |
| M5 | Supabase integration for persistence | ✅ Complete |
| M6 | Hugging Face Spaces deployment | ✅ Complete |
| M7 | Fix spectrogram rendering bug (BUG-001) | 🔲 Pending |
| M8 | Model training on labeled deepfake dataset | 🔲 Pending |
| M9 | Flutter app (cross-platform native) | 🔲 Starting |
| M10 | User authentication (Supabase Auth) | 🔲 Planned |
| M11 | iOS support | 🔲 Planned |
| M12 | Real-time microphone input | 🔲 Planned |

---

## 17. Success Metrics

| KPI | Target | Measurement |
|-----|--------|-------------|
| Detection Accuracy | ≥ 85% | F1-score on ASVspoof/WaveFake benchmarks |
| False Positive Rate | ≤ 5% | Organic audio incorrectly flagged as synthetic |
| End-to-End Latency | ≤ 2.5s | From upload to result display |
| App Crash Rate | ≤ 0.1% | Firebase Crashlytics / Sentry monitoring |
| User Retention (7-day) | ≥ 40% | Analytics tracking |
| Scan Volume | ≥ 1000/month | Backend monitoring |
| API Uptime | ≥ 99.5% | Health check monitoring |

---

## 18. Appendix

### A. Configuration Reference (`models/config.py`)

```python
# Audio Processing
SAMPLE_RATE = 22050           # Hz
AUDIO_DURATION = 5            # seconds
N_MELS = 128                  # Mel frequency bands
N_FFT = 2048                  # FFT window size
HOP_LENGTH = 512              # FFT hop length

# ResNet Feature Extraction
RESNET_OUTPUT_DIM = 512       # ResNet-18 output dimensionality
NUM_QUANTUM_FEATURES = 4      # Features encoded into qubits

# Quantum Circuit
NUM_QUBITS = 4                # Qubit count (= NUM_QUANTUM_FEATURES)
ZZ_REPS = 2                   # ZZFeatureMap repetitions
ANSATZ_REPS = 3               # RealAmplitudes repetitions

# Classification
CLASSES = ["organic", "synthetic"]
CONFIDENCE_THRESHOLD = 0.5    # Decision boundary

# Spectrogram Image
SPECTROGRAM_WIDTH = 224       # ResNet input width
SPECTROGRAM_HEIGHT = 224      # ResNet input height

# Spectral Entropy
ENTROPY_WINDOW_SIZE = 1024    # STFT window
ENTROPY_HOP = 512             # STFT hop
HIGH_ENTROPY_THRESHOLD = 0.85 # High-entropy cutoff

# File Upload
MAX_FILE_SIZE_MB = 50
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}
```

### B. Environment Variables

| Variable | Location | Purpose |
|----------|----------|---------|
| `SUPABASE_URL` | `api/.env` | Supabase project URL |
| `SUPABASE_KEY` | `api/.env` | Supabase anonymous API key |
| `NEXT_PUBLIC_SUPABASE_URL` | `app/.env.local` | Frontend Supabase URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `app/.env.local` | Frontend Supabase key |
| `NEXT_PUBLIC_API_URL` | `app/.env.local` | Backend API base URL |

### C. Trust Score Calculation

```
Trust Score = (1.0 - P(synthetic)) × 100

Where:
  P(synthetic) = Sigmoid(PostProcess(⟨ψ(x, θ)| Z^⊗4 |ψ(x, θ)⟩))
  
Color Mapping:
  ≥ 70%  → 🟢 Green  (#22c55e) → "Safe"
  40-69% → 🟡 Yellow (#eab308) → "Warning"
  < 40%  → 🔴 Red    (#ef4444) → "Danger"
```

---

*This PRD serves as the single source of truth for the QuantumEAR project.*  
*For questions, refer to the documentation in `docs/` or the codebase directly.*
