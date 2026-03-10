"""
Universal Audio Loader
======================
Handles ALL audio formats with proper format detection and decoding.
Uses multiple fallback strategies for maximum compatibility.
"""

import io
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Tuple, Optional, Dict
import struct


def detect_audio_format(audio_bytes: bytes) -> str:
    """
    Detect audio format from file header/magic bytes.
    More reliable than extension-based detection.
    """
    if len(audio_bytes) < 12:
        return "unknown"
    
    # Check magic numbers
    header = audio_bytes[:12]
    
    # WAV: RIFF....WAVE
    if header[:4] == b'RIFF' and header[8:12] == b'WAVE':
        return "wav"
    
    # MP3: ID3 or MPEG sync word
    if header[:3] == b'ID3' or (header[0] == 0xFF and (header[1] & 0xE0) == 0xE0):
        return "mp3"
    
    # FLAC: fLaC
    if header[:4] == b'fLaC':
        return "flac"
    
    # OGG: OggS
    if header[:4] == b'OggS':
        # Could be OGG Vorbis, Opus, or FLAC-in-OGG
        return "ogg"
    
    # M4A/AAC: ftyp or mdat (MP4 container)
    if header[4:8] == b'ftyp' or header[4:8] == b'mdat':
        return "m4a"
    
    # WMA: ASF header
    if header[:16] == b'\x30\x26\xB2\x75\x8E\x66\xCF\x11\xA6\xD9\x00\xAA\x00\x62\xCE\x6C':
        return "wma"
    
    # AAC raw (ADTS): 0xFFF sync word
    if (header[0] == 0xFF) and ((header[1] & 0xF0) == 0xF0):
        return "aac"
    
    return "unknown"


