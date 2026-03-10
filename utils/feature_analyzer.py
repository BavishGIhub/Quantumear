"""
Advanced Audio Feature Extractor
==================================
Extracts comprehensive audio features for deepfake detection.
Combines traditional audio features with spectral analysis.
"""

import numpy as np
import librosa
from typing import Dict, List, Tuple


def extract_advanced_features(y: np.ndarray, sr: int = 22050) -> Dict[str, np.ndarray]:
    """
    Extract comprehensive audio features for AI vs Human detection.
    
    Returns a dictionary of features that can distinguish between:
    - Natural human voice characteristics
    - AI-generated artifacts (Spectral inconsistencies, phase issues, etc.)
    """
    features = {}
    
    # 1. MFCC Features (Mel-Frequency Cepstral Coefficients)
    # Humans have consistent MFCC patterns, AI often shows irregularities
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    features['mfcc_mean'] = np.mean(mfcc, axis=1)
    features['mfcc_std'] = np.std(mfcc, axis=1)
    features['mfcc_delta'] = np.mean(np.diff(mfcc, axis=1), axis=1)
    
    # 2. Spectral Features
    # AI-generated audio often has unnatural spectral characteristics
    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    
    features['spectral_centroid_mean'] = np.mean(spectral_centroids)
    features['spectral_centroid_std'] = np.std(spectral_centroids)
    features['spectral_rolloff_mean'] = np.mean(spectral_rolloff)
    features['spectral_rolloff_std'] = np.std(spectral_rolloff)
    features['spectral_bandwidth_mean'] = np.mean(spectral_bandwidth)
    features['spectral_bandwidth_std'] = np.std(spectral_bandwidth)
    features['spectral_contrast_mean'] = np.mean(spectral_contrast, axis=1)
    features['spectral_contrast_std'] = np.std(spectral_contrast, axis=1)
    
    # 3. Rhythm and Temporal Features
    # AI audio often has unnatural timing
    zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
    features['zcr_mean'] = np.mean(zero_crossing_rate)
    features['zcr_std'] = np.std(zero_crossing_rate)
    
    # 4. Chroma Features (Pitch Class Profile)
    # Human voice has natural pitch variations
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    features['chroma_mean'] = np.mean(chroma, axis=1)
    features['chroma_std'] = np.std(chroma, axis=1)
    
    # 5. Harmonic-Percussive Separation
    # AI audio often struggles with natural harmonic content
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    features['harmonic_ratio'] = np.array([np.sum(y_harmonic**2) / (np.sum(y**2) + 1e-10)])
    features['percussive_ratio'] = np.array([np.sum(y_percussive**2) / (np.sum(y**2) + 1e-10)])
    
    # 6. Mel Spectrogram Statistics
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    features['mel_spec_mean'] = np.mean(mel_spec_db, axis=1)
    features['mel_spec_std'] = np.std(mel_spec_db, axis=1)
    features['mel_spec_flatness'] = np.array([np.mean(np.var(mel_spec_db, axis=1))])
    
    # 7. Voice-specific features (if applicable)
    # Fundamental frequency (F0) analysis
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), 
                                                   fmax=librosa.note_to_hz('C7'))
    if f0 is not None and not np.all(np.isnan(f0)):
        valid_f0 = f0[~np.isnan(f0)]
        if len(valid_f0) > 0:
            features['f0_mean'] = np.array([np.mean(valid_f0)])
            features['f0_std'] = np.array([np.std(valid_f0)])
            features['f0_range'] = np.array([np.max(valid_f0) - np.min(valid_f0)])
        else:
            features['f0_mean'] = np.array([0.0])
            features['f0_std'] = np.array([0.0])
            features['f0_range'] = np.array([0.0])
    else:
        features['f0_mean'] = np.array([0.0])
        features['f0_std'] = np.array([0.0])
        features['f0_range'] = np.array([0.0])
    
    return features


