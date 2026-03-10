"""
Hume AI Octave TTS Sample Generator
======================================
Generates AI voice clips with EMOTIONAL VARIATIONS using Hume's Octave TTS.

Supports MULTIPLE API KEYS — automatically rotates to the next key when one
hits its free-tier limit (10,000 chars/key/month).

Setup:
    pip install hume

    Add keys to Quantumear/.env (one per line):
        HUME_API_KEY_1=key_one_here
        HUME_API_KEY_2=key_two_here
        HUME_API_KEY_3=key_three_here

    Or set a single key:
        set HUME_API_KEY=your_key_here

Run:
    python scripts/generate_hume.py

Output:
    datasets/raw/synthetic/hume/hume_XXXX.wav
"""

import asyncio
import base64
import os
import sys
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / "datasets" / "raw" / "synthetic" / "hume"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ─── API Keys ─────────────────────────────────────────────────────────────────
# Supports multiple keys — rotates when one hits the free-tier limit.
# Add keys as HUME_API_KEY, HUME_API_KEY_1, HUME_API_KEY_2, etc.

def load_api_keys() -> List[str]:
    """Load all Hume API keys from environment and .env file."""
    keys = []

    # Check environment variables
    for var in ["HUME_API_KEY"] + [f"HUME_API_KEY_{i}" for i in range(1, 11)]:
        val = os.environ.get(var, "").strip()
        if val and val not in keys:
            keys.append(val)

    # Check .env files (project root AND api/ subfolder)
    for env_path in [PROJECT_ROOT / ".env", PROJECT_ROOT / "api" / ".env"]:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("HUME_API_KEY") and "=" in line:
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val and val not in keys:
                        keys.append(val)

    return keys


# ─── Sentences (30) ──────────────────────────────────────────────────────────

TEXTS = [
    # Professional
    "Hello, I wanted to confirm our meeting tomorrow at three PM.",
    "The quarterly results exceeded expectations by over fifteen percent.",
    "Please review the attached document and let me know your thoughts.",
    "I am calling to let you know that your application has been approved.",
    "We need to reschedule the appointment to sometime next week.",
    # Emotional scenarios (critical for scam detection)
    "Hi grandma, it is me. I am in trouble and I really need your help.",
    "I am so sorry about what happened. I should have been more careful.",
    "That is the best news I have heard all year. I am so happy right now!",
    "Something terrible has happened and I do not know what to do.",
    "I cannot believe they would do this to us after everything we did.",
    # Everyday conversation
    "The weather has been really beautiful lately, do you not think so?",
    "I just got off the phone with the doctor and the news is good.",
    "Did you remember to pick up the groceries on your way home?",
    "I was thinking we could go for a walk in the park this evening.",
    "My flight just landed and I should be home in about an hour.",
    # Storytelling
    "Once upon a time there was a young girl who loved to explore.",
    "The detective looked at the evidence and realized the truth.",
    "As the sun set behind the mountains everything went quiet.",
    "Years later he would remember that day as a turning point.",
    "She opened the letter and could not believe what it said.",
    # Questions / requests
    "Do you think artificial intelligence will replace most jobs?",
    "Could you please speak more slowly? I did not catch that.",
    "When was the last time you talked to your family back home?",
    "Would you be able to help me move this weekend if you are free?",
    "How long have you been working on this particular project?",
    # Commands / instructions
    "Please make sure to lock the door before you leave tonight.",
    "Take two tablets in the morning and one before bed with water.",
    "Turn left at the next intersection and then go straight.",
    "Read the instructions carefully before starting the assembly.",
    "Press the green button to confirm and the red one to cancel.",
]

# ─── Emotional acting instructions ───────────────────────────────────────────

EMOTIONS = [
    ("neutral",     "Calm, neutral tone. Matter-of-fact delivery with even pacing."),
    ("happy",       "Warm and cheerful. Genuinely happy and enthusiastic. Bright and uplifting."),
    ("sad",         "Melancholic and somber. Quiet, slow pacing. Reflective and subdued."),
    ("stern",       "Stern and impatient. Firm, clipped delivery. Businesslike and no-nonsense."),
    ("anxious",     "Anxious and concerned. Slightly hurried pace. Uneasy and worried."),
    ("whisper",     "Whispering softly. Very quiet, breathy delivery. Secretive tone."),
    ("excited",     "Very excited and energetic. Fast-paced and enthusiastic. Bright and lively."),
    ("comforting",  "Gentle, warm, and reassuring. Soft and caring. Soothing and kind."),
]

