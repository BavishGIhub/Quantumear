"""
Audio Augmentation Script
===========================
Simulates phone-call quality on existing human audio to prevent
false positives on real phone conversations.

Applies: noise, codec compression, bandwidth limiting, reverb.

Run:
    pip install pydub
    python scripts/augment_phone_quality.py
"""

import os
import sys
import random
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PROCESSED_DIR = PROJECT_ROOT / "datasets" / "processed"
HUMAN_DIR = PROCESSED_DIR / "human"
OUTPUT_DIR = PROCESSED_DIR / "human"  # Same dir — augmented files are still "human"

# How many augmented copies per original file
AUGMENT_RATIO = 0.3  # 30% of human files get augmented copies


def add_white_noise(y: np.ndarray, snr_db: float = 20.0) -> np.ndarray:
    """Add white noise at given SNR."""
    signal_power = np.mean(y ** 2)
    noise_power = signal_power / (10 ** (snr_db / 10))
    noise = np.random.normal(0, np.sqrt(noise_power), len(y))
    return (y + noise).astype(np.float32)


def lowpass_filter(y: np.ndarray, sr: int, cutoff: int = 3400) -> np.ndarray:
    """Simulate phone bandwidth (300-3400 Hz)."""
    try:
        from scipy.signal import butter, sosfilt
        # Phone bandpass: 300 Hz to 3400 Hz
        low = 300 / (sr / 2)
        high = min(cutoff / (sr / 2), 0.99)
        if low >= high:
            return y
        sos = butter(4, [low, high], btype='band', output='sos')
        return sosfilt(sos, y).astype(np.float32)
    except Exception:
        return y


def reduce_quality(y: np.ndarray, sr: int, target_sr: int = 8000) -> np.ndarray:
    """Downsample and upsample to simulate codec quality loss."""
    try:
        import librosa
        # Downsample to 8kHz (phone quality)
        y_low = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
        # Upsample back to original rate (quality is lost)
        y_back = librosa.resample(y_low, orig_sr=target_sr, target_sr=sr)
        # Ensure same length
        if len(y_back) > len(y):
            y_back = y_back[:len(y)]
        elif len(y_back) < len(y):
            y_back = np.pad(y_back, (0, len(y) - len(y_back)))
        return y_back.astype(np.float32)
    except Exception:
        return y


def add_room_reverb(y: np.ndarray, sr: int, decay: float = 0.3) -> np.ndarray:
    """Simple reverb simulation."""
    try:
        # Create a simple impulse response
        reverb_len = int(sr * 0.1)  # 100ms reverb
        impulse = np.zeros(reverb_len)
        impulse[0] = 1.0
        for i in range(1, reverb_len):
            impulse[i] = decay * impulse[i-1] * random.uniform(0.8, 1.0)
        
        from scipy.signal import fftconvolve
        y_reverb = fftconvolve(y, impulse, mode='same')
        # Normalize
        max_val = np.max(np.abs(y_reverb))
        if max_val > 0:
            y_reverb = y_reverb / max_val * np.max(np.abs(y))
        return y_reverb.astype(np.float32)
    except Exception:
        return y


def apply_random_augmentation(y: np.ndarray, sr: int) -> np.ndarray:
    """Apply a random combination of phone-quality degradations."""
    augmentations = []
    
    # Always apply bandwidth limiting (phone quality)
    y = lowpass_filter(y, sr, cutoff=random.choice([3400, 4000, 5000]))
    augmentations.append("bandpass")
    
    # 70% chance: add noise
    if random.random() < 0.7:
        snr = random.choice([10, 15, 20, 25])
        y = add_white_noise(y, snr_db=snr)
        augmentations.append(f"noise_snr{snr}")
    
    # 50% chance: reduce quality (codec simulation)
    if random.random() < 0.5:
        target_sr = random.choice([8000, 11025, 16000])
        y = reduce_quality(y, sr, target_sr)
        augmentations.append(f"codec_{target_sr}")
    
    # 30% chance: add reverb
    if random.random() < 0.3:
        y = add_room_reverb(y, sr, decay=random.uniform(0.2, 0.5))
        augmentations.append("reverb")
    
    return y


def main():
    import soundfile as sf
    
    # Find all human WAV files
    human_files = sorted(HUMAN_DIR.glob("*.wav"))
    
    if not human_files:
        print("❌ No human WAV files found in", HUMAN_DIR)
        return
    
    # Select random subset to augment
    num_to_augment = int(len(human_files) * AUGMENT_RATIO)
    files_to_augment = random.sample(human_files, min(num_to_augment, len(human_files)))
    
    print("=" * 60)
    print("📞  Phone-Quality Audio Augmentation")
    print(f"    Source    : {HUMAN_DIR}")
    print(f"    Human files: {len(human_files)}")
    print(f"    Augmenting : {len(files_to_augment)} files ({AUGMENT_RATIO*100:.0f}%)")
    print("=" * 60)
    
    created = 0
    errors = 0
    
    # Find max existing index
    existing_indices = []
    for f in HUMAN_DIR.glob("*.wav"):
        try:
            idx = int(f.stem.split("_")[1])
            existing_indices.append(idx)
        except (IndexError, ValueError):
            pass
    next_idx = max(existing_indices) + 1 if existing_indices else 0
    
    for i, filepath in enumerate(files_to_augment):
        try:
            y, sr = sf.read(filepath, dtype='float32')
            
            # Apply random phone-quality degradation
            y_aug = apply_random_augmentation(y, sr)
            
            # Save augmented file
            out_name = f"clip_{next_idx:06d}.wav"
            out_path = HUMAN_DIR / out_name
            sf.write(str(out_path), y_aug, sr)
            
            next_idx += 1
            created += 1
            
            if (i + 1) % 100 == 0 or i == 0:
                print(f"  [{i+1:>5}/{len(files_to_augment)}]  {filepath.name} → {out_name}")
                
        except Exception as e:
            errors += 1
            if errors <= 3:
                print(f"  ⚠️  Error: {e}")
    
    print(f"\n{'=' * 60}")
    print(f"✅  Created {created} augmented phone-quality clips")
    print(f"    Total human clips now: {len(list(HUMAN_DIR.glob('*.wav')))}")
    if errors:
        print(f"    ⚠️  {errors} errors")
    print(f"{'=' * 60}")
    print(f"\n    Next: Re-run prepare_dataset.py, then retrain!")


if __name__ == "__main__":
    main()
