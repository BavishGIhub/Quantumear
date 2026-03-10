"""
QuantumEAR — FastAPI Backend
==============================
High-performance async API for hybrid quantum-classical
AI voice deepfake detection.
"""

import os
import sys
import uuid
import time
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import numpy as np

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from models.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB
from utils.audio_processor import load_audio_from_bytes, get_waveform_data
from utils.spectrogram import generate_mel_spectrogram, spectrogram_to_tensor, spectrogram_to_base64
from utils.entropy import compute_spectral_entropy, find_high_entropy_regions, get_entropy_timeline
from models.feature_extractor import get_feature_extractor
from models.quantum_classifier import get_quantum_classifier

from models.feature_extractor import get_feature_extractor
from models.quantum_classifier import get_quantum_classifier

# We rely squarely on our highly trained model pipeline
ENSEMBLE_AVAILABLE = False

# ─── App Setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="QuantumEAR API",
    description="Hybrid quantum-classical AI voice deepfake detection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (fallback)
scan_results = {}
active_scans = {}

# Supabase Initialization
supabase_client = None
try:
    from supabase import create_client, Client
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if url and key:
        supabase_client = create_client(url, key)
        print("✅ Supabase integration enabled.")
    else:
        print("ℹ️ Supabase credentials missing. Using in-memory storage only.")
except ImportError:
    print("ℹ️ Supabase client not installed. Using in-memory storage only.")


async def save_scan_result(result_dict: dict):
    """Save scan result to Supabase or local memory."""
    scan_id = result_dict["id"]
    scan_results[scan_id] = result_dict
    
    if supabase_client:
        try:
            # Prepare data for Supabase (matching the schema)
            db_data = {
                "scan_id": scan_id,
                "filename": result_dict["filename"],
                "trust_score": result_dict["trust_score"],
                "label": result_dict["label"],
                "synthetic_probability": result_dict["synthetic_probability"],
                "processing_time_ms": result_dict["processing_time_ms"],
                "entropy_regions_count": len(result_dict["entropy_regions"]),
                "quantum_features": result_dict["quantum_features"],
                "scanned_at": result_dict["timestamp"]
            }
            supabase_client.table("scan_history").insert(db_data).execute()
        except Exception as e:
            print(f"❌ Supabase save error: {e}")

class ScanResult(BaseModel):
    id: str
    filename: str
    trust_score: float
    label: str
    synthetic_probability: float
    entropy_regions: list
    entropy_timeline: Optional[dict] = None
    waveform_data: Optional[list] = None
    spectrogram_base64: Optional[str] = None
    processing_time_ms: float
    quantum_features: list
    timestamp: str
    status: str = "complete"
    reasoning: str = "Analysis complete"


class ScanStatus(BaseModel):
    id: str
    status: str
    progress: float = 0.0
    message: str = ""


# Track in-progress scans
active_scans = {}


# ─── Startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    """Pre-load models on startup for faster inference."""
    print("🚀 QuantumEAR API starting up...")
    print("📦 Pre-loading feature extractor...")
    get_feature_extractor()
    print("⚛️  Pre-loading quantum classifier...")
    get_quantum_classifier()
    print("✅ All models loaded. Ready for quantum inference.")


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Root endpoint to verify the API is running in the browser."""
    return {
        "service": "QuantumEAR Hybrid AI Pipeline",
        "status": "online",
        "message": "Send audio files to /api/analyze to begin deepfake detection.",
        "docs_url": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "QuantumEAR",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "models_loaded": True
    }


@app.post("/api/analyze", response_model=ScanResult)
async def analyze_audio(file: UploadFile = File(...)):
    """
    Analyze an audio file for AI-generated deepfake detection.
    
    Supports .wav, .mp3, .flac, .ogg, .m4a formats.
    Maximum file size: 50MB.
    
    Returns a complete analysis including trust score,
    entropy regions, waveform data, and quantum features.
    """
    scan_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Validate file extension
    file_ext = Path(file.filename or "unknown.wav").suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {file_ext}. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file
    contents = await file.read()
    
    # Validate file size
    file_size_mb = len(contents) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large: {file_size_mb:.1f}MB. Maximum: {MAX_FILE_SIZE_MB}MB"
        )
    
    try:
        # ── Step 1: Audio Preprocessing ──
        print(f"📁 Loading audio: {file.filename}")
        y, sr = load_audio_from_bytes(contents, filename=file.filename)
        waveform = get_waveform_data(y, num_points=500)
        
        # ── Step 2: Generate Mel-Spectrogram ──
        mel_spec = generate_mel_spectrogram(y, sr)
        spec_tensor = spectrogram_to_tensor(mel_spec)
        spec_b64 = spectrogram_to_base64(mel_spec)
        
        # ── Step 3: Feature Extraction (ResNet-18) ──
        extractor = get_feature_extractor()
        features = extractor.extract_features(spec_tensor)
        
        # ── Step 4: Quantum Classification ──
        print("🧠 Running quantum classification...")
        classifier = get_quantum_classifier()
        
        # Predict using our highly trained Neural Network model directly
        trust_score, label, reasoning = classifier.predict(features, audio_signal=y, sr=sr)
        synthetic_prob = (100.0 - trust_score) / 100.0
        
        # ── Step 5: Spectral Entropy Analysis ──
        entropy = compute_spectral_entropy(y, sr)
        entropy_regions = find_high_entropy_regions(entropy, sr)
        entropy_tl = get_entropy_timeline(entropy, sr)
        
        processing_time = (time.time() - start_time) * 1000
        
        result = ScanResult(
            id=scan_id,
            filename=file.filename or "unknown",
            trust_score=round(trust_score, 1),
            label=label,
            synthetic_probability=round(synthetic_prob, 4),
            entropy_regions=entropy_regions,
            entropy_timeline=entropy_tl,
            waveform_data=waveform,
            spectrogram_base64=spec_b64,
            processing_time_ms=round(processing_time, 1),
            quantum_features=features.tolist(),
            timestamp=datetime.utcnow().isoformat(),
            status="complete",
            reasoning=reasoning if 'reasoning' in locals() else "Analysis complete"
        )
        
        # Store result persistently
        await save_scan_result(result.model_dump())
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/api/analyze/async")
async def analyze_audio_async(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Start async audio analysis. Returns a scan ID immediately.
    Poll /api/scan/{scan_id}/status for progress updates.
    """
    scan_id = str(uuid.uuid4())
    
    # Validate
    file_ext = Path(file.filename or "unknown.wav").suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {file_ext}")
    
    contents = await file.read()
    filename = file.filename or "unknown"
    
    active_scans[scan_id] = {
        "status": "processing",
        "progress": 0.0,
        "message": "Starting analysis..."
    }
    
    background_tasks.add_task(
        process_audio_background, scan_id, contents, filename
    )
    
    return {"scan_id": scan_id, "status": "processing"}