# ─── Hume Voice Library presets ───────────────────────────────────────────────

VOICES = [
    "Ava Song",
    "Sunny Meadow",
    "Stella Whisper",
    "River Moon",
    "Quinn Everett",
]

# ─── Character tracking ──────────────────────────────────────────────────────

FREE_TIER_LIMIT = 10_000   # characters per key per month


# ─── Multi-key Client Manager ────────────────────────────────────────────────

class HumeKeyManager:
    """Manages multiple API keys and rotates when one is exhausted."""

    def __init__(self, api_keys: List[str]):
        from hume import AsyncHumeClient

        self.keys = api_keys
        self.clients = [AsyncHumeClient(api_key=k) for k in api_keys]
        self.chars_used = [0] * len(api_keys)
        self.current_index = 0
        self.exhausted = set()

    @property
    def current_client(self):
        return self.clients[self.current_index]

    @property
    def current_key_label(self):
        return f"Key {self.current_index + 1}/{len(self.keys)}"

    def use_chars(self, n: int):
        self.chars_used[self.current_index] += n

    def is_current_exhausted(self) -> bool:
        return self.chars_used[self.current_index] >= FREE_TIER_LIMIT

    def mark_exhausted(self):
        self.exhausted.add(self.current_index)

    def rotate(self) -> bool:
        """Switch to the next available key. Returns False if all exhausted."""
        self.exhausted.add(self.current_index)
        for i in range(len(self.keys)):
            if i not in self.exhausted:
                self.current_index = i
                print(f"\n🔄  Switched to {self.current_key_label} "
                      f"({self.chars_used[i]:,}/{FREE_TIER_LIMIT:,} chars used)")
                return True
        return False

    def all_exhausted(self) -> bool:
        return len(self.exhausted) >= len(self.keys)

    def print_usage(self):
        print("\n📊  Character usage per key:")
        for i, used in enumerate(self.chars_used):
            status = "✅" if i not in self.exhausted else "🔴 exhausted"
            print(f"     Key {i+1}: {used:>6,} / {FREE_TIER_LIMIT:,} chars  {status}")
        total = sum(self.chars_used)
        print(f"     Total: {total:>6,} chars across {len(self.keys)} keys")


# ─── Generator ────────────────────────────────────────────────────────────────

async def generate_clip(
    manager: HumeKeyManager,
    text: str,
    voice_name: str,
    emotion_label: str,
    emotion_desc: str,
    output_path: Path,
) -> bool:
    """Generate a single Hume TTS clip with proper rate-limit backoff."""
    from hume.tts import PostedUtterance, PostedUtteranceVoiceWithName

    # Check if we need to rotate before even trying
    if manager.is_current_exhausted():
        if not manager.rotate():
            print("    🛑  All API keys exhausted!")
            return False

    char_count = len(text)
    # Patient backoff — wait 60s each time, up to 10 retries
    max_retries = 10
    wait_time = 60

    for attempt in range(max_retries):
        try:
            utterance = PostedUtterance(
                text=text,
                voice=PostedUtteranceVoiceWithName(name=voice_name, provider="HUME_AI"),
                description=emotion_desc,
            )

            result = await manager.current_client.tts.synthesize_json(
                utterances=[utterance],
                num_generations=1,
            )

            if result.generations and len(result.generations) > 0:
                audio_b64 = result.generations[0].audio
                audio_bytes = base64.b64decode(audio_b64)

                with open(output_path, "wb") as f:
                    f.write(audio_bytes)

                manager.use_chars(char_count)
                return True
            else:
                return False

        except Exception as e:
            error_str = str(e)

            # ── Invalid API key → permanently skip ──
            if "InvalidApiKey" in error_str:
                print(f"    🔴  {manager.current_key_label} is INVALID — skipping")
                if manager.rotate():
                    return await generate_clip(
                        manager, text, voice_name, emotion_label, emotion_desc, output_path
                    )
                return False

            # ── Rate limit (E0300 / billing / 429) → WAIT and retry SAME key ──
            is_rate_limit = ("429" in error_str or "E0300" in error_str
                           or "billing" in error_str.lower())

            if is_rate_limit:
                if attempt < 2:
                    # First 2 retries: wait and try same key
                    print(f"    ⏳  Rate limited — waiting {wait_time}s (retry {attempt+1})...")
                    await asyncio.sleep(wait_time)
                    continue
                elif attempt == 2:
                    # After 3 fails on this key, try next key
                    print(f"    🔄  {manager.current_key_label} still blocked — trying next key...")
                    old_idx = manager.current_index
                    manager.mark_exhausted()
                    if manager.rotate():
                        return await generate_clip(
                            manager, text, voice_name, emotion_label, emotion_desc, output_path
                        )
                    return False
                else:
                    # Should not reach here normally
                    return False

            # ── Any other error → skip clip ──
            if not hasattr(generate_clip, '_fail_count'):
                generate_clip._fail_count = 0
            generate_clip._fail_count += 1
            if generate_clip._fail_count <= 3 or generate_clip._fail_count % 20 == 0:
                print(f"    ⚠️  Skip: {error_str[:100]}")
            return False

    print(f"    ⚠️  Gave up after {max_retries} retries")
    return False


