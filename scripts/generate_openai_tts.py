"""
OpenAI TTS Sample Generator
==============================
Generates AI voice clips using OpenAI's gpt-4o-mini-tts model.
Supports EMOTIONAL INSTRUCTIONS — each voice can be generated
with different emotional tones via the "instructions" parameter.

OpenAI gives $5 free credit on new accounts.
gpt-4o-mini-tts costs $0.60/1M chars → $5 credit = ~8.3M chars = ~130,000 clips!
Even $1 credit gives ~26,000 clips — way more than we need.

Setup:
    pip install openai
    Add key to api/.env:
        OPENAI_API_KEY=sk-your-key-here

Run:
    python scripts/generate_openai_tts.py

Output:
    datasets/raw/synthetic/openai/oai_XXXX.mp3
"""

import os
import sys
import time
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / "datasets" / "raw" / "synthetic" / "openai"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ─── API Key ──────────────────────────────────────────────────────────────────

def load_api_key() -> str:
    """Load OpenAI API key from environment or .env files."""
    # Environment variable first
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        return key

    # .env files
    for env_path in [PROJECT_ROOT / ".env", PROJECT_ROOT / "api" / ".env"]:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("OPENAI_API_KEY") and "=" in line:
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val
    return ""


# ─── Sentences (30) ──────────────────────────────────────────────────────────

TEXTS = [
    "Hello, I wanted to confirm our meeting tomorrow at three PM.",
    "The quarterly results exceeded expectations by over fifteen percent.",
    "Please call me back as soon as you get this message.",
    "I am really sorry about what happened yesterday.",
    "That is the best news I have heard all week!",
    "We need to talk about something important when you get home.",
    "Hi grandma, it is me. I am calling because I need your help.",
    "Your refund has been processed and should appear within five business days.",
    "The doctor said everything went well and there is nothing to worry about.",
    "I cannot believe they would do something like that to us.",
    "The weather has been really beautiful lately, do you not think so?",
    "Did you remember to pick up the groceries on your way home?",
    "Breaking news: scientists announced a breakthrough in energy storage.",
    "I am so proud of you for everything you have accomplished this year.",
    "Could you please speak more slowly? I did not catch that.",
    "Once upon a time there was a young girl who loved to explore the forest.",
    "Your account may have been compromised. Please verify your identity.",
    "Thank you so much for everything you have done. I really appreciate it.",
    "The stock market closed at a record high for the third consecutive day.",
    "I miss you so much. When are you coming home?",
    "Take two tablets in the morning and one before bed with water.",
    "We should celebrate tonight. This calls for a special dinner.",
    "I was up all night worrying about the presentation tomorrow morning.",
    "Something does not feel right about this situation.",
    "Have you ever wondered what it would be like to live in another country?",
    "Press the green button to confirm and the red one to cancel.",
    "I promise I will make it up to you. Just give me another chance.",
    "Let us just take a deep breath and figure this out together.",
    "She opened the letter and could not believe what she was reading.",
    "The traffic is absolutely terrible today. I should have taken the train.",
]

# ─── OpenAI TTS Voices ───────────────────────────────────────────────────────
# gpt-4o-mini-tts supports: alloy, ash, coral, echo, fable, nova, onyx, sage, shimmer

VOICES = ["alloy", "ash", "coral", "echo", "fable", "nova", "onyx", "sage", "shimmer"]

# ─── Emotional Instructions ──────────────────────────────────────────────────
# gpt-4o-mini-tts supports an "instructions" parameter for emotional control

EMOTIONS = [
    ("neutral",     "Speak in a calm, conversational, neutral tone."),
    ("happy",       "Speak with warmth, enthusiasm, and genuine happiness. Sound upbeat and cheerful."),
    ("sad",         "Speak with a melancholic, subdued tone. Sound reflective and somber, with slower pacing."),
    ("urgent",      "Speak with urgency and intensity. Sound pressing, like time is running out."),
    ("whisper",     "Speak in a hushed, quiet whisper. Sound secretive and intimate."),
    ("excited",     "Speak with high energy and excitement! Sound thrilled and animated."),
    ("professional","Speak in a formal, business-like manner. Sound authoritative and confident."),
    ("comforting",  "Speak in a gentle, soothing, reassuring tone. Sound caring and warm."),
]


