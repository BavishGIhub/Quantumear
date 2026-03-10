# QuantumEAR Training Plan
## Making the Quantum Pipeline Actually Work

**Status:** Planning
**Target:** 10,000 balanced samples (5,000 AI + 5,000 Human)
**Expected Accuracy:** 85-90% on modern TTS systems

---

## Phase 0: Prerequisites

- Python 3.10+
- PyTorch with CUDA (recommended, ~10x faster training)
- ~20 GB disk space for datasets
- API keys for: ElevenLabs (free tier), Google Cloud TTS (free tier)
- GPU recommended but not required (CPU training works, just slower)

---

## Phase 1: Dataset Collection (Week 1-2)

### Directory Structure
```
Quantumear/
└── datasets/
    ├── raw/
    │   ├── human/           # Original human audio files
    │   │   ├── librispeech/
    │   │   ├── commonvoice/
    │   │   ├── voxceleb/
    │   │   └── personal/
    │   └── synthetic/       # AI-generated audio files
    │       ├── elevenlabs/
    │       ├── hume/
    │       ├── bark/
    │       ├── xtts/
    │       ├── f5tts/
    │       ├── openai/
    │       ├── google/
    │       └── azure/
    ├── processed/           # 5-second, 22050Hz, normalized clips
    │   ├── human/
    │   └── synthetic/
    ├── splits/              # Train/val/test CSV files
    │   ├── train.csv
    │   ├── val.csv
    │   └── test.csv
    └── metadata.json        # Dataset statistics
```

### Step-by-Step Collection

#### Human Samples (5,000)

1. **LibriSpeech clean-100** (1,500 samples)
   ```bash
   # Download (~6.3GB)
   wget https://www.openslr.org/resources/12/train-clean-100.tar.gz
   tar -xzf train-clean-100.tar.gz
   # Randomly select 1,500 FLAC files from the extracted directory
   ```

2. **Mozilla Common Voice** (1,500 samples)
   - Go to https://commonvoice.mozilla.org/en/datasets
   - Download English dataset (validated clips)
   - Select 1,500 random MP3 files

3. **VoxCeleb2** (1,000 samples)
   - Register at https://www.robots.ox.ac.uk/~vgg/data/voxceleb/
   - Download a subset of audio files

4. **VCTK** (500 samples)
   - Download from https://datashare.ed.ac.uk/handle/10283/3443
   - Select samples from diverse speakers/accents

5. **Personal/real-world** (500 samples)
   - Record yourself, friends, family
   - Save WhatsApp voice messages
   - Include phone call quality recordings
   - These are CRITICAL for reducing false positives

#### AI Samples (5,000)

1. **ElevenLabs** (1,000 samples) — TOP PRIORITY
   ```
   - Sign up at elevenlabs.io (free = 10,000 chars/month)
   - Use their API or web interface
   - Use multiple voices (Rachel, Adam, Antoni, etc.)
   - Generate from varied scripts (2-7 second clips)
   - Save as MP3s
   ```

2. **Bark** (800 samples) — FREE, LOCAL
   ```bash
   pip install git+https://github.com/suno-ai/bark.git
   # See scripts/generate_bark_samples.py
   ```

3. **XTTS v2** (800 samples) — FREE, LOCAL
   ```bash
   pip install TTS
   # See scripts/generate_xtts_samples.py
   ```

4. **Hume AI** (500 samples)
   ```
   - Sign up at hume.ai
   - Free developer tier
   - Use their expressive TTS API
   ```

5. **F5-TTS** (500 samples) — FREE, LOCAL
   ```bash
   pip install f5-tts
   ```

6. **Google Cloud TTS** (400 samples)
   ```bash
   pip install google-cloud-texttospeech
   # 1M free characters/month
   ```

7. **OpenAI TTS** (400 samples)
   ```python
   from openai import OpenAI
   client = OpenAI()
   response = client.audio.speech.create(model="tts-1-hd", voice="alloy", input="...")
   ```

