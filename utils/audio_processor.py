"""
Audio Processor
================
Handles audio file loading, normalization, format conversion,
and basic preprocessing before spectrogram generation.
Uses universal loader for maximum format compatibility.
"""

import io
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Tuple, Optional

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.config import SAMPLE_RATE, AUDIO_DURATION

# Import universal loader
try:
    from utils.audio_loader import load_audio_universal, detect_audio_format
    UNIVERSAL_LOADER_AVAILABLE = True
except ImportError:
    UNIVERSAL_LOADER_AVAILABLE = False
    print("⚠️  Universal loader not available, using basic loading")


def load_audio(file_path: str, sr: int = SAMPLE_RATE, duration: float = AUDIO_DURATION) -> Tuple[np.ndarray, int]:
    """
    Load and normalize an audio file using the universal loader to handle AAC/MP3/M4A.
    """
    try:
        with open(file_path, 'rb') as f:
            audio_bytes = f.read()
        return load_audio_from_bytes(audio_bytes, sr=sr, duration=duration, filename=Path(file_path).name)
    except Exception as e:
        raise RuntimeError(f"Universal loader failed for {file_path}: {e}")


def load_audio_from_bytes(audio_bytes: bytes, sr: int = SAMPLE_RATE, duration: float = AUDIO_DURATION, filename: Optional[str] = None) -> Tuple[np.ndarray, int]:
    """
    Load audio from bytes with universal format support.
    Uses multiple fallback strategies for maximum compatibility.
    """
    # Try universal loader first (best format support)
    if UNIVERSAL_LOADER_AVAILABLE:
        try:
            detected_format = detect_audio_format(audio_bytes)
            print(f"🔍 Detected audio format: {detected_format}")
            
            y, sr_out = load_audio_universal(audio_bytes, sr=sr, duration=duration, filename=filename)
            
            # Normalize
            max_val = np.max(np.abs(y))
            if max_val > 0:
                y = y / max_val
            
            return y, sr_out
            
        except Exception as e:
            print(f"⚠️  Universal loader failed: {e}, trying fallbacks...")
    
    # Fallback 1: Try librosa directly
    try:
        audio_io = io.BytesIO(audio_bytes)
        y, sr_orig = librosa.load(audio_io, sr=sr, mono=True, duration=duration)
        
        # Pad or truncate
        target_length = int(sr * duration)
        if len(y) < target_length:
            y = np.pad(y, (0, target_length - len(y)), mode='constant')
        elif len(y) > target_length:
            y = y[:target_length]
        
        return y, sr
        
    except Exception as e:
        print(f"⚠️  Librosa fallback failed: {e}")
    
    # Fallback 2: Try soundfile
    try:
        audio_io = io.BytesIO(audio_bytes)
        y, sr_orig = sf.read(audio_io, dtype='float32', always_2d=False)
        
        # Convert to mono
        if len(y.shape) > 1:
            y = y.mean(axis=1)
        
        # Resample if needed
        if sr_orig != sr:
            y = librosa.resample(y, orig_sr=sr_orig, target_sr=sr, res_type='kaiser_fast')
        
        # Pad or truncate
        target_length = int(sr * duration)
        if len(y) < target_length:
            y = np.pad(y, (0, target_length - len(y)), mode='constant')
        elif len(y) > target_length:
            y = y[:target_length]
        
        # Normalize
        max_val = np.max(np.abs(y))
        if max_val > 0:
            y = y / max_val
        
        return y, sr
        
    except Exception as e:
        raise RuntimeError(
            f"Failed to load audio. All strategies failed. "
            f"Please ensure ffmpeg is installed for best format support. "
            f"Last error: {e}"
        )


def normalize_audio(y: np.ndarray) -> np.ndarray:
    """
    Peak normalize audio to [-1, 1] range.
    Prevents clipping and ensures consistent input levels.
    """
    max_val = np.max(np.abs(y))
    if max_val > 0:
        y = y / max_val
    return y


def pad_or_truncate(y: np.ndarray, sr: int, duration: float) -> np.ndarray:
    """
    Pad with zeros or truncate audio to exact target duration.
    Ensures consistent tensor sizes for the neural network.
    """
    target_length = int(sr * duration)
    if len(y) < target_length:
        y = np.pad(y, (0, target_length - len(y)), mode='constant')
    else:
        y = y[:target_length]
    return y


def get_audio_info(file_path: str) -> dict:
    """Get metadata about an audio file."""
    try:
        info = sf.info(file_path)
        return {
            "sample_rate": info.samplerate,
            "channels": info.channels,
            "duration": info.duration,
            "format": info.format,
            "subtype": info.subtype,
        }
    except Exception as e:
        # Fallback to librosa
        try:
            y, sr = librosa.load(file_path, sr=None, mono=True, duration=1.0)
            duration = librosa.get_duration(path=file_path)
            return {
                "sample_rate": sr,
                "channels": 1,  # librosa converts to mono
                "duration": duration,
                "format": "unknown",
                "subtype": "unknown",
            }
        except Exception as e2:
            raise RuntimeError(f"Cannot read audio info: {e}")


def get_waveform_data(y: np.ndarray, num_points: int = 500) -> list:
    """
    Downsample waveform for frontend visualization.
    Returns evenly spaced amplitude points.
    """
    if len(y) <= num_points:
        return y.tolist()
    
    # Use max-pooling style downsampling to preserve peaks
    chunk_size = len(y) // num_points
    points = []
    for i in range(num_points):
        chunk = y[i * chunk_size:(i + 1) * chunk_size]
        # Alternate between max and min to preserve waveform shape
        if i % 2 == 0:
            points.append(float(np.max(chunk)))
        else:
            points.append(float(np.min(chunk)))
    return points
