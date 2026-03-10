"""
Microsoft Edge TTS Sample Generator — Round 2
================================================
Generates ~1,200 MORE AI voice clips using Edge TTS.
Cloud-based — no GPU needed, runs fast (~1-2 sec per clip).
Saves alongside existing clips (edge_0325+).

Run:
    python scripts/generate_edge_tts_v2.py

Output:
    datasets/raw/synthetic/edge_tts/edge_0325.mp3 ... edge_1524.mp3
"""

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / "datasets" / "raw" / "synthetic" / "edge_tts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

START_INDEX = 325  # Continue from previous run

# ─── 80 new sentences ────────────────────────────────────────────────────────
# Different from round 1 and bark scripts. Covers many speaking styles.

TEXTS = [
    # Scam / fraud scenarios (critical for deepfake detection use case)
    "Hi grandma, it is me. I am in trouble and I need you to send money right away.",
    "This is your bank calling. We detected suspicious activity on your account.",
    "You have won a free cruise vacation. Press one to claim your prize now.",
    "This is the IRS. You owe back taxes and a warrant has been issued for your arrest.",
    "Your social security number has been compromised. Please verify your identity.",
    "Hello, this is tech support. We have detected a virus on your computer.",
    "I am calling from the hospital. Your family member has been in an accident.",
    "This is an urgent message from your electricity provider about your overdue bill.",
    "Your Amazon account has been locked due to suspicious purchase activity.",
    "We are calling to inform you that your car warranty is about to expire.",
    # Medical / health
    "The doctor will see you now. Please follow me to examination room three.",
    "Take one capsule twice daily with food for the next fourteen days.",
    "Your blood pressure is slightly elevated. We should monitor it more closely.",
    "The test results came back normal. There is nothing to worry about.",
    "I recommend getting a flu shot before the cold season begins.",
    "You should avoid strenuous physical activity for at least two weeks.",
    "The pharmacy will have your prescription ready in about thirty minutes.",
    "Please drink plenty of fluids and get as much rest as possible.",
    "We need to schedule a follow up appointment in about six weeks.",
    "The surgery went well and the patient is now resting comfortably.",
    # Educational / academic
    "Today we will be discussing the fundamental principles of quantum mechanics.",
    "Please open your textbooks to chapter seven and read the first paragraph.",
    "The assignment is due next Monday. Late submissions will not be accepted.",
    "Can anyone explain the difference between mitosis and meiosis?",
    "The final exam will cover all material from the beginning of the semester.",
    "Remember to cite your sources properly using the APA format.",
    "This experiment demonstrates the relationship between pressure and volume.",
    "The historical significance of this event cannot be understated.",
    "For homework, please complete problems one through twenty on page ninety four.",
    "We will be watching a documentary on climate change in our next class.",
    # Technology / tech support
    "Have you tried turning it off and on again? That usually fixes the problem.",
    "The software update will take approximately fifteen minutes to install.",
    "Your password must contain at least eight characters including a number.",
    "The wifi network should appear in your available connections list.",
    "I will need to remote into your computer to diagnose the issue.",
    "Make sure to back up your files before performing the factory reset.",
    "The application crashed because it ran out of available memory.",
    "You can access your cloud storage from any device with an internet connection.",
    "The new feature will be rolled out to all users by the end of the month.",
    "Please clear your browser cache and cookies, then try logging in again.",
    # Travel / directions
    "Your flight has been delayed by approximately two hours due to weather conditions.",
    "The hotel checkout time is eleven AM. Would you like a late checkout?",
    "Take the second exit at the roundabout and continue for half a mile.",
    "The museum is open from nine AM to five PM, Tuesday through Sunday.",
    "Boarding will begin in approximately twenty minutes at gate B fourteen.",
    "The rental car pickup is on the ground floor of the parking garage.",
    "You can purchase tickets online or at the box office before the show.",
    "The subway station is just two blocks east of here on the right side.",
    "Please have your passport and boarding pass ready for inspection.",
    "The restaurant is fully booked tonight but we have availability tomorrow.",
    # Finance / banking
    "Your current account balance is three thousand four hundred and fifty dollars.",
    "The interest rate on this savings account is currently two point five percent.",
    "Your loan application has been approved for the requested amount.",
    "We recommend diversifying your portfolio to reduce overall risk.",
    "The transaction was declined because your card has reached its daily limit.",
    "Monthly statements are available for download through online banking.",
    "The exchange rate for euros to dollars is currently one point zero eight.",
    "Your mortgage payment of fifteen hundred dollars is due on the first of each month.",
    "We offer a zero percent introductory rate for the first twelve months.",
    "Please verify the last four digits of your social security number.",
    # Storytelling / narrative
    "Once upon a time in a small village there lived a young girl named Emma.",
    "The detective examined the evidence carefully, looking for any clues.",
    "As the sun set behind the mountains, the sky turned a beautiful shade of orange.",
    "He opened the old wooden box and inside he found a collection of letters.",
    "The storm had passed and the morning brought clear blue skies and calm winds.",
    "She walked through the crowded marketplace, taking in all the sights and sounds.",
    "Years later he would look back on that moment as the turning point in his life.",
    "The old lighthouse had been standing on that cliff for over a hundred years.",
    "They packed their bags and set off on an adventure they would never forget.",
    "In the distance a wolf howled and the forest fell completely silent.",
    # Short / quick phrases (variety in length)
    "Yes, absolutely. I completely agree with you.",
    "No, that is not correct. Let me explain why.",
    "Excuse me, could you repeat that please?",
    "I will be right back. Just give me one moment.",
    "That sounds like a great idea. Let us do it.",
    "I am not sure about that. Let me check and get back to you.",
    "Perfect. That works for me. See you then.",
    "Wait, what did you just say? I did not catch that.",
    "Oh really? I had no idea. That is very interesting.",
    "Sure, no problem at all. Happy to help.",
]

