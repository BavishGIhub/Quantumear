# 📄 QuantumEAR — Product Requirements Document (PRD)

**Version:** 2.0  
**Last Updated:** 2026-02-24  
**Author:** Engineering Team  
**Status:** Production Ready  

---

## 📋 Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Product Vision & Goals](#3-product-vision--goals)
4. [Target Audience](#4-target-audience)
5. [System Architecture](#5-system-architecture)
6. [Android Application Structure](#6-android-application-structure)
7. [Feature Specifications](#7-feature-specifications)
8. [User Flows](#8-user-flows)
9. [Data Models & Schema](#9-data-models--schema)
10. [API Contracts](#10-api-contracts)
11. [Non-Functional Requirements](#11-non-functional-requirements)
12. [Tech Stack Summary](#12-tech-stack-summary)
13. [File & Module Inventory](#13-file--module-inventory)
14. [Milestones & Roadmap](#14-milestones--roadmap)

---

## 1. Executive Summary

**QuantumEAR** (Quantum-Enhanced Audio Recognition) is a hybrid quantum-classical mobile application that detects AI-generated voice deepfakes by analyzing sub-perceptual spectral artifacts in audio files. It combines a pre-trained **ResNet-18** CNN for feature extraction with a **Qiskit-powered quantum variational circuit** (ZZFeatureMap + RealAmplitudes) for binary classification.

The Android application is built using **Capacitor.js** wrapping a **Next.js 16+** progressive web app, delivering a native mobile experience with web-based development velocity.

### Current Implementation Stack
- **Frontend**: Next.js 16.1.6 + React 19.2.3 + Tailwind CSS 4.x
- **Mobile Wrapper**: Capacitor.js 8.x (Android API)
- **Backend**: FastAPI (Python 3.10+)
- **ML Pipeline**: PyTorch + librosa + Qiskit
- **Database**: Supabase (PostgreSQL)
- **Build Target**: Android APK (API 22-34)

---

## 2. Problem Statement

### The Deepfake Audio Threat
AI-generated voice cloning (ElevenLabs, Tortoise-TTS, VALL-E) has become alarmingly realistic, enabling:
- **Social engineering attacks** — Executive impersonation for wire fraud
- **Disinformation** — Fabricated audio of public figures
- **Identity theft** — Bypassing voice-based biometric authentication
- **Harassment** — Non-consensual voice cloning

### Why Quantum?
Traditional classifiers struggle with subtle spectral artifacts from modern synthesizers. Quantum-enhanced approaches encode audio features into **Hilbert space** via entanglement, detecting non-linear correlations classical methods miss.

---

## 3. Product Vision & Goals

### Vision
> *"Make every person capable of verifying audio authenticity in seconds, powered by quantum computing."*

### Primary Goals

| # | Goal | Metric |
|---|------|--------|
| G1 | Detect AI-generated audio with high accuracy | Trust Score accuracy ≥ 85% |
| G2 | Sub-2-second analysis on mobile | Processing time ≤ 2000ms |
| G3 | Cross-platform mobile availability | Android APK (iOS future) |
| G4 | Zero-knowledge operation | Audio files NOT stored — only metadata |
| G5 | Native mobile experience | Capacitor.js with haptics, file system |

---

## 4. Target Audience

| Persona | Description | Use Case |
|---------|-------------|----------|
| **Security Analyst** | Corporate cybersecurity | Verify voicemail/meeting recordings |
| **Journalist** | Media professionals | Authenticate source audio |
| **General Consumer** | Privacy-conscious individuals | Check suspicious voice messages |
| **Researcher** | ML/Quantum researchers | Study hybrid QNN performance |

---

## 5. System Architecture

### 5.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ANDROID APPLICATION                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           Capacitor.js Container                      │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │         Next.js 16+ Frontend (SPA)               │  │  │
│  │  │  ┌────────┐ ┌──────────┐ ┌────────────────┐   │  │  │
│  │  │  │DropZone│ │ Waveform │ │ Trust Meter    │   │  │  │
│  │  │  │ Upload │ │ Viewer   │ │ (SVG Gauge)    │   │  │  │
│  │  │  └────────┘ └──────────┘ └────────────────┘   │  │  │
│  │  │  ┌─────────────────┐ ┌──────────────────┐    │  │  │
│  │  │  │ Results Panel   │ │ Scan History     │    │  │  │
│  │  │  │ (Entropy Chart) │ │ (Supabase Sync)  │    │  │  │
│  │  │  └─────────────────┘ └──────────────────┘    │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│         Capacitor Plugins: Haptics, StatusBar, Filesystem    │
└─────────────────────────────────────────────────────────────┘
                              │ HTTPS / HTTP
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 BACKEND (FastAPI)                          │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────────┐   │
│  │  Audio   │→ │  Mel-    │→ │ ResNet-18 Feature      │   │
│  │  Proc    │  │ Spectro  │  │ Extractor (512→4 dim)   │   │
│  └──────────┘  └──────────┘  └────────────────────────┘   │
│                                           │                 │
│                                           ▼                 │
│                              ┌────────────────────────┐    │
│                              │ Quantum Classifier      │    │
│                              │ (ZZFeatureMap + Real    │    │
│                              │  Amplitudes + Qiskit)   │    │
│                              └────────────────────────┘    │
│                                           │                 │
│                    ┌──────────────────────┘                 │
│                    ▼                                        │
│          ┌──────────────────┐                                │
│          │   Supabase DB    │                                │
│          │  (PostgreSQL)    │                                │
│          └──────────────────┘                                │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Processing Pipeline (5 Stages)

| Stage | Module | Input | Output | Time |
|-------|--------|-------|--------|------|
| 1. Audio Preprocessing | `audio_processor.py` | Raw audio bytes | Normalized signal (22050Hz, 5s, mono) | ~50ms |
| 2. Spectrogram Generation | `spectrogram.py` | Signal `y` | Mel-spectrogram tensor (3, 224, 224) | ~100ms |
| 3. Feature Extraction | `feature_extractor.py` | Spectrogram | Feature vector (4,) in [-1, 1] | ~200ms |
| 4. Quantum Classification | `quantum_classifier.py` | Features (4,) | Probability [0, 1], label | ~800ms |
| 5. Entropy Analysis | `entropy.py` | Signal `y` | Entropy timeline + regions | ~150ms |

---

## 6. Android Application Structure

### 6.1 Capacitor Configuration

```typescript
// capacitor.config.ts
const config: CapacitorConfig = {
    appId: 'com.quantumear.app',
    appName: 'QuantumEAR',
    webDir: 'out',
    server: {
        androidScheme: 'https',
    },
    plugins: {
        StatusBar: {
            style: 'DARK',
            backgroundColor: '#00000000',
            overlaysWebView: true,
        },
        SplashScreen: {
            launchAutoHide: true,
            backgroundColor: '#030712',
            androidSplashResourceName: 'splash',
            androidScaleType: 'CENTER_CROP',
            showSpinner: false,
            splashFullScreen: true,
            splashImmersive: true,
        },
    },
    android: {
        backgroundColor: '#030712',
        allowMixedContent: true,
        captureInput: true,
        webContentsDebuggingEnabled: false,
    },
};
```

### 6.2 Android Manifest

```xml
<!-- AndroidManifest.xml -->
<manifest>
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/AppTheme">
        
        <activity android:name=".MainActivity"
            android:launchMode="singleTask"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        
        <provider android:name="androidx.core.content.FileProvider"
            android:authorities="${applicationId}.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
        </provider>
    </application>
    
    <!-- Permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.READ_MEDIA_AUDIO" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.VIBRATE" />
</manifest>
```

### 6.3 Build Configuration

```gradle
// app/build.gradle
android {
    namespace = "com.quantumear.app"
    compileSdk = rootProject.ext.compileSdkVersion
    defaultConfig {
        applicationId "com.quantumear.app"
        minSdkVersion rootProject.ext.minSdkVersion
        targetSdkVersion rootProject.ext.targetSdkVersion
        versionCode 1
        versionName "1.0"
    }
}

dependencies {
    implementation project(':capacitor-android')
    implementation "androidx.appcompat:appcompat:$androidxAppCompatVersion"
    implementation "androidx.core:core-splashscreen:$coreSplashScreenVersion"
    implementation project(':capacitor-cordova-android-plugins')
}
```

---

## 7. Feature Specifications

### 7.1 Core Features (Implemented)

#### F1: Audio File Upload (DropZone)
- **Component**: `DropZone.tsx`
- **Behavior**: Drag-and-drop or click-to-browse
- **Formats**: `.wav`, `.mp3`, `.flac`, `.ogg`, `.m4a`
- **Max Size**: 50MB
- **Mobile**: File picker integration via Capacitor Filesystem
- **Haptics**: Vibration feedback on successful upload

#### F2: Trust Score Gauge (TrustMeter)
- **Component**: `TrustMeter.tsx`
- **Display**: Animated circular SVG gauge (0-100%)
- **Color Coding**:
  - 🟢 Green (≥70%): Safe / Organic
  - 🟡 Yellow (40-69%): Warning / Suspicious
  - 🔴 Red (<40%): Danger / Synthetic
- **Animation**: Smooth arc transition with CSS

#### F3: Waveform Visualization
- **Component**: `WaveformViewer.tsx`
- **Library**: WaveSurfer.js v7
- **Features**: Interactive, zoomable waveform
- **Highlights**: High-entropy regions marked

#### F4: Results Panel
- **Component**: `ResultsPanel.tsx`
- **Displays**:
  - Classification label (ORGANIC / SYNTHETIC)
  - Synthetic probability
  - Processing time
  - Entropy timeline chart (Chart.js)
  - Spectrogram image (base64 PNG)
  - Quantum feature values

#### F5: Scan History
- **Component**: `ScanHistory.tsx`
- **Storage**: Supabase PostgreSQL + local state
- **Actions**: View, Delete, Clear all
- **Sync**: Automatic cloud persistence

#### F6: Navigation
- **Component**: `Navbar.tsx`
- **Routes**: Dashboard (`/`), History (`/history`)
- **Style**: Glassmorphism with Framer Motion

#### F7: Mobile Haptics
- **Implementation**: `@capacitor/haptics`
- **Heavy Impact**: When synthetic detected (alert)
- **Light Impact**: When organic detected (confirmation)

### 7.2 Planned Features (Roadmap)

| Feature | Priority | Target |
|---------|----------|--------|
| Real-time microphone recording | P0 | v2.1 |
| Batch file analysis | P1 | v2.2 |
| User authentication (Supabase Auth) | P1 | v2.1 |
| Export PDF reports | P2 | v2.3 |
| iOS support | P1 | v3.0 |
| Dark/Light theme toggle | P3 | v2.2 |
| Multi-language support | P3 | v2.4 |

---

## 8. User Flows

### 8.1 Primary Flow: Audio Analysis

```
1. User opens QuantumEAR Android app
2. Dashboard loads with DropZone
3. User taps DropZone → Android file picker opens
4. User selects audio file from device
5. Upload progress displays (0% → 30%)
6. Backend processes through pipeline:
   - Audio preprocessing (30% → 40%)
   - Spectrogram generation (40% → 50%)
   - ResNet feature extraction (50% → 70%)
   - Quantum classification (70% → 90%)
   - Entropy analysis (90% → 100%)
7. Results appear:
   - Trust Meter animates to score
   - Waveform renders with highlights
   - Results panel shows full analysis
8. Haptic feedback based on result
9. Scan saved to history (local + Supabase)
```

### 8.2 Secondary Flow: View History

```
1. User taps History in Navbar
2. History page loads from Supabase
3. Table displays: filename, trust score, label, timestamp
4. User can:
   - Tap to view scan details
   - Swipe to delete individual scans
   - Clear all history
```

### 8.3 Error Flows

| Scenario | Behavior |
|----------|----------|
| Unsupported format | Toast error with supported formats list |
| File too large (>50MB) | Error with size limit message |
| Backend unreachable | Demo mode with mock data + warning banner |
| Network error | Retry button + offline indicator |

---

## 9. Data Models & Schema

### 9.1 TypeScript Types (Frontend)

```typescript
interface ScanResult {
    id: string;                              // UUID
    filename: string;                        // Original filename
    trust_score: number;                     // 0.0 - 100.0
    label: 'organic' | 'synthetic';         // Classification
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
    values: number[];          // Normalized entropy [0, 1]
    threshold: number;         // High-entropy threshold (0.85)
    total_duration: number;    // Audio duration
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
```

---

## 10. API Contracts

### Base URL
```
Production:  https://<your-hf-space>.hf.space
Development: http://localhost:8000
Android:     http://10.0.2.2:8000 (emulator)
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/analyze` | Synchronous audio analysis |
| `GET` | `/api/history` | List scan history |
| `DELETE` | `/api/history/{id}` | Delete scan |
| `DELETE` | `/api/history` | Clear all history |

### Request/Response Example

**POST /api/analyze**
```http
Content-Type: multipart/form-data

file: <binary audio data>
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
        "times": [0.0, 0.023, 0.046],
        "values": [0.45, 0.52, 0.61],
        "threshold": 0.85,
        "total_duration": 5.0
    },
    "waveform_data": [0.12, -0.34, 0.67],
    "spectrogram_base64": "iVBORw0KGgoAAAA...",
    "processing_time_ms": 1234.5,
    "quantum_features": [0.12, -0.45, 0.78, 0.33],
    "timestamp": "2026-02-24T09:15:30.123456",
    "status": "complete"
}
```

---

## 11. Non-Functional Requirements

### 11.1 Performance Targets

| Metric | Requirement | Status |
|--------|-------------|--------|
| App Load Time | < 1.0s | ✅ Achieved |
| End-to-End Pipeline | < 2500ms | ✅ ~1300ms |
| APK Size | < 20MB | ✅ Achieved |
| UI Responsiveness | 60 FPS | ✅ Achieved |

### 11.2 Security

- **Input validation**: Strict file extension whitelist
- **No audio storage**: Only metadata persisted
- **UUID-based IDs**: Non-sequential scan IDs
- **CORS**: Configurable allowed origins
- **Permissions**: Minimal required (Internet, Storage, Vibrate)

### 11.3 Reliability

- **Classical fallback**: MLP when Qiskit unavailable
- **Offline UI**: Demo mode when backend disconnected
- **Graceful errors**: All stages wrapped in try/except
- **Lazy loading**: Models initialized on first request

---

## 12. Tech Stack Summary

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend Framework | Next.js | 16.1.6 |
| UI Library | React | 19.2.3 |
| Styling | Tailwind CSS | 4.x |
| Animations | Framer Motion | 12.x |
| Charts | Chart.js | 4.x |
| Waveform | WaveSurfer.js | 7.x |
| Icons | Lucide React | 0.575 |
| File Upload | react-dropzone | 15.x |
| Mobile Wrapper | Capacitor.js | 8.x |
| Backend | FastAPI | Latest |
| ML Framework | PyTorch | Latest |
| Audio Processing | librosa | Latest |
| Quantum Computing | Qiskit | 1.0+ |
| Database | Supabase | Latest |
| Language (FE) | TypeScript | 5.x |
| Language (BE) | Python | 3.10+ |

---

## 13. File & Module Inventory

### 13.1 Frontend (`app/src/`)

| File | Purpose |
|------|---------|
| `app/page.tsx` | Main dashboard — orchestrates all components |
| `app/layout.tsx` | Root layout with Navbar |
| `app/globals.css` | Global styles, Tailwind, glassmorphism |
| `components/DropZone.tsx` | Audio file upload with validation |
| `components/Navbar.tsx` | Top navigation |
| `components/TrustMeter.tsx` | Circular trust score gauge |
| `components/WaveformViewer.tsx` | WaveSurfer.js interactive waveform |
| `components/ResultsPanel.tsx` | Full analysis results |
| `components/ScanHistory.tsx` | History table with CRUD |
| `lib/api.ts` | API client with upload progress |
| `lib/supabase.ts` | Supabase client |
| `types/index.ts` | TypeScript type definitions |

### 13.2 Android (`app/android/`)

| File | Purpose |
|------|---------|
| `app/src/main/AndroidManifest.xml` | App permissions and configuration |
| `app/build.gradle` | Module build configuration |
| `capacitor.config.ts` | Capacitor platform settings |

### 13.3 Configuration

| File | Purpose |
|------|---------|
| `capacitor.config.ts` | Capacitor config (app ID, plugins) |
| `package.json` | Node.js dependencies |
| `next.config.ts` | Next.js static export config |

---

## 14. Milestones & Roadmap

### Current (v1.0) — Production Ready
- ✅ Android APK via Capacitor.js
- ✅ Audio upload and analysis
- ✅ Trust score visualization
- ✅ Waveform with entropy highlights
- ✅ Scan history with Supabase sync
- ✅ Mobile haptics feedback

### v2.1 (Next)
- Real-time microphone recording
- User authentication (Supabase Auth)
- Improved offline support

### v2.2
- Batch file analysis
- Dark/Light theme toggle

### v2.3
- PDF report export
- Advanced analytics dashboard

### v3.0
- iOS support (Capacitor iOS build)
- Multi-language support

---

**End of Document**
