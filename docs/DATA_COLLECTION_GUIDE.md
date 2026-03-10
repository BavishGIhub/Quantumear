# 🎤 Data Collection Guide — Step by Step

All files go inside the `Quantumear/datasets/raw/` folder that was already created for you.

```
Quantumear/
└── datasets/
    └── raw/
        ├── human/
        │   ├── librispeech/     ← Step A
        │   ├── commonvoice/     ← Step B
        │   └── personal/        ← Step C
        └── synthetic/
            ├── elevenlabs/      ← Step 1
            ├── hume/            ← Step 2
            ├── bark/            ← Step 3
            ├── xtts/            ← Step 4
            ├── google/          ← Step 5
            └── openai/          ← Step 6
```

---

## 🟢 HUMAN VOICES (Real People)

---

### Step A — LibriSpeech (FREE, ~1500 samples)
*Clean audiobook recordings from real people. Best quality human data.*

1. Go to → **https://www.openslr.org/12**
2. Download **`train-clean-100.tar.gz`** (6.3 GB)
   > ⚠️ It's large. If you want less, download `test-clean.tar.gz` (346 MB) for ~2,600 clips
3. Extract the downloaded file (right-click → Extract All or use 7-Zip)
4. Inside you'll find folders like:
   ```
   LibriSpeech/train-clean-100/19/198/19-198-0000.flac
                                        19-198-0001.flac
                                        ...
   ```
5. **Copy any `.flac` files you want** into:
   ```
   datasets/raw/human/librispeech/
   ```
   Just dump them flat in the folder — no need to keep the sub-folders.

> 💡 **Tip**: You don't need all 28,000 files. Pick 1,000–2,000 at random.

---

### Step B — Mozilla Common Voice (FREE, ~1500 samples)
*Crowdsourced voices — diverse accents, ages, recording qualities. Very realistic.*

1. Go to → **https://commonvoice.mozilla.org/en/datasets**
2. Click **"English"** then click **"Download"**
   > You need to log in with a free account
3. Download the validated clips archive (`.tar.gz`, around 2-10 GB depending on version)
4. Extract it — you'll find a folder called `clips/` full of `.mp3` files
5. **Copy the `.mp3` files** into:
   ```
   datasets/raw/human/commonvoice/
   ```

> 💡 **Tip**: The validated set has better quality. Pick randomly from the `validated.tsv` list included in the archive.

---

### Step C — Personal Recordings (IMPORTANT for reducing false positives)
*Your own voice, friends, WhatsApp messages, phone calls. This is critical — without it the model will flag compressed/noisy audio as AI.*

Collect any of these:
- Record yourself talking on your phone's voice recorder (2–30 seconds each)
- Save WhatsApp voice messages (`.opus` files from `WhatsApp/Media/WhatsApp Voice Notes/`)
- Record a video call and extract the audio
- Ask 2–3 friends to record short voice messages and send them

**Put all of these into:**
```
datasets/raw/human/personal/
```

Supported formats: `.wav`, `.mp3`, `.ogg`, `.opus`, `.m4a`, `.flac`

> 💡 **Aim for**: at least 50–100 personal clips. These are gold for training.

---
---

## 🔴 AI VOICES (Synthetic — The Ones You Want to Detect)

---

### Step 1 — ElevenLabs (FREE TIER, TOP PRIORITY 🥇)
*The hardest AI voice to detect. You must have these in your training data.*

1. Go to → **https://elevenlabs.io** and sign up for free
2. Click **"Text to Speech"** in the left sidebar
3. Type any sentence in the text box. Use varied sentences like:
   ```
   Hello, I wanted to confirm our meeting tomorrow at 3pm.
   The package was delivered this morning to your front door.
   Please call me back as soon as you get this message.
   I am reaching out regarding your recent application.
   Can you hear me clearly? I will call again in five minutes.
   ```
4. Select different **voices** from the dropdown (Rachel, Adam, Sarah, Charlie, etc.)
5. Click **Generate** → then click the **Download** button (arrow icon)
6. Save the `.mp3` file
7. Repeat with different voices and different sentences
8. **Put all downloaded `.mp3` files into:**
   ```
   datasets/raw/synthetic/elevenlabs/
   ```

> 💡 **Free tier**: 10,000 characters/month. At ~100 chars per sentence that's ~100 clips/month.
> 💡 **Go faster**: $5/month Creator plan gives you 30,000 chars — ~300 clips/month.
> 🎯 **Target**: At least 200–500 ElevenLabs clips.

---

### Step 2 — Hume AI (FREE TIER 🥈)
*Emotional AI voices — detects a different kind of synthesis artifact.*

