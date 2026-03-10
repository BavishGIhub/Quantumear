"""
Microsoft Edge TTS Sample Generator
=====================================
Generates AI voice clips using edge-tts — Microsoft's neural TTS engine.

✅ Works with ANY Python version (including 3.14)
✅ Completely FREE — no API key, no account needed
✅ High quality (same voices as Azure Neural TTS)
✅ 300+ voices across 40+ languages

Setup (one time):
    pip install edge-tts

Run:
    python scripts/generate_edge_tts.py

Output:
    datasets/raw/synthetic/edge_tts/edge_XXXX.mp3
"""

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / "datasets" / "raw" / "synthetic" / "edge_tts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── Sentences ────────────────────────────────────────────────────────────────
# Varied content: professional messages, casual speech, questions, commands.
# Each sentence is roughly 5–15 words → ~3–6 seconds of audio.

TEXTS = [
    # Professional / business
    "Hello, I wanted to confirm our meeting tomorrow at three PM.",
    "The package was delivered this morning to your front door.",
    "Please call me back as soon as you get this message.",
    "I am reaching out regarding your recent application to the open position.",
    "Thank you for your time today. I really appreciate your help.",
    "We need to reschedule the appointment to sometime next week if possible.",
    "Your order has been shipped and will arrive in two to three business days.",
    "Could you send me the document before end of day today please?",
    "I think we should move the call to Thursday morning instead.",
    "The meeting went well and everyone seemed happy with the proposal.",
    # Casual / conversational
    "Can you hear me clearly? I will try calling again in five minutes.",
    "The weather here has been quite unusual for this time of year.",
    "I just wanted to check in and see how you were doing.",
    "Hi there. I was hoping we could talk about the project timeline.",
    "I got your message and I will get back to you very soon.",
    "Sorry for the delay. I have been busy but I have not forgotten.",
    "Let me know if you need anything else. Happy to help anytime.",
    "I am running a few minutes late but I will be there soon.",
    "The report looks great. Just a few small edits and it will be perfect.",
    "Thanks for reaching out. I will review this and get back to you.",
    # Informational / narrative
    "Scientists have discovered a new species of deep-sea fish near the Pacific.",
    "The city council voted unanimously to approve the new transit plan.",
    "Researchers say that regular exercise can significantly improve mental health.",
    "The temperature is expected to drop below freezing by tomorrow evening.",
    "Local volunteers spent the weekend cleaning up the riverbank and park.",
]

# ─── Voices ───────────────────────────────────────────────────────────────────
# Mix of US, UK, Australian, and Indian English voices — different synthesis
# characteristics, important for training a generalised detector.

VOICES = [
    # US English — Neural
    "en-US-AriaNeural",         # Female, conversational
    "en-US-GuyNeural",          # Male, professional
    "en-US-JennyNeural",        # Female, friendly
    "en-US-EricNeural",         # Male, casual
    "en-US-MichelleNeural",     # Female, warm
    "en-US-RogerNeural",        # Male, authoritative
    # UK English
    "en-GB-SoniaNeural",        # Female, British
    "en-GB-RyanNeural",         # Male, British
    "en-GB-LibbyNeural",        # Female, British casual
    # Australian English
    "en-AU-NatashaNeural",      # Female, Australian
    "en-AU-WilliamNeural",      # Male, Australian
    # Indian English
    "en-IN-NeerjaNeural",       # Female, Indian
    "en-IN-PrabhatNeural",      # Male, Indian
]


# ─── Generator ────────────────────────────────────────────────────────────────

async def generate_clip(voice: str, text: str, output_path: Path) -> bool:
    """Generate a single TTS clip. Returns True on success."""
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(output_path))
        return True
    except Exception as e:
        print(f"    ⚠️  Failed ({voice}): {e}")
        return False


async def main():
    try:
        import edge_tts
    except ImportError:
        print("❌  edge-tts is not installed.")
        print("    Run: pip install edge-tts")
        return

    total = len(VOICES) * len(TEXTS)

    print("=" * 60)
    print("🔷  Microsoft Edge TTS Sample Generator")
    print(f"    Output : {OUTPUT_DIR}")
    print(f"    Voices : {len(VOICES)}")
    print(f"    Scripts: {len(TEXTS)}")
    print(f"    Total  : {total} clips")
    print(f"    ✅ Works on Python 3.14  |  Free  |  No API key")
    print("=" * 60)
    print("\n⚡  Generating (edge-tts is fast — ~1–3 sec per clip)...\n")

    count = 0
    errors = 0

    for voice in VOICES:
        for i, text in enumerate(TEXTS):
            filename = OUTPUT_DIR / f"edge_{count:04d}.mp3"

            print(f"  [{count+1:>4}/{total}]  {voice:<30}  \"{text[:42]}...\"")

            success = await generate_clip(voice, text, filename)
            if not success:
                errors += 1

            count += 1

            # Small delay to be polite to Microsoft's servers
            await asyncio.sleep(0.3)

    print(f"\n{'=' * 60}")
    ok = count - errors
    print(f"✅  Done!  {ok} / {total} clips generated → {OUTPUT_DIR}")
    if errors:
        print(f"    ⚠️  {errors} clips failed (network issue — re-run to retry)")
    print(f"{'=' * 60}")
    print(f"\n   Next step ➜  python scripts/prepare_dataset.py")


if __name__ == "__main__":
    asyncio.run(main())