# ─── Generator ────────────────────────────────────────────────────────────────

def generate_clip(
    client,
    text: str,
    voice: str,
    emotion_label: str,
    emotion_instructions: str,
    output_path: Path,
) -> bool:
    """Generate a single OpenAI TTS clip with emotional instructions."""
    backoff_times = [10, 30, 60]

    for attempt in range(len(backoff_times)):
        try:
            response = client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice=voice,
                input=text,
                instructions=emotion_instructions,
                response_format="mp3",
            )

            response.stream_to_file(str(output_path))
            return True

        except Exception as e:
            error_str = str(e)

            # Rate limit
            if "429" in error_str or "rate" in error_str.lower():
                wait = backoff_times[attempt]
                print(f"    ⏳  Rate limited — waiting {wait}s...")
                time.sleep(wait)
                continue

            # Quota / billing
            if "quota" in error_str.lower() or "billing" in error_str.lower() or "insufficient" in error_str.lower():
                print(f"    🛑  Quota/billing issue: {error_str[:100]}")
                return None  # signals to stop

            # Other error
            print(f"    ⚠️  Error: {error_str[:100]}")
            return False

    print(f"    ⚠️  Gave up after {len(backoff_times)} retries")
    return False


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    api_key = load_api_key()

    if not api_key:
        print("❌  No OpenAI API key found!")
        print("")
        print("    Add to your api/.env file:")
        print("      OPENAI_API_KEY=sk-your-key-here")
        print("")
        print("    Get a key from: https://platform.openai.com/api-keys")
        print("    New accounts get $5 free credit = ~8,000+ clips")
        return

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    total_desired = len(VOICES) * len(EMOTIONS) * len(TEXTS)
    total_chars = sum(len(t) for t in TEXTS) * len(VOICES) * len(EMOTIONS)
    cost_estimate = total_chars * 0.60 / 1_000_000

    print("=" * 60)
    print("🤖  OpenAI TTS Sample Generator (gpt-4o-mini-tts)")
    print(f"    Output    : {OUTPUT_DIR}")
    print(f"    Voices    : {len(VOICES)} ({', '.join(VOICES[:4])}...)")
    print(f"    Emotions  : {len(EMOTIONS)} per voice")
    print(f"    Texts     : {len(TEXTS)} sentences")
    print(f"    Total     : {total_desired} clips")
    print(f"    Est. chars: {total_chars:,}")
    print(f"    Est. cost : ${cost_estimate:.2f} (gpt-4o-mini-tts @ $0.60/1M)")
    print(f"    ☁️   Cloud-based — no GPU used")
    print("=" * 60)
    print(f"\n⚡  Generating...\n")

    count = 0
    errors = 0
    skipped = 0
    stop = False

    for voice in VOICES:
        if stop:
            break
        for emotion_label, emotion_desc in EMOTIONS:
            if stop:
                break

            section_start = count
            for text in TEXTS:
                if stop:
                    break

                filename = OUTPUT_DIR / f"oai_{count:04d}.mp3"

                # ── RESUME: skip existing ──
                if filename.exists() and filename.stat().st_size > 1000:
                    skipped += 1
                    count += 1
                    continue

                if (count + 1) % 20 == 0 or count == section_start:
                    print(f"  [{count+1:>5}]  {voice:<8} | {emotion_label:<13} | \"{text[:30]}...\"")

                result = generate_clip(client, text, voice, emotion_label, emotion_desc, filename)

                if result is None:
                    # Quota issue — stop everything
                    stop = True
                    break
                elif not result:
                    errors += 1

                count += 1
                time.sleep(0.5)  # Polite pacing

            if not stop:
                section_count = count - section_start
                print(f"  ✅  {voice} / {emotion_label}: {section_count} clips")

    ok = count - errors - skipped
    print(f"\n{'=' * 60}")
    print(f"✅  Done!  {ok} new + {skipped} skipped")
    print(f"    Output: {OUTPUT_DIR}")
    if errors:
        print(f"    ⚠️  {errors} clips failed")
    if stop:
        print(f"    🛑  Stopped early — check billing/quota")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
