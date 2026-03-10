"""
QuantumEAR Dataset Preparation Script
=======================================
Processes raw audio files into training-ready format:
- Converts all formats to WAV (22050Hz, mono)
- Normalizes and trims leading/trailing silence
- SMART SLICING: Long clips are split into multiple 5-second segments
  (e.g. a 30s file → 6 training samples instead of 1)
- Short clips (2-5s) are padded to exactly 5 seconds
- Very short clips (< 2s) are discarded
- Creates reproducible train/val/test splits (70/15/15)
- Generates metadata CSV files and a summary JSON

Usage:
    python scripts/prepare_dataset.py

Expected directory structure:
    datasets/raw/human/librispeech/    ← .flac, .wav files from LibriSpeech
    datasets/raw/human/commonvoice/    ← .mp3 files from Mozilla Common Voice
    datasets/raw/human/personal/       ← any recordings you make yourself
    datasets/raw/synthetic/elevenlabs/ ← AI clips from ElevenLabs
    datasets/raw/synthetic/bark/       ← AI clips from Bark
    ... (any subdirectory name works, it is recorded in metadata)

Output:
    datasets/processed/human/          ← 5-second WAV clips, normalized
    datasets/processed/synthetic/      ← 5-second WAV clips, normalized
    datasets/splits/train.csv
    datasets/splits/val.csv
    datasets/splits/test.csv
    datasets/metadata.json             ← Dataset statistics
"""

import os
import sys
import json
import random
import hashlib
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Tuple

# ─── Project root ─────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import librosa
import soundfile as sf

from models.config import SAMPLE_RATE, AUDIO_DURATION


# ─── Configuration ────────────────────────────────────────────────────────────

RAW_DIR       = PROJECT_ROOT / "datasets" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "datasets" / "processed"
SPLITS_DIR    = PROJECT_ROOT / "datasets" / "splits"

SUPPORTED_FORMATS = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac", ".wma", ".opus", ".webm"}

# Split ratios
TRAIN_RATIO = 0.70
VAL_RATIO   = 0.15
TEST_RATIO  = 0.15

# Silence trimming
SILENCE_TOP_DB = 30    # dB below peak to count as silence

# Slicing rules
CLIP_DURATION   = float(AUDIO_DURATION)   # 5.0 seconds — the fixed model input length
MIN_CLIP_AUDIO  = 2.0                     # Discard any clip whose usable audio is shorter than this
SLICE_OVERLAP   = 0.0                     # Overlap between consecutive slices (seconds).
                                          # Set to e.g. 1.0 for 1-second overlap / data augmentation.
MIN_CONTENT_RATIO = 0.40                  # A slice must contain at least 40 % non-silent samples
                                          # (avoids storing slices that are mostly silence/padding)


# ─── Core helpers ─────────────────────────────────────────────────────────────

def load_and_normalise(path: Path) -> Optional[np.ndarray]:
    """Load any audio file → mono 22050 Hz float32, peak-normalised to [-1, 1].
    Returns None on failure."""
    try:
        y, _ = librosa.load(str(path), sr=SAMPLE_RATE, mono=True)
        if y is None or len(y) == 0:
            return None
        max_val = np.max(np.abs(y))
        if max_val > 0:
            y = y / max_val
        return y
    except Exception as e:
        print(f"    ❌  Load failed ({path.name}): {e}")
        return None


def trim_silence(y: np.ndarray) -> np.ndarray:
    """Remove leading / trailing silence."""
    y_trimmed, _ = librosa.effects.trim(y, top_db=SILENCE_TOP_DB)
    return y_trimmed


def has_enough_content(y: np.ndarray) -> bool:
    """Return True if the clip contains enough non-silent samples."""
    rms = np.sqrt(np.mean(y ** 2))
    # Rough check: RMS above a very small floor means content is present
    return rms > 1e-4 and (np.sum(np.abs(y) > 1e-3) / len(y)) >= MIN_CONTENT_RATIO


