"""
Bark TTS Sample Generator — Round 2
=====================================
Generates 700 MORE AI voice clips using all 10 Bark English speakers
and 70 new sentences. Saves alongside existing clips (bark_0120+).

Run with the bark_env venv:
    bark_env\Scripts\python scripts/generate_bark_v2.py

Output:
    datasets/raw/synthetic/bark/bark_0120.wav ... bark_0819.wav
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / "datasets" / "raw" / "synthetic" / "bark"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Start numbering from where v1 left off
START_INDEX = 120

# ─── 70 new sentences ────────────────────────────────────────────────────────
# Varied content: professional, casual, emotional, questions, commands, news

TEXTS = [
    # Professional / business
    "Good morning, I am calling about the job opening you posted last week.",
    "The quarterly results exceeded expectations by over fifteen percent.",
    "We will need your signature on the contract before we can proceed.",
    "The board has approved the merger and it will take effect next month.",
    "Please review the attached document and let me know your thoughts.",
    "I wanted to follow up on our conversation from yesterday afternoon.",
    "The deadline has been moved to Friday so we have a bit more time.",
    "She asked me to forward this information to you as soon as possible.",
    "The client is very happy with the progress we have made so far.",
    "We should schedule a follow up meeting to discuss the next steps.",
    # Customer service
    "Your refund has been processed and should appear within five business days.",
    "I understand your frustration and I am here to help resolve this issue.",
    "Could you please provide your order number so I can look into this for you?",
    "We apologize for the inconvenience and appreciate your patience.",
    "The warranty covers repairs for up to two years from the purchase date.",
    "I have escalated your case to our technical support team.",
    "Is there anything else I can help you with today?",
    "Your account has been updated with the new information you provided.",
    "We are currently experiencing higher than normal call volumes.",
    "Thank you for being a valued customer. We truly appreciate your business.",
    # Casual conversation
    "Hey, what are you up to this weekend? Want to grab some dinner?",
    "I saw that movie you recommended and it was absolutely fantastic.",
    "Did you hear about what happened at the office yesterday? It was wild.",
    "I have been so busy lately I barely have time to eat properly.",
    "My flight got delayed again. I probably will not make it before midnight.",
    "That restaurant we tried last week had the best pasta I have ever had.",
    "Do you know if the store on main street is still open this late?",
    "I totally forgot about the appointment. Can we reschedule for tomorrow?",
    "She texted me saying she would be about twenty minutes late.",
    "The traffic is absolutely terrible today. I should have taken the train.",
    # News / informational
    "Breaking news: a major earthquake has been reported off the coast of Chile.",
    "Scientists announced a breakthrough in renewable energy storage technology.",
    "The stock market closed at a record high for the third consecutive day.",
    "Authorities are investigating the cause of the warehouse fire downtown.",
    "The new highway extension is expected to reduce commute times significantly.",
    "Temperatures will reach a record high of forty two degrees this afternoon.",
    "The government announced new regulations for artificial intelligence systems.",
    "Flood warnings have been issued for several counties in the northern region.",
    "The space agency confirmed plans to launch the next Mars mission in June.",
    "Researchers have identified a new species of deep sea creatures near Japan.",
    # Emotional / expressive
    "I am so proud of you for everything you have accomplished this year.",
    "That was honestly the scariest experience I have ever been through.",
    "I cannot believe they actually invited us to the premiere. This is amazing!",
    "I am really sorry about what happened. I should have been more careful.",
    "This is the happiest day of my life and I want to share it with everyone.",
    "I am worried about the situation and I do not think it will improve soon.",
    "Congratulations on the promotion! You absolutely deserve this recognition.",
    "I feel so disappointed after all the effort we put into this project.",
    "You will not believe what just happened to me on the way over here.",
    "It has been such a long day and I cannot wait to finally get some rest.",
    # Instructions / commands
    "First turn left at the light, then go straight for about two miles.",
    "Make sure to save your work before closing the application.",
    "Take two tablets in the morning and one before bed with a glass of water.",
    "Remember to turn off the lights and lock the door when you leave.",
    "Press the red button to start the machine and the green one to stop it.",
    "Please do not forget to pick up the dry cleaning on your way home.",
    "You need to restart your computer for the update to take effect.",
    "Add the flour slowly while stirring constantly to avoid any lumps.",
    "Hold the phone closer to your mouth so I can hear you more clearly.",
    "Read the instructions carefully before assembling the furniture.",
    # Questions / dialogues
    "What time does the next train to the city center depart from here?",
    "Have you ever wondered what it would be like to live in another country?",
    "Do you think artificial intelligence will replace most jobs in the future?",
    "How long have you been working on this particular research project?",
    "When was the last time you spoke to your family back home?",
    "Why did they decide to cancel the event without telling anyone?",
    "Where exactly did you find that amazing vintage jacket you wore yesterday?",
    "Who is responsible for making sure everything runs smoothly around here?",
    "Can you explain to me how this new system is supposed to work?",
    "Would you be able to pick me up from the airport tomorrow evening?",
]

# All 10 Bark English speakers for maximum voice diversity
SPEAKERS = [
    "v2/en_speaker_0",
    "v2/en_speaker_1",
    "v2/en_speaker_2",
    "v2/en_speaker_3",
    "v2/en_speaker_4",
    "v2/en_speaker_5",
    "v2/en_speaker_6",
    "v2/en_speaker_7",
    "v2/en_speaker_8",
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

    total = len(SPEAKERS) * len(TEXTS)

    print("=" * 60)
    print("🐶  Bark TTS Sample Generator — Round 2")
    print(f"    Output  : {OUTPUT_DIR}")
    print(f"    Speakers: {len(SPEAKERS)} (all English speakers)")
    print(f"    Scripts : {len(TEXTS)} new sentences")
    print(f"    Total   : {total} clips (bark_{START_INDEX:04d} → bark_{START_INDEX + total - 1:04d})")
    print("=" * 60)

    # ── PyTorch 2.6 compatibility fix ──
    import torch
    import functools
    _original_torch_load = torch.load

    @functools.wraps(_original_torch_load)
    def _patched_torch_load(*args, **kwargs):
        kwargs.setdefault("weights_only", False)
        return _original_torch_load(*args, **kwargs)

    torch.load = _patched_torch_load
    print("\n🔧  Applied PyTorch 2.6 compatibility patch.")

    # ── GPU detection ──
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb  = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"🚀  GPU: {gpu_name} ({vram_gb:.1f} GB VRAM)")
        USE_GPU = True
    else:
        print("⚠️   No GPU — running on CPU (will be slow)")
        USE_GPU = False

    print("📦  Loading Bark models...")
    preload_models(
        text_use_gpu=USE_GPU,
        coarse_use_gpu=USE_GPU,
        fine_use_gpu=USE_GPU,
        codec_use_gpu=USE_GPU,
        force_reload=False,
    )
    print("✅  Models loaded.\n")

    count = 0
    skipped = 0
    errors = 0

    for speaker in SPEAKERS:
        for text in TEXTS:
            idx = START_INDEX + count
            filename = OUTPUT_DIR / f"bark_{idx:04d}.wav"

            # ── RESUME: skip if file already exists ──
            if filename.exists() and filename.stat().st_size > 1000:
                skipped += 1
                count += 1
                continue

            print(f"  [{count+1:>4}/{total}]  {speaker:<18}  \"{text[:45]}...\"")

            try:
                audio = generate_audio(
                    text,
                    history_prompt=speaker,
                    silent=True,
                )
                write_wav(str(filename), SAMPLE_RATE, audio)
            except Exception as e:
                print(f"    ⚠️  Failed: {e}")
                errors += 1

            count += 1

    print(f"\n{'=' * 60}")
    ok = count - errors - skipped
    print(f"✅  Done!  {ok} new + {skipped} skipped (already existed)")
    print(f"    Total Bark clips now: {START_INDEX + count - errors}")
    print(f"    Output: {OUTPUT_DIR}")
    if errors:
        print(f"    ⚠️  {errors} clips failed")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