1. Go to → **https://www.hume.ai** → Sign up free
2. Go to their **Playground** or **Text to Speech** demo
3. Generate clips using their **Octave TTS** voices
4. Download the audio files
5. **Put them into:**
   ```
   datasets/raw/synthetic/hume/
   ```

> 💡 **Target**: 100–200 Hume clips.

---

### Step 3 — Bark (FREE, UNLIMITED, runs on your PC 🥉)
*Open source AI voice. Free to run locally, generates unlimited clips.*

**One-time setup (do this once):**
```bash
pip install git+https://github.com/suno-ai/bark.git
```

**Generate clips — run this Python script:**
```python
# Save as: scripts/generate_bark.py
# Run with: python scripts/generate_bark.py

from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav
import numpy as np
from pathlib import Path

preload_models()

OUTPUT_DIR = Path("datasets/raw/synthetic/bark")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SCRIPTS = [
    "Hello, I wanted to confirm our meeting tomorrow at three PM.",
    "The package was delivered this morning to your front door.",
    "Please call me back as soon as you get this message.",
    "I am reaching out regarding your recent application to the position.",
    "Can you hear me? I will try calling again in five minutes.",
    "Thank you for your time today. I really appreciate it.",
    "The weather here has been quite unusual lately, don't you think?",
    "I just wanted to check in and see how you were doing.",
    "We need to reschedule the appointment for next week if possible.",
    "Your order has been shipped and will arrive in two business days.",
]

SPEAKERS = [
    "[SPEAKER_0]", "[SPEAKER_1]", "[SPEAKER_2]",
    "v2/en_speaker_0", "v2/en_speaker_1", "v2/en_speaker_6",
]

count = 0
for speaker in SPEAKERS:
    for i, text in enumerate(SCRIPTS):
        prompt = f"{speaker} {text}"
        audio = generate_audio(prompt)
        filename = OUTPUT_DIR / f"bark_{count:04d}.wav"
        write_wav(str(filename), SAMPLE_RATE, audio)
        print(f"Generated: {filename.name}")
        count += 1

print(f"\nDone! Generated {count} Bark clips.")
```

Run it:
```bash
python scripts/generate_bark.py
```

**Output goes automatically to:**
```
datasets/raw/synthetic/bark/
```

> 💡 Bark is slow without a GPU (~30s per clip on CPU). Run overnight for 100+ clips.
> 💡 With a GPU it takes ~3s per clip.

---

### Step 4 — XTTS v2 (FREE, UNLIMITED, high quality)
*Coqui XTTS — one of the best open-source voice cloners.*

**One-time setup:**
```bash
pip install TTS
```

**Generate clips:**
```python
# Save as: scripts/generate_xtts.py
# Run with: python scripts/generate_xtts.py

from TTS.api import TTS
from pathlib import Path

OUTPUT_DIR = Path("datasets/raw/synthetic/xtts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

TEXTS = [
    "Hello, I wanted to confirm our meeting tomorrow at three PM.",
    "The package was delivered this morning to your front door.",
    "Please call me back as soon as you get this message.",
    "Thank you for your time today, I really appreciate your help.",
    "We need to reschedule the appointment for next week if possible.",
    "Your order has been shipped and will arrive in two business days.",
    "I am reaching out regarding your recent application.",
    "Can you hear me clearly? I will call again in five minutes.",
    "The weather here has been quite unusual lately.",
    "I just wanted to check in and see how you were doing.",
]

count = 0
for i, text in enumerate(TEXTS):
    filename = OUTPUT_DIR / f"xtts_{count:04d}.wav"
    tts.tts_to_file(
        text=text,
        speaker=tts.speakers[i % len(tts.speakers)],
        language="en",
        file_path=str(filename)
    )
    print(f"Generated: {filename.name}")
    count += 1

print(f"\nDone! Generated {count} XTTS clips.")
```

Run it:
```bash
python scripts/generate_xtts.py
```

---

### Step 5 — Google Cloud TTS (FREE TIER, 1M chars/month)
*Very natural sounding, different synthesis engine from ElevenLabs.*

