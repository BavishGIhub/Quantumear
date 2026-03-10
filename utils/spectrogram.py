"""
Spectrogram Generator
======================
Generates Mel-Spectrograms from audio signals for CNN feature extraction.
Outputs both visual spectrograms (for display) and tensor spectrograms (for model input).
"""

import numpy as np
import librosa
import librosa.display
from PIL import Image
import io
import base64
from typing import Tuple, Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.config import (
    N_MELS, N_FFT, HOP_LENGTH, SAMPLE_RATE,
    SPECTROGRAM_WIDTH, SPECTROGRAM_HEIGHT
)


def generate_mel_spectrogram(y: np.ndarray, sr: int = SAMPLE_RATE) -> np.ndarray:
    """
    Generate a Mel-Spectrogram from raw audio signal.
    
    Args:
        y: Audio time series
        sr: Sample rate
    
    Returns:
        Mel-spectrogram as 2D numpy array (in dB scale)
    """
    try:
        mel_spec = librosa.feature.melspectrogram(
            y=y,
            sr=sr,
            n_mels=N_MELS,
            n_fft=N_FFT,
            hop_length=HOP_LENGTH,
            power=2.0
        )
        # Convert to dB scale for better dynamic range
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        return mel_spec_db
    except Exception as e:
        print(f"⚠️  Error generating mel-spectrogram: {e}")
        # Return a blank spectrogram as fallback
        return np.zeros((N_MELS, 128))


def spectrogram_to_image(mel_spec_db: np.ndarray) -> Image.Image:
    """
    Convert Mel-spectrogram array to a PIL Image for ResNet input.
    Normalizes to [0, 255] and resizes to 224x224.
    """
    try:
        # Normalize to [0, 1]
        spec_norm = (mel_spec_db - mel_spec_db.min()) / (mel_spec_db.max() - mel_spec_db.min() + 1e-8)
        # Convert to uint8
        spec_uint8 = (spec_norm * 255).astype(np.uint8)
        # Create image and resize
        img = Image.fromarray(spec_uint8)
        img = img.resize((SPECTROGRAM_WIDTH, SPECTROGRAM_HEIGHT), Image.BICUBIC)
        # Convert to RGB (3 channels for ResNet)
        img_rgb = Image.merge('RGB', [img, img, img])
        return img_rgb
    except Exception as e:
        print(f"⚠️  Error converting spectrogram to image: {e}")
        # Return blank image as fallback
        return Image.new('RGB', (SPECTROGRAM_WIDTH, SPECTROGRAM_HEIGHT), color='black')


def spectrogram_to_tensor(mel_spec_db: np.ndarray) -> np.ndarray:
    """
    Convert Mel-spectrogram to a 3-channel tensor ready for ResNet.
    Output shape: (3, 224, 224)
    """
    try:
        img = spectrogram_to_image(mel_spec_db)
        tensor = np.array(img, dtype=np.float32) / 255.0
        # Transpose from (H, W, C) to (C, H, W) for PyTorch
        tensor = tensor.transpose(2, 0, 1)
        # Normalize with ImageNet stats
        mean = np.array([0.485, 0.456, 0.406]).reshape(3, 1, 1)
        std = np.array([0.229, 0.224, 0.225]).reshape(3, 1, 1)
        tensor = (tensor - mean) / std
        return tensor
    except Exception as e:
        print(f"⚠️  Error converting spectrogram to tensor: {e}")
        # Return zeros as fallback
        return np.zeros((3, SPECTROGRAM_HEIGHT, SPECTROGRAM_WIDTH), dtype=np.float32)


def spectrogram_to_base64(mel_spec_db: np.ndarray) -> Optional[str]:
    """
    Convert spectrogram to base64-encoded PNG for API response.
    Uses a custom colormap for cybersecurity aesthetic.
    """
    try:
        # Check for valid input
        if mel_spec_db is None or mel_spec_db.size == 0:
            return None
        
        # Normalize
        spec_min = mel_spec_db.min()
        spec_max = mel_spec_db.max()
        if spec_max - spec_min < 1e-8:
            return None
            
        spec_norm = (mel_spec_db - spec_min) / (spec_max - spec_min)
        
        # Apply cyan-purple colormap (cybersecurity aesthetic)
        h, w = spec_norm.shape
        colored = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Vectorized colormap application for speed
        for i in range(h):
            for j in range(w):
                val = spec_norm[i, j]
                # Dark blue → Cyan → Purple → White gradient
                if val < 0.33:
                    r = int(val * 3 * 20)
                    g = int(val * 3 * 255)
                    b = int(val * 3 * 200 + 55)
                elif val < 0.66:
                    t = (val - 0.33) * 3
                    r = int(20 + t * 180)
                    g = int(255 - t * 100)
                    b = int(255)
                else:
                    t = (val - 0.66) * 3
                    r = int(200 + t * 55)
                    g = int(155 + t * 100)
                    b = int(255)
                
                colored[i, j] = [r, g, b]
        
        # Flip vertically (low freq at bottom)
        colored = colored[::-1]
        
        img = Image.fromarray(colored)
        img = img.resize((600, 300), Image.BICUBIC)
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"⚠️  Error generating base64 spectrogram: {e}")
        return None