# ─── Main ─────────────────────────────────────────────────────────────────────

async def main():
    api_keys = load_api_keys()

    if not api_keys:
        print("❌  No API keys found!")
        print("")
        print("    Add keys to your .env file (one per line):")
        print("      HUME_API_KEY_1=your_first_key_here")
        print("      HUME_API_KEY_2=your_second_key_here")
        print("      HUME_API_KEY_3=your_third_key_here")
        print("")
        print("    Or set a single key:")
        print("      set HUME_API_KEY=your_key_here")
        return

    manager = HumeKeyManager(api_keys)

    # Calculate what we can generate with available keys
    total_chars_available = len(api_keys) * FREE_TIER_LIMIT
    avg_chars_per_text = sum(len(t) for t in TEXTS) / len(TEXTS)
    max_clips_possible = int(total_chars_available / avg_chars_per_text)

    total_desired = len(VOICES) * len(EMOTIONS) * len(TEXTS)

    print("=" * 60)
    print("🎭  Hume AI Octave TTS Sample Generator")
    print(f"    Output   : {OUTPUT_DIR}")
    print(f"    API Keys : {len(api_keys)} ({total_chars_available:,} total chars)")
    print(f"    Max clips: ~{max_clips_possible} possible with {len(api_keys)} free-tier key(s)")
    print(f"    Voices   : {len(VOICES)}")
    print(f"    Emotions : {len(EMOTIONS)} ({', '.join(e[0] for e in EMOTIONS)})")
    print(f"    Texts    : {len(TEXTS)} sentences")
    print(f"    Desired  : {total_desired} clips")
    print(f"    ☁️   Cloud-based API — no GPU used")
    print("=" * 60)

    if max_clips_possible < total_desired:
        print(f"\n⚠️  With {len(api_keys)} free-tier key(s), you can generate ~{max_clips_possible} clips")
        print(f"    (need {total_desired} for full coverage). Will generate as many as possible.")

    print(f"\n⚡  Generating...\n")

    count = 0
    errors = 0
    stopped_early = False

    for voice in VOICES:
        if manager.all_exhausted():
            stopped_early = True
            break

        for emotion_label, emotion_desc in EMOTIONS:
            if manager.all_exhausted():
                stopped_early = True
                break

            section_start = count
            for text in TEXTS:
                if manager.all_exhausted():
                    stopped_early = True
                    break

                filename = OUTPUT_DIR / f"hume_{count:04d}.wav"

                # ── RESUME: skip existing clips ──
                if filename.exists() and filename.stat().st_size > 1000:
                    count += 1
                    continue

                if (count + 1) % 10 == 0 or count == 0:
                    print(f"  [{count+1:>5}]  {manager.current_key_label} | "
                          f"{voice:<16} | {emotion_label:<11} | \"{text[:30]}...\"")

                success = await generate_clip(
                    manager, text, voice, emotion_label, emotion_desc, filename
                )
                if not success:
                    errors += 1
                    if manager.all_exhausted():
                        stopped_early = True
                        break

                count += 1
                await asyncio.sleep(5)  # 5s between clips to stay under rate limit

            if not stopped_early:
                section_count = count - section_start
                print(f"  ✅  {voice} / {emotion_label}: {section_count} clips")

        if stopped_early:
            break

    # Summary
    manager.print_usage()

    ok = count - errors
    print(f"\n{'=' * 60}")
    print(f"✅  Done!  {ok} / {count} clips generated → {OUTPUT_DIR}")
    if stopped_early:
        print(f"    ⚠️  Stopped early — all {len(api_keys)} keys exhausted")
        print(f"    💡  Add more keys to .env and re-run to continue")
    if errors:
        print(f"    ⚠️  {errors} clips failed")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
