"""
Bark TTS Sample Generator
==========================
Generates AI voice clips using Bark (Suno AI) — free, runs locally.

Setup (one time):
    pip install git+https://github.com/suno-ai/bark.git

Run:
    python scripts/generate_bark.py

Output:
    datasets/raw/synthetic/bark/bark_XXXX.wav
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / "datasets" / "raw" / "synthetic" / "bark"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── Sentences to synthesize ──────────────────────────────────────────────────
# Keep each one between 5–20 words (maps to roughly 2–8 seconds of audio)

TEXTS = [
    "Hello, I wanted to confirm our meeting tomorrow at three PM.",
    "The package was delivered this morning to your front door.",
    "Please call me back as soon as you get this message.",
    "I am reaching out regarding your recent application to the open position.",
    "Can you hear me clearly? I will try calling again in five minutes.",
    "Thank you for your time today. I really appreciate your help.",
    "The weather here has been quite unusual for this time of year.",
    "I just wanted to check in and see how you were doing.",
    "We need to reschedule the appointment to sometime next week if possible.",
    "Your order has been shipped and will arrive in two to three business days.",
    "Hi there. I was hoping we could talk about the project timeline.",
    "I got your message and I will get back to you very soon.",
    "Sorry for the delay. I have been busy but I have not forgotten.",
    "Could you send me the document before end of day today please?",
    "I think we should move the call to Thursday morning instead.",
    "The meeting went well and everyone seemed happy with the proposal.",
    "Let me know if you need anything else. Happy to help anytime.",
    "I am running a few minutes late but I will be there soon.",
    "The report looks great. Just a few small edits and it will be perfect.",
    "Thanks for reaching out. I will review this and get back to you.",
]

# Bark speaker presets — covers different genders and accents
SPEAKERS = [
    "v2/en_speaker_0",
    "v2/en_speaker_1",
    "v2/en_speaker_2",
    "v2/en_speaker_3",
    "v2/en_speaker_6",
    "v2/en_speaker_9",
]


def main():
    try:
        from bark import SAMPLE_RATE, generate_audio, preload_models
        from scipy.io.wavfile import write as write_wav
    except ImportError:
        print("❌  Bark is not installed.")
        print("    Run: pip install git+https://github.com/suno-ai/bark.git")
        return

    print("=" * 60)
    print("🐶  Bark TTS Sample Generator")
    print(f"    Output: {OUTPUT_DIR}")
    print(f"    Speakers: {len(SPEAKERS)}")
    print(f"    Scripts : {len(TEXTS)}")
    print(f"    Total   : {len(SPEAKERS) * len(TEXTS)} clips")
    print("=" * 60)

    # ── PyTorch 2.6 compatibility fix ──────────────────────────────────────
    # Bark checkpoints were saved with an older format. PyTorch 2.6 changed
    # the default of torch.load to weights_only=True, which breaks Bark.
    # We monkey-patch torch.load to force weights_only=False before Bark
    # calls it. Bark's checkpoints are from a trusted source (Suno AI).
    import torch
    import functools
    _original_torch_load = torch.load

    @functools.wraps(_original_torch_load)
    def _patched_torch_load(*args, **kwargs):
        kwargs.setdefault("weights_only", False)
        return _original_torch_load(*args, **kwargs)

    torch.load = _patched_torch_load
    print("\n🔧  Applied PyTorch 2.6 compatibility patch for Bark checkpoints.")
    # ────────────────────────────────────────────────────────────────────────

    # ── GPU detection ─────────────────────────────────────────────────────
    import torch
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb  = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"🚀  GPU detected: {gpu_name} ({vram_gb:.1f} GB VRAM) — using CUDA")
        USE_GPU = True
    else:
        print("⚠️   No CUDA GPU found — running on CPU (will be slow)")
        USE_GPU = False
    # ─────────────────────────────────────────────────────────────────────

    print("📦  Loading Bark models (already cached — loading fast)...")
    preload_models(
        text_use_gpu=USE_GPU,
        text_use_small=False,
        coarse_use_gpu=USE_GPU,
        coarse_use_small=False,
        fine_use_gpu=USE_GPU,
        fine_use_small=False,
        codec_use_gpu=USE_GPU,
        force_reload=False,
    )
    print("✅  Models loaded.\n")

    count = 0
    total = len(SPEAKERS) * len(TEXTS)

    for speaker in SPEAKERS:
        for text in TEXTS:
            filename = OUTPUT_DIR / f"bark_{count:04d}.wav"

            print(f"  [{count+1:>4}/{total}]  {speaker}  →  \"{text[:50]}...\"")

            try:
                audio = generate_audio(
                    text,
                    history_prompt=speaker,   # speaker voice preset
                    silent=True,              # suppress per-clip progress bars
                )
                write_wav(str(filename), SAMPLE_RATE, audio)
            except Exception as e:
                print(f"    ⚠️  Failed: {e}")
                count += 1
                continue

            count += 1

    print(f"\n{'=' * 60}")
    print(f"✅  Done!  Generated {count} Bark clips → {OUTPUT_DIR}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