def features_to_vector(features: Dict[str, np.ndarray]) -> np.ndarray:
    """
    Convert feature dictionary to a flat vector for classification.
    """
    vectors = []
    
    # Concatenate all features in a consistent order
    feature_order = [
        'mfcc_mean', 'mfcc_std', 'mfcc_delta',
        'spectral_centroid_mean', 'spectral_centroid_std',
        'spectral_rolloff_mean', 'spectral_rolloff_std',
        'spectral_bandwidth_mean', 'spectral_bandwidth_std',
        'spectral_contrast_mean', 'spectral_contrast_std',
        'zcr_mean', 'zcr_std',
        'chroma_mean', 'chroma_std',
        'harmonic_ratio', 'percussive_ratio',
        'mel_spec_mean', 'mel_spec_std', 'mel_spec_flatness',
        'f0_mean', 'f0_std', 'f0_range'
    ]
    
    for key in feature_order:
        if key in features:
            vectors.append(np.array(features[key]).flatten())
    
    return np.concatenate(vectors)


def detect_ai_artifacts(y: np.ndarray, sr: int = 22050) -> Dict[str, float]:
    """
    Detect AI generation artifacts tuned for modern neural TTS
    (ElevenLabs, Humme, XTTS, Bark, etc.).
    
    Returns artifact scores where HIGHER = MORE LIKELY AI-GENERATED.
    Score range: 0.0 (human-like) to 1.0 (AI-like).
    """
    artifacts = {}
    
    stft_complex = librosa.stft(y)
    stft_mag = np.abs(stft_complex)
    phase = np.angle(stft_complex)
    
    # ── 1. Spectral flux ratio (AI transitions are unnaturally smooth) ──
    # Normalize by mean magnitude so recording level doesn't affect score
    spec_diff = np.diff(stft_mag, axis=1)
    mean_mag = np.mean(stft_mag) + 1e-10
    norm_flux = np.mean(np.abs(spec_diff)) / mean_mag
    # Human: norm_flux typically 0.25-0.80; AI (ElevenLabs): 0.05-0.20
    # Score: below 0.18 = very AI-like (1.0), above 0.35 = human-like (0.0)
    artifacts['spectral_smoothness'] = float(np.clip((0.35 - norm_flux) / (0.35 - 0.10), 0, 1))
    
    # ── 2. Phase irregularity (human phase is noisier) ──
    phase_diff = np.diff(phase, axis=1)
    mean_phase_jump = np.mean(np.abs(phase_diff)) / np.pi
    # Human: mean_phase_jump ~ 0.45-0.65; AI: ~ 0.25-0.40
    # Low phase jump = AI-like
    artifacts['phase_predictability'] = float(np.clip((0.40 - mean_phase_jump) / (0.40 - 0.20), 0, 1))
    
    # ── 3. Energy coefficient of variation (AI is too temporally flat) ──
    frame_energy = np.sum(stft_mag**2, axis=0)
    if np.mean(frame_energy) > 1e-10:
        cv = np.std(frame_energy) / (np.mean(frame_energy) + 1e-10)
        # Human CV: typically 0.6-2.0; AI: 0.1-0.5
        # Low CV = AI-like
        artifacts['temporal_regularity'] = float(np.clip((0.55 - cv) / (0.55 - 0.10), 0, 1))
    else:
        artifacts['temporal_regularity'] = 0.5
    
    # ── 4. Harmonic over-purity (ElevenLabs/Humme are "too clean") ──
    harmonic, percussive = librosa.effects.hpss(y)
    h_energy = np.sum(harmonic**2)
    total_energy = np.sum(y**2) + 1e-10
    harmonic_ratio = h_energy / total_energy
    # Human voice: 0.50-0.82 (wide variation); AI: 0.88-0.98
    # Only score high if clearly above human range (> 0.83)
    artifacts['harmonic_overpurity'] = float(np.clip((harmonic_ratio - 0.83) / 0.12, 0, 1))
    
    # ── 5. Pitch coefficient of variation (AI F0 is unnaturally steady) ──
    f0, _, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'),
                                        fmax=librosa.note_to_hz('C7'))
    if f0 is not None and not np.all(np.isnan(f0)):
        valid_f0 = f0[~np.isnan(f0)]
        if len(valid_f0) > 15:
            f0_cv = np.std(valid_f0) / (np.mean(valid_f0) + 1e-10)
            # Human CV: 0.05-0.25 (calm speakers can be 0.05 naturally)
            # AI CV: 0.005-0.04
            # Only fire if clearly in AI range (< 0.04)
            artifacts['pitch_overstability'] = float(np.clip((0.05 - f0_cv) / (0.05 - 0.008), 0, 1))
            
            # Micro-jitter: human voice always has some frame-to-frame pitch flutter
            f0_diff = np.abs(np.diff(valid_f0))
            jitter = np.mean(f0_diff) / (np.mean(valid_f0) + 1e-10)
            # Human jitter: 0.008-0.035; AI: 0.001-0.006
            # Only fire if clearly in AI range (< 0.006)
            artifacts['jitter_deficit'] = float(np.clip((0.008 - jitter) / (0.008 - 0.001), 0, 1))
        else:
            artifacts['pitch_overstability'] = 0.3
            artifacts['jitter_deficit'] = 0.3
    else:
        artifacts['pitch_overstability'] = 0.3
        artifacts['jitter_deficit'] = 0.3
    
    # ── 6. Spectral bandwidth coefficient of variation ──
    bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
    bw_cv = np.std(bandwidth) / (np.mean(bandwidth) + 1e-10)
    # Human: bw_cv 0.15-0.50; AI: 0.03-0.12
    # Only fire if clearly uniform (< 0.10)
    artifacts['bandwidth_uniformity'] = float(np.clip((0.12 - bw_cv) / (0.12 - 0.03), 0, 1))
    
    # ── 7. Spectral flatness frame-to-frame variation ──
    flatness = librosa.feature.spectral_flatness(y=y)[0]
    flatness_std = np.std(flatness)
    # Human flatness_std: 0.04-0.15; AI: 0.005-0.025
    # Only fire if clearly in AI range (< 0.025)
    artifacts['flatness_consistency'] = float(np.clip((0.030 - flatness_std) / (0.030 - 0.005), 0, 1))
    
    # ── 8. High-frequency energy ratio ──
    n_fft = stft_mag.shape[0]
    hf_start = int(n_fft * 0.75)
    hf_energy = np.mean(stft_mag[hf_start:, :])
    lf_energy = np.mean(stft_mag[:hf_start, :]) + 1e-10
    hf_ratio = hf_energy / lf_energy
    # Human: hf_ratio 0.08-0.35 (room acoustics vary); AI: 0.01-0.06
    # Only fire if clearly deficient (< 0.06)
    artifacts['hf_deficit'] = float(np.clip((0.07 - hf_ratio) / (0.07 - 0.01), 0, 1))

    # ── 9. Codec compression detection ──
    # Phone/call recordings compressed with G.711, AMR, Opus, WhatsApp voice
    # naturally suppress HF, reduce spectral flux, and flatten pitch jitter.
    # These recordings look like AI on features 1,5,6,8 — we must compensate.
    #
    # Compression signatures:
    #   - Hard HF cutoff: energy above 3.5kHz drops to near zero
    #   - Narrow bandwidth: most energy below 4kHz (telephony = 300-3400 Hz)
    #   - Very low noise floor above cutoff frequency
    freqs = librosa.fft_frequencies(sr=sr, n_fft=(stft_mag.shape[0] - 1) * 2)
    cutoff_bin_3k = int(np.searchsorted(freqs, 3500))
    cutoff_bin_4k = int(np.searchsorted(freqs, 4000))
    if cutoff_bin_4k < stft_mag.shape[0] and cutoff_bin_3k > 0:
        energy_below_4k = np.mean(stft_mag[:cutoff_bin_4k, :])
        energy_above_4k = np.mean(stft_mag[cutoff_bin_4k:, :]) + 1e-10
        telephony_ratio = energy_below_4k / energy_above_4k
        # Telephony codec: ratio > 20 (almost all energy below 4kHz)
        # Wideband human: ratio 2-8
        is_compressed = telephony_ratio > 15.0
    else:
        is_compressed = False

    if is_compressed:
        # These features are unreliable for compressed recordings —
        # scale them down dramatically to avoid false positives
        artifacts['spectral_smoothness'] = artifacts['spectral_smoothness'] * 0.25
        artifacts['hf_deficit'] = artifacts['hf_deficit'] * 0.20
        artifacts['bandwidth_uniformity'] = artifacts['bandwidth_uniformity'] * 0.25
        artifacts['jitter_deficit'] = artifacts['jitter_deficit'] * 0.30
        artifacts['pitch_overstability'] = artifacts['pitch_overstability'] * 0.40

    artifacts['_is_compressed'] = float(is_compressed)
    return artifacts


