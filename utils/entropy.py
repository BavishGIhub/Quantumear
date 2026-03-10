"""
Spectral Entropy Calculator
=============================
Computes spectral entropy across time frames to identify regions
where AI-generated audio shows characteristic "glitches" — areas
of unusually high or low spectral entropy compared to natural speech.
"""

import numpy as np
from scipy.signal import stft
from typing import List, Tuple

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.config import (
    ENTROPY_WINDOW_SIZE, ENTROPY_HOP, HIGH_ENTROPY_THRESHOLD, SAMPLE_RATE
)


def compute_spectral_entropy(y: np.ndarray, sr: int = SAMPLE_RATE) -> np.ndarray:
    """
    Compute spectral entropy for each time frame using STFT.
    
    Spectral entropy measures the "flatness" of the spectrum.
    - High entropy → noise-like (flat spectrum)
    - Low entropy → tonal (peaked spectrum)
    
    AI-generated audio often shows abnormal entropy patterns
    in transition regions between phonemes.
    
    Args:
        y: Audio time series
        sr: Sample rate
    
    Returns:
        Array of entropy values per time frame (normalized 0-1)
    """
    # Compute STFT
    f, t, Zxx = stft(y, fs=sr, nperseg=ENTROPY_WINDOW_SIZE, noverlap=ENTROPY_WINDOW_SIZE - ENTROPY_HOP)
    
    # Power spectrum
    power = np.abs(Zxx) ** 2
    
    # Normalize each frame to create probability distribution
    frame_sums = np.sum(power, axis=0, keepdims=True)
    frame_sums = np.maximum(frame_sums, 1e-10)  # Prevent division by zero
    prob = power / frame_sums
    
    # Shannon entropy per frame
    # H = -Σ p(f) * log2(p(f))
    log_prob = np.log2(prob + 1e-10)
    entropy = -np.sum(prob * log_prob, axis=0)
    
    # Normalize to [0, 1] using max possible entropy
    max_entropy = np.log2(power.shape[0])
    entropy_normalized = entropy / max_entropy
    
    return entropy_normalized


def find_high_entropy_regions(
    entropy: np.ndarray,
    sr: int = SAMPLE_RATE,
    threshold: float = HIGH_ENTROPY_THRESHOLD,
    min_duration: float = 0.05  # minimum 50ms region
) -> List[Tuple[float, float]]:
    """
    Find contiguous regions of high spectral entropy.
    
    These are potential "glitch" areas where AI synthesis
    introduced spectral artifacts.
    
    Args:
        entropy: Array of per-frame entropy values
        sr: Sample rate
        threshold: Entropy threshold (0-1)
        min_duration: Minimum region duration in seconds
    
    Returns:
        List of (start_time, end_time) tuples in seconds
    """
    # Time per frame
    frame_duration = ENTROPY_HOP / sr
    min_frames = int(min_duration / frame_duration)
    
    high_mask = entropy > threshold
    regions = []
    
    i = 0
    while i < len(high_mask):
        if high_mask[i]:
            start = i
            while i < len(high_mask) and high_mask[i]:
                i += 1
            end = i
            
            if (end - start) >= min_frames:
                start_time = round(start * frame_duration, 3)
                end_time = round(end * frame_duration, 3)
                regions.append((start_time, end_time))
        else:
            i += 1
    
    return regions


def get_entropy_timeline(entropy: np.ndarray, sr: int = SAMPLE_RATE, num_points: int = 200) -> dict:
    """
    Create a downsampled entropy timeline for frontend visualization.
    
    Returns:
        Dict with 'times' and 'values' arrays
    """
    frame_duration = ENTROPY_HOP / sr
    total_time = len(entropy) * frame_duration
    
    if len(entropy) <= num_points:
        times = [round(i * frame_duration, 3) for i in range(len(entropy))]
        values = entropy.tolist()
    else:
        indices = np.linspace(0, len(entropy) - 1, num_points, dtype=int)
        times = [round(idx * frame_duration, 3) for idx in indices]
        values = entropy[indices].tolist()
    
    return {
        "times": times,
        "values": values,
        "threshold": HIGH_ENTROPY_THRESHOLD,
        "total_duration": round(total_time, 3)
    }