# ─── 15 voices (expanded from round 1's 13) ──────────────────────────────────
# Now includes multilingual accent voices for more diversity

VOICES = [
    # US English
    "en-US-AriaNeural",
    "en-US-GuyNeural",
    "en-US-JennyNeural",
    "en-US-EricNeural",
    "en-US-MichelleNeural",
    "en-US-RogerNeural",
    "en-US-SteffanNeural",
    "en-US-AndrewNeural",
    # UK English
    "en-GB-SoniaNeural",
    "en-GB-RyanNeural",
    "en-GB-LibbyNeural",
    "en-GB-ThomasNeural",
    # Australian English
    "en-AU-NatashaNeural",
    "en-AU-WilliamNeural",
    # Indian English
    "en-IN-NeerjaNeural",
]


# ─── Generator ────────────────────────────────────────────────────────────────

async def generate_clip(voice: str, text: str, output_path: Path) -> bool:
    """Generate a single TTS clip."""
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
    print("🔷  Edge TTS Sample Generator — Round 2")
    print(f"    Output : {OUTPUT_DIR}")
    print(f"    Voices : {len(VOICES)}")
    print(f"    Scripts: {len(TEXTS)} new sentences")
    print(f"    Total  : {total} clips (edge_{START_INDEX:04d} → edge_{START_INDEX + total - 1:04d})")
    print(f"    ☁️   Cloud-based — no GPU used")
    print("=" * 60)
    print(f"\n⚡  Generating (~1-2 sec per clip, ETA: ~{total * 1.5 / 60:.0f} min)...\n")

    count = 0
    errors = 0

    for voice in VOICES:
        voice_start = count
        for text in TEXTS:
            idx = START_INDEX + count
            filename = OUTPUT_DIR / f"edge_{idx:04d}.mp3"

            if (count + 1) % 25 == 0 or count == 0:
                print(f"  [{count+1:>5}/{total}]  {voice:<28}  \"{text[:40]}...\"")

            success = await generate_clip(voice, text, filename)
            if not success:
                errors += 1

            count += 1
            await asyncio.sleep(0.2)  # Polite delay

        voice_count = count - voice_start
        print(f"  ✅  {voice}: {voice_count} clips done")

    print(f"\n{'=' * 60}")
    ok = count - errors
    print(f"✅  Done!  {ok} / {total} clips generated")
    print(f"    Total Edge TTS clips now: {START_INDEX + ok}")
    print(f"    Output: {OUTPUT_DIR}")
    if errors:
        print(f"    ⚠️  {errors} clips failed (re-run to retry)")
    print(f"{'=' * 60}")
    print(f"\n   Next step ➜  python scripts/prepare_dataset.py")


if __name__ == "__main__":
    asyncio.run(main())
