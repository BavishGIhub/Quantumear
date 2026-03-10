"""
QuantumEAR — Pipeline Validation Tool
=======================================
Standalone script to verify the hybrid quantum-classical neural network.
Generates a dummy audio signal and runs it through the entire pipeline.
"""

import os
import sys
import numpy as np
import torch
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.audio_processor import normalize_audio, pad_or_truncate
from utils.spectrogram import generate_mel_spectrogram, spectrogram_to_tensor
from models.feature_extractor import get_feature_extractor
from models.quantum_classifier import get_quantum_classifier
from models.config import SAMPLE_RATE, AUDIO_DURATION

def run_test():
    print("🔊 Starting QuantumEAR Pipeline Validation...")
    
    # 1. Generate a synthetic audio signal (sine sweep)
    print("📝 Step 1: Generating test signal...")
    t = np.linspace(0, AUDIO_DURATION, int(SAMPLE_RATE * AUDIO_DURATION))
    # A simple frequency sweep to represent 'organic' complex signal
    y = np.sin(2 * np.pi * (100 + 500 * t) * t)
    y = normalize_audio(y)
    y = pad_or_truncate(y, SAMPLE_RATE, AUDIO_DURATION)
    print(f"   - Signal generated: {len(y)} samples @ {SAMPLE_RATE}Hz")

    # 2. Generate Spectrogram
    print("🖼️ Step 2: Generating Mel-Spectrogram...")
    mel_spec = generate_mel_spectrogram(y, SAMPLE_RATE)
    spec_tensor = spectrogram_to_tensor(mel_spec)
    print(f"   - Spectrogram tensor shape: {spec_tensor.shape}")

    # 3. Classical Feature Extraction (ResNet-18)
    print("🧠 Step 3: Extracting features via ResNet-18...")
    extractor = get_feature_extractor()
    features = extractor.extract_features(spec_tensor)
    print(f"   - Feature vector: {features}")

    # 4. Quantum Classification
    print("⚛️ Step 4: Running hybrid quantum classification...")
    classifier = get_quantum_classifier()
    synthetic_prob, label = classifier.predict(features)
    
    # 5. Output Results
    print("\n" + "="*40)
    print("🎯 PIPELINE RESULTS")
    print("="*40)
    print(f"Label:      {label.upper()}")
    print(f"Confidence: {synthetic_prob:.4f}")
    print(f"Trust:      {(1-synthetic_prob)*100:.1f}%")
    print("="*40)
    
    if synthetic_prob > 0.5:
        print("⚠️ Warning: Synthetic artifacts detected.")
    else:
        print("✅ Success: Audio signal appears organic.")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()