def slice_audio(y: np.ndarray) -> List[np.ndarray]:
    """
    Smart-slice a (possibly long) audio array into CLIP_DURATION-second windows.

    Rules:
      • If the audio is exactly the right length → return it as-is.
      • If shorter than CLIP_DURATION but >= MIN_CLIP_AUDIO → zero-pad and return.
      • If shorter than MIN_CLIP_AUDIO → return [] (discard).
      • If longer → slide a CLIP_DURATION window with SLICE_OVERLAP step,
        collecting every slice that has enough audio content.

    Example (CLIP_DURATION=5, SLICE_OVERLAP=0):
        30-second file  →  6 slices  (6 training samples)
        12-second file  →  2 slices  (2 training samples, last padded)
         4-second file  →  1 slice   (zero-padded to 5 s)
         1-second file  →  discarded
    """
    target_samples = int(SAMPLE_RATE * CLIP_DURATION)
    step_samples   = int(SAMPLE_RATE * (CLIP_DURATION - SLICE_OVERLAP))
    min_samples    = int(SAMPLE_RATE * MIN_CLIP_AUDIO)

    total_samples = len(y)

    # ── Too short to use ──
    if total_samples < min_samples:
        return []

    # ── Fits in one clip (with possible padding) ──
    if total_samples <= target_samples:
        if total_samples < target_samples:
            y = np.pad(y, (0, target_samples - total_samples), mode='constant')
        return [y] if has_enough_content(y) else []

    # ── Long enough to slice ──
    slices = []
    start = 0
    while start < total_samples:
        end = start + target_samples
        chunk = y[start:end]

        if len(chunk) < min_samples:
            break                       # Remaining tail is too short, skip it

        if len(chunk) < target_samples:
            chunk = np.pad(chunk, (0, target_samples - len(chunk)), mode='constant')

        if has_enough_content(chunk):
            slices.append(chunk)

        start += step_samples

    return slices


def fingerprint(y: np.ndarray) -> str:
    """Short MD5 hash for deduplication."""
    return hashlib.md5(y.tobytes()).hexdigest()[:12]


# ─── Per-file processing ──────────────────────────────────────────────────────

def process_file(
    input_path: Path,
    label_dir: str,
    global_counter: List[int],   # mutable counter shared across calls
) -> List[dict]:
    """
    Process one source file into 1-N output WAV clips.
    Returns a list of metadata dicts (one per output clip).
    """
    y = load_and_normalise(input_path)
    if y is None:
        return []

    y = trim_silence(y)

    slices = slice_audio(y)
    if not slices:
        return []

    results = []
    for chunk in slices:
        idx = global_counter[0]
        global_counter[0] += 1

        output_name = f"{label_dir}_{idx:06d}.wav"
        output_path = PROCESSED_DIR / label_dir / output_name
        output_path.parent.mkdir(parents=True, exist_ok=True)

        sf.write(str(output_path), chunk, SAMPLE_RATE, subtype='PCM_16')

        results.append({
            "filename"         : output_name,
            "original_file"    : input_path.name,
            "original_format"  : input_path.suffix.lower(),
            "source_dir"       : input_path.parent.name,  # e.g. "elevenlabs", "librispeech"
            "duration_original": round(len(y) / SAMPLE_RATE, 2),
            "duration_final"   : CLIP_DURATION,
            "sample_rate"      : SAMPLE_RATE,
            "slices_from_file" : len(slices),
            "rms_energy"       : round(float(np.sqrt(np.mean(chunk ** 2))), 6),
            "hash"             : fingerprint(chunk),
        })

    return results


# ─── Dataset splitting ────────────────────────────────────────────────────────