**One-time setup:**
1. Go to → **https://console.cloud.google.com**
2. Create a free account (requires a credit card but won't be charged)
3. Enable the **Text-to-Speech API**
4. Create a service account key (JSON file)
5. Set the environment variable:
   ```bash
   set GOOGLE_APPLICATION_CREDENTIALS=path\to\your-key.json
   ```
6. Install the library:
   ```bash
   pip install google-cloud-texttospeech
   ```

**Generate clips:**
```python
# Save as: scripts/generate_google_tts.py
# Run with: python scripts/generate_google_tts.py

from google.cloud import texttospeech
from pathlib import Path

OUTPUT_DIR = Path("datasets/raw/synthetic/google")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

client = texttospeech.TextToSpeechClient()

TEXTS = [
    "Hello, I wanted to confirm our meeting tomorrow at three PM.",
    "The package was delivered this morning to your front door.",
    "Please call me back as soon as you get this message.",
    "Thank you for your time today, I really appreciate your help.",
    "Your order has been shipped and will arrive in two business days.",
    "Can you hear me clearly? I will try calling again in five minutes.",
    "I am reaching out regarding your recent application to the position.",
    "We need to reschedule the appointment for next week if possible.",
    "The weather here has been quite unusual for this time of year.",
    "I just wanted to check in and see how you were doing recently.",
]

VOICES = [
    ("en-US-Journey-D", texttospeech.SsmlVoiceGender.MALE),
    ("en-US-Journey-F", texttospeech.SsmlVoiceGender.FEMALE),
    ("en-US-Neural2-A", texttospeech.SsmlVoiceGender.MALE),
    ("en-US-Neural2-C", texttospeech.SsmlVoiceGender.FEMALE),
    ("en-GB-Neural2-B", texttospeech.SsmlVoiceGender.MALE),
]

count = 0
for voice_name, gender in VOICES:
    for text in TEXTS:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_name[:5],
            name=voice_name,
            ssml_gender=gender,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        filename = OUTPUT_DIR / f"google_{count:04d}.mp3"
        with open(filename, "wb") as f:
            f.write(response.audio_content)
        print(f"Generated: {filename.name}")
        count += 1

print(f"\nDone! Generated {count} Google TTS clips.")
```

---

### Step 6 — OpenAI TTS (PAID, ~$0.015 per clip)
*Very high quality. Worth paying for at least 100–200 clips.*

**Setup:**
```bash
pip install openai
set OPENAI_API_KEY=your_api_key_here
```

**Generate clips:**
```python
# Save as: scripts/generate_openai_tts.py
# Run with: python scripts/generate_openai_tts.py

from openai import OpenAI
from pathlib import Path

OUTPUT_DIR = Path("datasets/raw/synthetic/openai")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

client = OpenAI()

TEXTS = [
    "Hello, I wanted to confirm our meeting tomorrow at three PM.",
    "The package was delivered this morning to your front door.",
    "Please call me back as soon as you get this message.",
    "Thank you for your time today, I really appreciate your help.",
    "Your order has been shipped and will arrive in two business days.",
    "Can you hear me clearly? I will try calling again in five minutes.",
    "I am reaching out regarding your recent application to the position.",
    "We need to reschedule the appointment for next week if possible.",
    "The weather here has been quite unusual for this time of year.",
    "I just wanted to check in and see how you were doing recently.",
]

VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

count = 0
for voice in VOICES:
    for text in TEXTS:
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice=voice,
            input=text,
        )
        filename = OUTPUT_DIR / f"openai_{count:04d}.mp3"
        response.stream_to_file(str(filename))
        print(f"Generated: {filename.name}  ({voice})")
        count += 1

print(f"\nDone! Generated {count} OpenAI TTS clips.")
print(f"Estimated cost: ~${count * 0.015:.2f}")
```

---

## ✅ Final Checklist

Once you have collected your files, verify the folder structure:

```
datasets/raw/
├── human/
│   ├── librispeech/    ← *.flac files
│   ├── commonvoice/    ← *.mp3 files
│   └── personal/       ← any format
└── synthetic/
    ├── elevenlabs/     ← *.mp3 files (MOST IMPORTANT)
    ├── hume/           ← *.mp3 or *.wav files
    ├── bark/           ← *.wav files (auto-generated)
    ├── xtts/           ← *.wav files (auto-generated)
    ├── google/         ← *.mp3 files (auto-generated)
    └── openai/         ← *.mp3 files (auto-generated)
```

Then run the preparation script:
```bash
cd Quantumear
python scripts/prepare_dataset.py
```

Then train:
```bash
python scripts/train.py --epochs 50
```

---

## 📊 Minimum Viable Dataset

If you just want to get started quickly:

| Source | Target | Time |
|--------|--------|------|
| LibriSpeech `test-clean` (download 346 MB) | ~500 human clips | 15 min |
| ElevenLabs free tier (manual) | ~100 AI clips | 30 min |
| Bark script (run overnight) | ~100 AI clips | 8 hrs |
| **Total** | **~700 clips** | **One evening** |

That's enough to get the model training and see real results. Add more over time.
