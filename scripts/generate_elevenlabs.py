"""
ElevenLabs TTS Sample Generator
=================================
Generates AI voice clips using ElevenLabs — the #1 AI voice platform.
Most critical for training QuantumEAR to detect high-quality deepfakes.

Supports MULTIPLE API KEYS with rotation and resume capability.
API calls use your API key for auth, NOT IP-based blocking.

Setup:
    pip install elevenlabs
    Add keys to api/.env:
        ELEVENLABS_API_KEY_1=key_here
        ELEVENLABS_API_KEY_2=key_here

Run:
    python scripts/generate_elevenlabs.py

Output:
    datasets/raw/synthetic/elevenlabs/el_XXXX.mp3
"""

import os
import sys
import time
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / "datasets" / "raw" / "synthetic" / "elevenlabs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FREE_TIER_CHARS = 10_000  # per key per month


# ─── API Keys ─────────────────────────────────────────────────────────────────

def load_api_keys() -> List[str]:
    """Load all ElevenLabs API keys from environment and .env files."""
    keys = []

    # Environment variables
    prefixes = ["ELEVENLABS_API_KEY", "ELEVEN_API_KEY"]
    for prefix in prefixes:
        for var in [prefix] + [f"{prefix}_{i}" for i in range(1, 21)]:
            val = os.environ.get(var, "").strip()
            if val and val not in keys:
                keys.append(val)

    # .env files
    for env_path in [PROJECT_ROOT / ".env", PROJECT_ROOT / "api" / ".env"]:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if (line.startswith("ELEVENLABS_API_KEY") or line.startswith("ELEVEN_API_KEY")) and "=" in line:
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val and val not in keys:
                        keys.append(val)

    return keys


# ─── Sentences (30) ──────────────────────────────────────────────────────────

TEXTS = [
    "Hello, I wanted to confirm our meeting tomorrow at three PM.",
    "The quarterly results exceeded expectations by over fifteen percent.",
    "Please call me back as soon as you get this message.",
    "I am really sorry about what happened yesterday.",
    "That is the best news I have heard all week!",
    "We need to talk about something important when you get home.",
    "Hi grandma, it is me. I am in trouble and I need your help right away.",
    "Your refund has been processed and should appear within five business days.",
    "The doctor said everything went well and there is nothing to worry about.",
    "I cannot believe they would do something like that to us.",
    "The weather has been really beautiful lately, do you not think so?",
    "Did you remember to pick up the groceries on your way home?",
    "Breaking news: scientists announced a breakthrough in energy storage.",
    "I am so proud of you for everything you have accomplished this year.",
    "Could you please speak more slowly? I did not catch that.",
    "Once upon a time there was a young girl who loved to explore.",
    "Your social security number has been compromised. Please verify your identity.",
    "Thank you so much for everything you have done. I really appreciate it.",
    "The stock market closed at a record high for the third consecutive day.",
    "I miss you so much. When are you coming home?",
    "Take two tablets in the morning and one before bed with water.",
    "We should celebrate tonight. This calls for a special dinner.",
    "Your password must contain at least eight characters including a number.",
    "I was up all night worrying about the presentation tomorrow.",
    "The rental car pickup is on the ground floor of the parking garage.",
    "Something does not feel right about this situation.",
    "Have you ever wondered what it would be like to live in another country?",
    "Press the green button to confirm and the red one to cancel.",
    "I promise I will make it up to you. Just give me another chance.",
    "Let us just take a deep breath and figure this out together.",
]

# ─── ElevenLabs voices (pre-made, available on free tier) ─────────────────────

VOICES = [
    # (voice_id, name) — these are ElevenLabs' default pre-made voices
    ("21m00Tcm4TlvDq8ikWAM", "Rachel"),
    ("AZnzlk1XvdvUeBnXmlld", "Domi"),
    ("EXAVITQu4vr4xnSDxMaL", "Bella"),
    ("ErXwobaYiN019PkySvjV", "Antoni"),
    ("MF3mGyEYCl7XYWbV9V6O", "Elli"),
    ("TxGEqnHWrfWFTfGW9XjX", "Josh"),
    ("VR6AewLTigWG4xSOukaG", "Arnold"),
    ("pNInz6obpgDQGcFmaJgB", "Adam"),
    ("yoZ06aMxZJJ28mfd3POQ", "Sam"),
    ("onwK4e9ZLuTAKqWW03F9", "Daniel"),
]


# ─── Key Manager ──────────────────────────────────────────────────────────────

class ElevenLabsKeyManager:
    def __init__(self, api_keys: List[str]):
        self.keys = api_keys
        self.chars_used = [0] * len(api_keys)
        self.current_index = 0
        self.exhausted = set()
        self.invalid = set()

    @property
    def current_key(self):
        return self.keys[self.current_index]

    @property
    def label(self):
        return f"Key {self.current_index + 1}/{len(self.keys)}"

    def use_chars(self, n: int):
        self.chars_used[self.current_index] += n

    def mark_exhausted(self):
        self.exhausted.add(self.current_index)

    def mark_invalid(self):
        self.invalid.add(self.current_index)
        self.exhausted.add(self.current_index)

    def rotate(self) -> bool:
        for i in range(len(self.keys)):
            if i not in self.exhausted:
                self.current_index = i
                print(f"\n🔄  Switched to {self.label}")
                return True
        return False

    def all_done(self) -> bool:
        return len(self.exhausted) >= len(self.keys)

    def print_summary(self):
        print("\n📊  Key usage:")
        for i, used in enumerate(self.chars_used):
            status = "🔴 invalid" if i in self.invalid else ("🔴 exhausted" if i in self.exhausted else "✅")
            print(f"     Key {i+1}: {used:>6,} chars  {status}")