def load_audio_universal(
    audio_bytes: bytes, 
    sr: int = 22050, 
    duration: float = 5.0,
    filename: Optional[str] = None
) -> Tuple[np.ndarray, int]:
    """
    Universal audio loader with format auto-detection and multiple fallbacks.
    
    Args:
        audio_bytes: Raw audio file bytes
        sr: Target sample rate
        duration: Target duration
        filename: Optional filename for extension hint
    
    Returns:
        (audio_signal, sample_rate)
    """
    detected_format = detect_audio_format(audio_bytes)
    
    # Strategy 1: Try librosa with format hint
    try:
        audio_io = io.BytesIO(audio_bytes)
        
        # For M4A/AAC, librosa might need special handling
        if detected_format in ["m4a", "aac"]:
            # Try with soundfile first (supports MP4 via ffmpeg)
            try:
                audio_io.seek(0)
                y, sr_orig = sf.read(audio_io, dtype='float32', always_2d=False)
                
                # Convert to mono if stereo
                if len(y.shape) > 1:
                    y = y.mean(axis=1)
                
                # Resample if needed
                if sr_orig != sr:
                    y = librosa.resample(y, orig_sr=sr_orig, target_sr=sr, res_type='kaiser_fast')
                
                # Truncate/pad
                max_samples = int(sr * duration)
                if len(y) > max_samples:
                    y = y[:max_samples]
                elif len(y) < max_samples:
                    y = np.pad(y, (0, max_samples - len(y)), mode='constant')
                
                # Normalize
                max_val = np.max(np.abs(y))
                if max_val > 0:
                    y = y / max_val
                
                return y, sr
                
            except Exception as e:
                print(f"Soundfile fallback failed for {detected_format}: {e}")
        
        # Standard librosa load
        audio_io.seek(0)
        y, sr_orig = librosa.load(audio_io, sr=sr, mono=True, duration=duration)
        return y, sr
        
    except Exception as e:
        print(f"Librosa load failed: {e}")
        
    # Strategy 1.5: Try PyAV (contains built-in FFmpeg, works without system installation)
    try:
        import av
        audio_io = io.BytesIO(audio_bytes)
        container = av.open(audio_io)
        
        # Extract audio stream
        audio_stream = next(s for s in container.streams if s.type == 'audio')
        
        # Resample to target sr and mono format
        resampler = av.AudioResampler(format='fltp', layout='mono', rate=sr)
        
        samples = []
        for frame in container.decode(audio_stream):
            # Pass through resampler
            frame.pts = None
            resampled_frames = resampler.resample(frame)
            for rf in resampled_frames:
                # Convert frame data to numpy array
                arr = rf.to_ndarray()
                samples.append(arr.flatten())
                
        # Flush resampler
        for rf in resampler.resample(None):
            samples.append(rf.to_ndarray().flatten())
            
        if samples:
            y = np.concatenate(samples)
            
            # Truncate/pad
            max_samples = int(sr * duration)
            if len(y) > max_samples:
                y = y[:max_samples]
            elif len(y) < max_samples:
                y = np.pad(y, (0, max_samples - len(y)), mode='constant')
                
            # Normalize
            max_val = np.max(np.abs(y))
            if max_val > 0:
                y = y / max_val
                
            return y, sr
            
    except ImportError:
        print("av not available for fallback")
    except Exception as e:
        print(f"PyAV fallback failed: {e}")
    
    # Strategy 2: Try pydub as ultimate fallback (requires system ffmpeg)
    try:
        from pydub import AudioSegment
        audio_io = io.BytesIO(audio_bytes)
        audio = AudioSegment.from_file(audio_io)
        
        # Convert to target sample rate
        if audio.frame_rate != sr:
            audio = audio.set_frame_rate(sr)
        
        # Convert to mono
        if audio.channels > 1:
            audio = audio.set_channels(1)
        
        # Get raw samples
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
        
        # Normalize based on bit depth
        max_val = float(2 ** (audio.sample_width * 8 - 1))
        samples = samples / max_val
        
        # Truncate/pad
        max_samples = int(sr * duration)
        if len(samples) > max_samples:
            samples = samples[:max_samples]
        elif len(samples) < max_samples:
            samples = np.pad(samples, (0, max_samples - len(samples)), mode='constant')
        
        return samples, sr
        
    except ImportError:
        print("pydub not available for fallback")
    except Exception as e:
        print(f"pydub fallback failed: {e}")
    
    # Strategy 3: Raw PCM interpretation (last resort)
    if detected_format == "unknown" and len(audio_bytes) > 44:
        try:
            # Try to interpret as raw 16-bit PCM
            # Skip first 44 bytes (common header size)
            raw_data = audio_bytes[44:]
            if len(raw_data) % 2 == 0:
                samples = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32)
                samples = samples / 32768.0  # Normalize 16-bit
                
                # Resample if we have too many samples (assume 44.1k or 48k)
                assumed_sr = 44100
                if len(samples) > int(assumed_sr * duration):
                    samples = samples[:int(assumed_sr * duration)]
                    # Simple downsampling
                    samples = samples[::int(assumed_sr / sr)]
                
                return samples, sr
        except Exception as e:
            print(f"Raw PCM fallback failed: {e}")
    
    # All strategies failed
    raise RuntimeError(
        f"Could not load audio format: {detected_format}. "
        f"Supported formats: WAV, MP3, FLAC, OGG, M4A, AAC, WMA. "
        f"Consider installing ffmpeg for better format support."
    )


def get_audio_info_advanced(audio_bytes: bytes) -> Dict:
    """Get detailed audio file information."""
    info = {
        "detected_format": detect_audio_format(audio_bytes),
        "size_bytes": len(audio_bytes),
        "duration_estimate": None,
        "sample_rate": None,
        "channels": None,
    }
    
    try:
        # Try to get accurate info
        audio_io = io.BytesIO(audio_bytes)
        try:
            sf_info = sf.info(audio_io)
            info["duration_estimate"] = sf_info.duration
            info["sample_rate"] = sf_info.samplerate
            info["channels"] = sf_info.channels
            info["subtype"] = sf_info.subtype
            info["format"] = sf_info.format
        except:
            pass
    except:
        pass
    
    return info