async def process_audio_background(scan_id: str, contents: bytes, filename: str):
    """Background task for async audio processing."""
    start_time = time.time()
    
    try:
        active_scans[scan_id] = {"status": "processing", "progress": 0.1, "message": "Loading audio..."}
        y, sr = load_audio_from_bytes(contents, filename=filename)
        waveform = get_waveform_data(y)
        
        active_scans[scan_id] = {"status": "processing", "progress": 0.3, "message": "Generating spectrogram..."}
        mel_spec = generate_mel_spectrogram(y, sr)
        spec_tensor = spectrogram_to_tensor(mel_spec)
        spec_b64 = spectrogram_to_base64(mel_spec)
        
        active_scans[scan_id] = {"status": "processing", "progress": 0.5, "message": "Extracting features (ResNet-18)..."}
        extractor = get_feature_extractor()
        features = extractor.extract_features(spec_tensor)
        
        active_scans[scan_id] = {"status": "processing", "progress": 0.7, "message": "Quantum classification..."}
        classifier = get_quantum_classifier()
        
        # Predict using our highly trained Neural Network model directly
        trust_score, label, reasoning = classifier.predict(features, audio_signal=y, sr=sr)
        synthetic_prob = (100.0 - trust_score) / 100.0
        
        active_scans[scan_id] = {"status": "processing", "progress": 0.9, "message": "Computing spectral entropy..."}
        entropy = compute_spectral_entropy(y, sr)
        entropy_regions = find_high_entropy_regions(entropy, sr)
        entropy_tl = get_entropy_timeline(entropy, sr)
        
        processing_time = (time.time() - start_time) * 1000
        
        result_dict = {
            "id": scan_id,
            "filename": filename,
            "trust_score": round(trust_score, 1),
            "label": label,
            "synthetic_probability": round(synthetic_prob, 4),
            "entropy_regions": entropy_regions,
            "entropy_timeline": entropy_tl,
            "waveform_data": waveform,
            "spectrogram_base64": spec_b64,
            "processing_time_ms": round(processing_time, 1),
            "quantum_features": features.tolist(),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "complete",
            "reasoning": reasoning
        }
        
        await save_scan_result(result_dict)
        active_scans[scan_id] = {"status": "complete", "progress": 1.0, "message": "Analysis complete"}
        
    except Exception as e:
        active_scans[scan_id] = {"status": "error", "progress": 0, "message": str(e)}


@app.get("/api/scan/{scan_id}/status")
async def get_scan_status(scan_id: str):
    """Get the status of an async scan."""
    if scan_id in active_scans:
        return active_scans[scan_id]
    if scan_id in scan_results:
        return {"status": "complete", "progress": 1.0, "message": "Analysis complete"}
    raise HTTPException(status_code=404, detail="Scan not found")


@app.get("/api/scan/{scan_id}")
async def get_scan_result(scan_id: str):
    """Get the complete result of a scan."""
    if scan_id in scan_results:
        return scan_results[scan_id]
    if scan_id in active_scans:
        return {"status": active_scans[scan_id]["status"], "message": "Still processing"}
    raise HTTPException(status_code=404, detail="Scan not found")


@app.get("/api/history")
async def get_history(limit: int = 50, offset: int = 0):
    """Get scan history, ordered by most recent first."""
    all_results = list(scan_results.values())
    all_results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return {
        "total": len(all_results),
        "limit": limit,
        "offset": offset,
        "results": all_results[offset:offset + limit]
    }


@app.delete("/api/history/{scan_id}")
async def delete_scan(scan_id: str):
    """Delete a scan from history."""
    if scan_id in scan_results:
        del scan_results[scan_id]
        return {"message": "Scan deleted"}
    raise HTTPException(status_code=404, detail="Scan not found")


@app.delete("/api/history")
async def clear_history():
    """Clear all scan history."""
    scan_results.clear()
    return {"message": "History cleared"}


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