# ─── Generator ────────────────────────────────────────────────────────────────

def generate_clip(
    manager: ElevenLabsKeyManager,
    text: str,
    voice_id: str,
    voice_name: str,
    output_path: Path,
) -> bool:
    """Generate a single ElevenLabs TTS clip with retry logic."""
    from elevenlabs import ElevenLabs

    backoff_times = [10, 30, 60]

    for attempt in range(len(backoff_times)):
        try:
            client = ElevenLabs(api_key=manager.current_key)

            audio_gen = client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )

            # audio_gen is a generator, collect all bytes
            audio_bytes = b"".join(audio_gen)

            with open(output_path, "wb") as f:
                f.write(audio_bytes)

            manager.use_chars(len(text))
            return True

        except Exception as e:
            error_str = str(e)

            # Invalid API key
            if "unauthorized" in error_str.lower() or "invalid" in error_str.lower() or "401" in error_str:
                print(f"    🔴  {manager.label} is INVALID")
                manager.mark_invalid()
                if manager.rotate():
                    return generate_clip(manager, text, voice_id, voice_name, output_path)
                return False

            # Rate limit (429)
            if "429" in error_str or "rate" in error_str.lower() or "too many" in error_str.lower():
                wait = backoff_times[attempt]
                print(f"    ⏳  Rate limited — waiting {wait}s...")
                time.sleep(wait)
                continue

            # Quota exceeded
            if "quota" in error_str.lower() or "limit" in error_str.lower() or "exceeded" in error_str.lower():
                print(f"    📊  {manager.label} quota spent — rotating...")
                manager.mark_exhausted()
                if manager.rotate():
                    return generate_clip(manager, text, voice_id, voice_name, output_path)
                return False

            # Other error
            print(f"    ⚠️  Error ({voice_name}): {error_str[:100]}")
            return False

    print(f"    ⚠️  Gave up after {len(backoff_times)} retries")
    return False


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    api_keys = load_api_keys()

    if not api_keys:
        print("❌  No ElevenLabs API keys found!")
        print("")
        print("    Add to your api/.env file:")
        print("      ELEVENLABS_API_KEY_1=your_key_here")
        print("      ELEVENLABS_API_KEY_2=your_key_here")
        print("")
        print("    Get keys from: https://elevenlabs.io/app/settings/api-keys")
        return

    manager = ElevenLabsKeyManager(api_keys)

    total_chars = len(api_keys) * FREE_TIER_CHARS
    avg_chars = sum(len(t) for t in TEXTS) / len(TEXTS)
    max_clips = int(total_chars / avg_chars)
    total_desired = len(VOICES) * len(TEXTS)

    print("=" * 60)
    print("🎙️  ElevenLabs TTS Sample Generator")
    print(f"    Output   : {OUTPUT_DIR}")
    print(f"    API Keys : {len(api_keys)} ({total_chars:,} total chars)")
    print(f"    Max clips: ~{max_clips} possible")
    print(f"    Voices   : {len(VOICES)}")
    print(f"    Texts    : {len(TEXTS)} sentences")
    print(f"    Desired  : {total_desired} clips")
    print(f"    ☁️   Cloud-based — no GPU used")
    print("=" * 60)
    print(f"\n⚡  Generating...\n")

    count = 0
    errors = 0
    skipped = 0

    for voice_id, voice_name in VOICES:
        if manager.all_done():
            break

        voice_start = count
        for text in TEXTS:
            if manager.all_done():
                break

            filename = OUTPUT_DIR / f"el_{count:04d}.mp3"

            # ── RESUME: skip existing ──
            if filename.exists() and filename.stat().st_size > 1000:
                skipped += 1
                count += 1
                continue

            if (count + 1) % 10 == 0 or count == voice_start:
                print(f"  [{count+1:>5}]  {manager.label} | {voice_name:<10} | \"{text[:35]}...\"")

            success = generate_clip(manager, text, voice_id, voice_name, filename)
            if not success:
                errors += 1
                if manager.all_done():
                    break

            count += 1
            time.sleep(1.5)  # Polite pacing

        voice_clips = count - voice_start - skipped
        print(f"  ✅  {voice_name}: done")

    manager.print_summary()

    ok = count - errors - skipped
    print(f"\n{'=' * 60}")
    print(f"✅  Done!  {ok} new + {skipped} skipped")
    print(f"    Output: {OUTPUT_DIR}")
    if errors:
        print(f"    ⚠️  {errors} clips failed")
    if manager.all_done():
        print(f"    💡  Add more keys to api/.env and re-run to continue")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
