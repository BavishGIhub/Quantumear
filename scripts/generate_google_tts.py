"""
Google Cloud TTS Sample Generator
===================================
Generates AI voice clips using Google Cloud Text-to-Speech.
1,000,000 free characters per month (WaveNet) — that's ~5,000 clips/month free.

Setup (one time):
    pip install google-cloud-texttospeech
    1. Create a Google Cloud account at https://console.cloud.google.com
    2. Enable the "Cloud Text-to-Speech API"
    3. Create a Service Account → download the JSON key file
    4. Set environment variable:
       (Windows):  set GOOGLE_APPLICATION_CREDENTIALS=C:\\path\\to\\key.json
       (Mac/Linux): export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

Run:
    python scripts/generate_google_tts.py

Output:
    datasets/raw/synthetic/google/google_XXXX.mp3
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / "datasets" / "raw" / "synthetic" / "google"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

# (voice_name, language_code)  — mix of Neural2, Journey (most natural), and WaveNet
VOICES = [
    ("en-US-Journey-D",   "en-US"),   # Journey voices are closest to human
    ("en-US-Journey-F",   "en-US"),
    ("en-US-Journey-O",   "en-US"),
    ("en-US-Neural2-A",   "en-US"),
    ("en-US-Neural2-C",   "en-US"),
    ("en-US-Neural2-D",   "en-US"),
    ("en-GB-Neural2-B",   "en-GB"),
    ("en-GB-Neural2-C",   "en-GB"),
    ("en-AU-Neural2-A",   "en-AU"),
    ("en-AU-Neural2-B",   "en-AU"),
]


def main():
    try:
        from google.cloud import texttospeech
    except ImportError:
        print("❌  Google Cloud TTS SDK not installed.")
        print("    Run: pip install google-cloud-texttospeech")
        return

    import os
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        print("❌  GOOGLE_APPLICATION_CREDENTIALS is not set.")
        print("    See the setup instructions at the top of this script.")
        return

    print("=" * 60)
    print("🔵  Google Cloud TTS Sample Generator")
    print(f"    Output : {OUTPUT_DIR}")
    print(f"    Voices : {len(VOICES)}")
    print(f"    Scripts: {len(TEXTS)}")
    print(f"    Total  : {len(VOICES) * len(TEXTS)} clips")
    print("=" * 60)
    
    # Estimate character usage
    total_chars = sum(len(t) for t in TEXTS) * len(VOICES)
    print(f"\n📊  Estimated characters used: ~{total_chars:,}")
    print(f"    Monthly free quota        :  1,000,000")
    print(f"    Remaining after this run  : ~{1_000_000 - total_chars:,}\n")

    try:
        client = texttospeech.TextToSpeechClient()
    except Exception as e:
        print(f"❌  Failed to connect: {e}")
        return

    count = 0
    total = len(VOICES) * len(TEXTS)
    errors = 0

    for voice_name, lang_code in VOICES:
        for text in TEXTS:
            filename = OUTPUT_DIR / f"google_{count:04d}.mp3"
            print(f"  [{count+1:>4}/{total}]  {voice_name:<28}  \"{text[:40]}...\"")

            try:
                synthesis_input = texttospeech.SynthesisInput(text=text)
                voice = texttospeech.VoiceSelectionParams(
                    language_code=lang_code,
                    name=voice_name,
                )
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=1.0,   # 1.0 = normal speed
                    pitch=0.0,           # 0 = natural pitch
                )
                response = client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config,
                )
                with open(filename, "wb") as f:
                    f.write(response.audio_content)

            except Exception as e:
                print(f"    ⚠️  Failed ({voice_name}): {e}")
                errors += 1

            count += 1

    print(f"\n{'=' * 60}")
    print(f"✅  Done!  Generated {count - errors} / {total} Google TTS clips → {OUTPUT_DIR}")
    if errors:
        print(f"    ⚠️  {errors} clips failed (check voice name availability in your region)")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