8. **Azure TTS** (300 samples)
   ```bash
   pip install azure-cognitiveservices-speech
   # 500K free characters/month
   ```

9. **Fish Speech** (300 samples) — FREE, LOCAL
   ```bash
   # https://github.com/fishaudio/fish-speech
   ```

---

## Phase 2: Data Preparation (Week 2)

### Processing Pipeline
For each audio file:
1. Load audio (any format)
2. Convert to mono, 22050 Hz
3. Normalize to [-1, 1]
4. Trim silence from start/end
5. Truncate or pad to exactly 5 seconds
6. Save as WAV (consistent format)
7. Log metadata (source, label, duration, speaker)

### Train/Val/Test Split
```
Total: 10,000 samples
├── Train:  7,000 (70%) — 3,500 human + 3,500 AI
├── Val:    1,500 (15%) —   750 human +   750 AI
└── Test:   1,500 (15%) —   750 human +   750 AI
```

**Critical rules:**
- Same speaker should NOT appear in both train and test
- Same AI voice should NOT appear in both train and test
- Each split should have diverse TTS sources

---

## Phase 3: Training (Week 3)

### What Gets Trained

1. **Feature Extractor Reducer** (`models/feature_extractor.py`)
   - The ResNet-18 backbone stays FROZEN (pretrained ImageNet)
   - Only the `reducer` MLP (512 → 128 → 64 → 4) gets trained
   - This learns to compress spectrogram features for quantum encoding

2. **Quantum Classifier** (`models/quantum_classifier.py`)
   - The `post_process` MLP (1 → 16 → 1) gets trained
   - The quantum circuit weights get trained via TorchConnector

3. **VQC** (`models/quantum_ml.py`)
   - `classical_net`, `theta` parameters, and `output_layer` all get trained

4. **Heuristic thresholds** — These should be VALIDATED, not trained
   - Run all human + AI samples through the heuristic
   - Check if the hardcoded thresholds are still optimal
   - Adjust if needed

### Training Configuration
```python
# Recommended hyperparameters
EPOCHS = 50
BATCH_SIZE = 32
LEARNING_RATE = 0.001
WEIGHT_DECAY = 1e-4
OPTIMIZER = "Adam"
SCHEDULER = "CosineAnnealing"
LOSS = "BCELoss"  # Binary cross-entropy

# Early stopping
PATIENCE = 10  # Stop if val loss doesn't improve for 10 epochs
```

### Training Script
See `scripts/train.py` — the full training script.

---

## Phase 4: Evaluation (Week 3-4)

### Metrics to Track
- **Accuracy** — overall correctness
- **Precision** — of those flagged synthetic, how many actually are
- **Recall** — of all synthetic samples, how many did we catch
- **F1 Score** — harmonic mean of precision and recall
- **EER** — Equal Error Rate (standard in anti-spoofing)
- **Per-TTS accuracy** — how well we detect each specific AI system

### Key Test Scenarios
1. Clean human speech → should be "organic" (≥ 80 trust score)
2. ElevenLabs voices → should be "synthetic" (≤ 30 trust score)
3. Phone call recordings → should be "organic" (test for false positives)
4. Noisy recordings → should handle gracefully
5. Music → should not crash, may be "organic"
6. Silence / near-silence → should handle gracefully

---

## Phase 5: Iteration (Ongoing)

### Common Failure Modes
1. **False positives on phone calls** → Add more compressed/telephony human samples
2. **Misses ElevenLabs Turbo v2.5** → Generate more samples from latest models
3. **Fails on non-English** → Add multilingual AI + human samples
4. **Overfits to specific speaker** → Ensure speaker diversity in training

### Continuous Improvement
- Add 100-500 new samples per week
- Retrain monthly
- Always test on a HELD-OUT set the model has never seen
- Track per-TTS-system accuracy over time