def create_splits(
    human_metas: List[dict],
    synthetic_metas: List[dict],
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Stratified train / val / test split.
    Shuffled with a fixed seed so results are reproducible.
    """
    random.seed(42)

    for m in human_metas:
        m["label"] = "organic"
        m["label_id"] = 0
    for m in synthetic_metas:
        m["label"] = "synthetic"
        m["label_id"] = 1

    def split_list(items):
        random.shuffle(items)
        n = len(items)
        t = int(n * TRAIN_RATIO)
        v = int(n * (TRAIN_RATIO + VAL_RATIO))
        return items[:t], items[t:v], items[v:]

    h_tr, h_va, h_te = split_list(human_metas)
    s_tr, s_va, s_te = split_list(synthetic_metas)

    def merge_and_shuffle(*lists):
        merged = []
        for lst in lists:
            merged.extend(lst)
        random.shuffle(merged)
        return pd.DataFrame(merged)

    train_df = merge_and_shuffle(h_tr, s_tr)
    val_df   = merge_and_shuffle(h_va, s_va)
    test_df  = merge_and_shuffle(h_te, s_te)

    return train_df, val_df, test_df


# ─── Main ─────────────────────────────────────────────────────────────────────

def find_audio_files(directory: Path) -> List[Path]:
    """Recursively find all supported audio files."""
    files = []
    if not directory.exists():
        return files
    for ext in SUPPORTED_FORMATS:
        files.extend(directory.rglob(f"*{ext}"))
        files.extend(directory.rglob(f"*{ext.upper()}"))
    return sorted(set(files))


def process_category(
    raw_dir: Path,
    label_dir: str,
    label_emoji: str,
) -> List[dict]:
    """Find, slice and process all files in a category (human or synthetic)."""
    files = find_audio_files(raw_dir)
    print(f"\n{'─' * 60}")
    print(f"{label_emoji} Processing {label_dir} audio — {len(files)} source file(s) found")

    if not files:
        print(f"   ⚠️  No files in {raw_dir}")
        print(f"   ➜  Drop audio files (any format) into sub-folders there.")
        return []

    all_metas: List[dict] = []
    counter   = [0]           # mutable so process_file can increment it

    for i, fp in enumerate(files):
        if i % 50 == 0 or i == len(files) - 1:
            print(f"   [{i+1:>5}/{len(files)}]  {fp.parent.name}/{fp.name}")

        metas = process_file(fp, label_dir, counter)

        if not metas:
            print(f"    ⚠️  Skipped (too short or silent): {fp.name}")
            continue

        if len(metas) > 1:
            print(f"    ✂️  Sliced into {len(metas)} clips  ← {fp.name}")

        all_metas.extend(metas)

    print(f"\n   ✅  {len(all_metas)} clips produced from {len(files)} source files")

    # Multiplier summary
    if files:
        ratio = len(all_metas) / len(files)
        print(f"   📈  Expansion ratio: {ratio:.1f}× "
              f"({'great — long files are being fully used' if ratio >= 2 else 'mostly short clips'})")

    return all_metas


def main():
    global SLICE_OVERLAP
    parser = argparse.ArgumentParser(description="Prepare QuantumEAR training dataset")
    parser.add_argument("--overlap", type=float, default=SLICE_OVERLAP,
                        help="Slice overlap in seconds (default 0). "
                             "Use e.g. 1.0 for data augmentation on small datasets.")
    args = parser.parse_args()

    SLICE_OVERLAP = args.overlap

    print("=" * 60)
    print("🔊  QuantumEAR — Dataset Preparation")
    print(f"    Clip length  : {CLIP_DURATION}s")
    print(f"    Min audio    : {MIN_CLIP_AUDIO}s (shorter clips discarded)")
    print(f"    Slice overlap: {SLICE_OVERLAP}s")
    print(f"    Splits       : {int(TRAIN_RATIO*100)}/{int(VAL_RATIO*100)}/{int(TEST_RATIO*100)}"
          f"  (train/val/test)")
    print("=" * 60)

    # Ensure root dirs exist
    (RAW_DIR / "human").mkdir(parents=True, exist_ok=True)
    (RAW_DIR / "synthetic").mkdir(parents=True, exist_ok=True)

    # ── Process both categories ──
    human_metas    = process_category(RAW_DIR / "human",    "human",    "🎤")
    synthetic_metas = process_category(RAW_DIR / "synthetic", "synthetic", "🤖")

    total = len(human_metas) + len(synthetic_metas)
    if total == 0:
        print("\n⚠️  No clips were produced. Add audio files and re-run.")
        return

    # ── Train / val / test splits ──
    print(f"\n{'─' * 60}")
    print("📋  Creating stratified splits...")

    train_df, val_df, test_df = create_splits(human_metas, synthetic_metas)

    SPLITS_DIR.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(SPLITS_DIR / "train.csv", index=False)
    val_df.to_csv(SPLITS_DIR   / "val.csv",   index=False)
    test_df.to_csv(SPLITS_DIR  / "test.csv",  index=False)

    def split_summary(df, name):
        counts = df["label"].value_counts().to_dict() if "label" in df.columns else {}
        print(f"   {name:<6}: {len(df):>6} clips  {counts}")

    split_summary(train_df, "Train")
    split_summary(val_df,   "Val  ")
    split_summary(test_df,  "Test ")

    # ── Metadata JSON ──
    metadata = {
        "created_at"         : datetime.now().isoformat(),
        "clip_duration_s"    : CLIP_DURATION,
        "slice_overlap_s"    : SLICE_OVERLAP,
        "sample_rate"        : SAMPLE_RATE,
        "total_clips"        : total,
        "total_human_clips"  : len(human_metas),
        "total_synthetic_clips": len(synthetic_metas),
        "train_clips"        : len(train_df),
        "val_clips"          : len(val_df),
        "test_clips"         : len(test_df),
        "human_sources"      : sorted(set(m["source_dir"] for m in human_metas)),
        "synthetic_sources"  : sorted(set(m["source_dir"] for m in synthetic_metas)),
    }

    meta_path = PROJECT_ROOT / "datasets" / "metadata.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    with open(meta_path, "w") as fh:
        json.dump(metadata, fh, indent=2)

    # ── Final summary ──
    print(f"\n{'=' * 60}")
    print(f"✅  Dataset ready!")
    print(f"   Total clips  : {total}")
    print(f"     Human      : {len(human_metas)}")
    print(f"     Synthetic  : {len(synthetic_metas)}")
    print(f"   Processed dir: {PROCESSED_DIR}")
    print(f"   Splits dir   : {SPLITS_DIR}")
    print(f"   Metadata     : {meta_path}")
    print(f"\n   Next step ➜  python scripts/train.py")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