def calculate_confidence_score(
    base_prob: float,
    artifacts: Dict[str, float],
    features: Dict[str, np.ndarray]
) -> Tuple[float, str, str]:
    """
    Calculate final confidence score combining quantum base probability
    with artifact detection results.
    
    Artifact scores: HIGHER = MORE LIKELY AI-GENERATED (0.0-1.0).
    
    Returns:
        (trust_score, label, reasoning)
        trust_score: 0-100 (higher = more organic/trustworthy)
    """
    is_compressed = bool(artifacts.get('_is_compressed', 0.0))

    # Weighted artifact score — higher = more AI-like
    # Weights reflect how discriminative each feature is for ElevenLabs/Humme:
    # Pitch & jitter are strongest, harmonic purity is strong but needs clear signal
    ai_score = (
        artifacts.get('spectral_smoothness', 0.0) * 0.12 +
        artifacts.get('phase_predictability', 0.0) * 0.08 +
        artifacts.get('temporal_regularity', 0.0) * 0.10 +
        artifacts.get('harmonic_overpurity', 0.0) * 0.15 +
        artifacts.get('pitch_overstability', 0.0) * 0.18 +
        artifacts.get('jitter_deficit', 0.0) * 0.16 +
        artifacts.get('bandwidth_uniformity', 0.0) * 0.08 +
        artifacts.get('flatness_consistency', 0.0) * 0.07 +
        artifacts.get('hf_deficit', 0.0) * 0.06
    )
    
    # Combine: artifact analysis 70% weight, quantum base 30%
    synthetic_prob = ai_score * 0.70 + base_prob * 0.30
    synthetic_prob = max(0.0, min(1.0, synthetic_prob))
    
    # Only apply a small boost if MULTIPLE strong indicators align (reduces false positives)
    # Exclude _is_compressed meta-key from scoring
    real_artifacts = {k: v for k, v in artifacts.items() if not k.startswith('_')}
    strong_ai_indicators = sum(1 for v in real_artifacts.values() if v > 0.70)
    if strong_ai_indicators >= 4:  # Need at least 4 strong indicators out of 8
        boost = 0.06 * (strong_ai_indicators / len(real_artifacts))
        synthetic_prob = min(1.0, synthetic_prob + boost)
    
    # 0.58 threshold — balanced: catches clear AI without over-flagging human voices
    if synthetic_prob > 0.58:
        label = "synthetic"
    else:
        label = "organic"
    
    # Generate detailed reasoning (exclude meta keys)
    top_artifacts = sorted(real_artifacts.items(), key=lambda x: x[1], reverse=True)[:3]
    indicator_names = {
        'spectral_smoothness': 'spectral over-smoothness',
        'phase_predictability': 'phase predictability',
        'temporal_regularity': 'temporal over-regularity',
        'harmonic_overpurity': 'harmonic over-purity',
        'pitch_overstability': 'pitch over-stability',
        'jitter_deficit': 'micro-jitter deficit',
        'bandwidth_uniformity': 'bandwidth uniformity',
        'flatness_consistency': 'flatness consistency',
        'hf_deficit': 'high-frequency deficit',
    }
    
    if label == "synthetic":
        top_reasons = [indicator_names.get(k, k) for k, v in top_artifacts if v > 0.5]
        if top_reasons:
            reasoning = f"AI detected: {', '.join(top_reasons[:3])}"
        else:
            reasoning = "Synthetic characteristics detected in audio analysis"
    else:
        if is_compressed:
            reasoning = "Natural voice (compressed recording): telephony codec detected, HF/jitter features adjusted"
        else:
            reasoning = "Natural voice characteristics: sufficient variation in pitch, harmonics, and spectral content"
    
    # Trust score: 0 (definitely AI) to 100 (definitely human)
    trust_score = (1.0 - synthetic_prob) * 100.0
    trust_score = max(0.0, min(100.0, trust_score))
    
    return trust_score, label, reasoning
