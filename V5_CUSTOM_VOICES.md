# V5: Custom Voices & Avatars (KPOP/Elsa/Any Character!)

**Version:** 5.0
**File:** `paper_to_video_v5.py`

---

## 🎯 What's New in V5

**Custom Voice Narrators:**
- ✅ KPOP idol voices
- ✅ Elsa from Frozen
- ✅ Any celebrity/character voice
- ✅ Your own voice

**Avatar Integration:**
- ✅ Character images appear on slides
- ✅ KPOP idols presenting papers
- ✅ Elsa as lecturer
- ✅ Animated talking heads (optional)

---

## 🎤 Voice Options

### Option 1: Coqui TTS (Voice Cloning) ⭐ RECOMMENDED

**What it does:** Clones any voice from a 10-second audio sample

**Setup:**
```bash
pip install TTS
```

**Get voice samples:**
```bash
# Example: Download KPOP idol voice sample
# You need a 10-30 second WAV/MP3 of the person speaking
# Can be from:
# - YouTube clips (use youtube-dl + ffmpeg to extract)
# - Interviews
# - V-logs
# - Audio recordings
```

**Create Elsa voice:**
```bash
# 1. Find Elsa voice clip from Frozen movie
# 2. Extract 10-30 seconds of clean speech (no music)
# 3. Convert to WAV:
ffmpeg -i elsa_clip.mp4 -vn -ar 22050 elsa_voice.wav

# 4. Generate video with Elsa voice:
python paper_to_video_v5.py \
    --paper-location="paper.pdf" \
    --voice-engine=coqui \
    --voice-sample=elsa_voice.wav \
    --avatar-image=elsa.png
```

**Create KPOP idol voice:**
```bash
# 1. Get voice sample (e.g., Blackpink Jennie, Aespa Karina, etc.)
ffmpeg -i kpop_interview.mp4 -vn -ar 22050 kpop_voice.wav

# 2. Generate video:
python paper_to_video_v5.py \
    --paper-location="paper.pdf" \
    --voice-engine=coqui \
    --voice-sample=kpop_voice.wav \
    --avatar-image=kpop_idol.png
```

**Quality:** ⭐⭐⭐⭐⭐ (Very realistic)
**Cost:** Free
**Privacy:** Local (offline)

---

### Option 2: ElevenLabs API (Premium Quality)

**What it does:** Professional voice cloning and premade voices

**Setup:**
```bash
# 1. Sign up at https://elevenlabs.io
# 2. Get API key
# 3. Add to script:
ELEVENLABS_API_KEY = "your_key_here"  # Line 18 in v5.py

# 4. Clone voice on ElevenLabs website (upload 1-5 minutes of audio)
# 5. Get voice_id from ElevenLabs dashboard
```

**Usage:**
```python
# Modify line 258 in v5.py:
def text_to_speech_elevenlabs(text, output_path, voice_id="YOUR_VOICE_ID"):
```

```bash
python paper_to_video_v5.py \
    --paper-location="paper.pdf" \
    --voice-engine=elevenlabs \
    --avatar-image=character.png
```

**Premade voices available:**
- Rachel (American female)
- Adam (American male)
- Bella (British female)
- Many celebrity-like voices

**Quality:** ⭐⭐⭐⭐⭐ (Best)
**Cost:** $5-11/month (10k-30k characters)
**Privacy:** Cloud-based

---

### Option 3: gTTS (Default, Simple)

**Usage:**
```bash
python paper_to_video_v5.py \
    --paper-location="paper.pdf" \
    --voice-engine=gtts \
    --avatar-image=character.png
```

**Quality:** ⭐⭐⭐ (Basic)
**Cost:** Free
**Privacy:** Cloud-based

---

## 👤 Avatar Images

### Prepare Avatar Images

**Requirements:**
- PNG or JPG format
- Transparent background (PNG with alpha channel) recommended
- Portrait orientation
- 300x400 pixels or larger (will be resized)

**Where to get avatars:**

1. **Elsa from Frozen:**
   ```bash
   # Download high-quality PNG from:
   # - Official Disney art
   # - Fan art sites (DeviantArt, Pinterest)
   # - Google Images → Tools → Type → Transparent

   # Example:
   wget "https://example.com/elsa.png" -O elsa_avatar.png
   ```

2. **KPOP Idols:**
   ```bash
   # Sources:
   # - Official photo cards (scan or high-res download)
   # - Twitter fan accounts
   # - Google Images → High resolution

   # Remove background (if not transparent):
   # Use remove.bg website or Photoshop
   ```

3. **Create transparent background:**
   ```bash
   # Using ImageMagick:
   convert character.jpg -fuzz 10% -transparent white character.png

   # Or use online tool: https://remove.bg
   ```

### Avatar Placement in Videos

**Title slides:**
- Avatar appears on left side (300x400px)
- Text appears on right side
- Creates "presenter introducing topic" effect

**Content slides:**
- Avatar appears bottom-left corner
- Text area adjusted to not overlap
- Creates "lecturer explaining content" effect

---

## 🎬 Complete Examples

### Example 1: Elsa Narrating Quantum Physics Paper

```bash
# 1. Prepare Elsa voice sample
ffmpeg -i frozen_elsa_clip.mp4 -vn -ar 22050 -ss 00:01:00 -t 00:00:20 elsa_voice.wav

# 2. Get Elsa avatar image
wget "https://example.com/elsa_transparent.png" -O elsa.png

# 3. Generate video
python paper_to_video_v5.py \
    --paper-location="quantum_paper.pdf" \
    --summarizer=ollama \
    --voice-engine=coqui \
    --voice-sample=elsa_voice.wav \
    --avatar-image=elsa.png

# Output: Elsa's voice narrating quantum physics with her image on slides!
```

### Example 2: KPOP Idol Group Presenting Machine Learning

```bash
# 1. Get KPOP voice sample (e.g., from interview/V-log)
youtube-dl "https://youtube.com/watch?v=KPOP_INTERVIEW" -x --audio-format wav
ffmpeg -i interview.wav -ar 22050 -ss 00:00:30 -t 00:00:15 kpop_voice.wav

# 2. Get idol image
# Download from Twitter/Instagram, remove background
# Save as kpop_idol.png

# 3. Generate video
python paper_to_video_v5.py \
    --paper-location="ml_paper.pdf" \
    --summarizer=ollama \
    --voice-engine=coqui \
    --voice-sample=kpop_voice.wav \
    --avatar-image=kpop_idol.png
```

### Example 3: Your Own Voice as Narrator

```bash
# 1. Record yourself speaking for 20-30 seconds
# Use phone voice recorder or:
ffmpeg -f alsa -i default -t 30 my_voice.wav

# 2. Get your photo (optional)
# Take selfie, remove background
# Save as my_avatar.png

# 3. Generate video
python paper_to_video_v5.py \
    --paper-location="my_paper.pdf" \
    --summarizer=ollama \
    --voice-engine=coqui \
    --voice-sample=my_voice.wav \
    --avatar-image=my_avatar.png
```

---

## 🎨 Visual Examples

### Before (V4): Plain slides

```
┌────────────────────────────────────┐
│         Introduction               │ ← Just text
│                                    │
└────────────────────────────────────┘
```

### After (V5): With Elsa avatar

```
┌────────────────────────────────────┐
│  ┌─────┐                           │
│  │     │      Introduction          │ ← Elsa image + text
│  │ELSA │                            │    Elsa's voice!
│  │     │                            │
│  └─────┘                            │
└────────────────────────────────────┘
```

---

## 🔧 Advanced: Animated Talking Heads (Future)

For truly animated avatars (lips moving with speech), you can post-process:

```bash
# Install SadTalker
git clone https://github.com/OpenTalker/SadTalker
cd SadTalker
pip install -r requirements.txt

# Generate talking head video
python inference.py \
    --driven_audio voiceover.mp3 \
    --source_image elsa.png \
    --result_dir ./results/

# Then composite onto slides using moviepy
```

Or use services like:
- D-ID (https://d-id.com) - $5/month
- HeyGen (https://heygen.com) - $24/month

---

## 📋 Installation

```bash
# Basic
pip install -r requirements_v4.txt

# Add Coqui TTS for voice cloning
pip install TTS

# For audio extraction
sudo apt-get install ffmpeg youtube-dl
```

---

## 🎯 Quick Start Guide

### Beginner: Use existing voice with avatar

```bash
# Just add avatar image (no voice cloning)
python paper_to_video_v5.py \
    --paper-location="paper.pdf" \
    --avatar-image=elsa.png
```

### Intermediate: Clone voice from sample

```bash
# 1. Get 20-second voice sample
ffmpeg -i video.mp4 -vn -ar 22050 voice.wav

# 2. Run with voice cloning
python paper_to_video_v5.py \
    --paper-location="paper.pdf" \
    --voice-engine=coqui \
    --voice-sample=voice.wav \
    --avatar-image=avatar.png
```

### Advanced: Full custom setup

```bash
# 1. Extract voice
youtube-dl URL -x --audio-format wav
ffmpeg -i input.wav -ar 22050 -ss START -t DURATION voice.wav

# 2. Prepare avatar
# Remove background using remove.bg
# Resize if needed: convert avatar.png -resize 300x400 avatar_final.png

# 3. Generate
python paper_to_video_v5.py \
    --paper-location="paper.pdf" \
    --summarizer=ollama \
    --voice-engine=coqui \
    --voice-sample=voice.wav \
    --avatar-image=avatar_final.png
```

---

## 🎤 Voice Sample Tips

**Good voice samples:**
- ✅ Clear speech, no background music
- ✅ 10-30 seconds (longer is better, up to 5 minutes for ElevenLabs)
- ✅ Natural speaking pace
- ✅ Variety of tones/emotions
- ✅ Good audio quality (no static/noise)

**Bad voice samples:**
- ❌ Heavy background music
- ❌ Multiple people talking
- ❌ Poor audio quality
- ❌ Too short (< 5 seconds)
- ❌ Singing instead of speaking

**Extract clean speech:**
```bash
# Remove background noise
ffmpeg -i noisy.wav -af "highpass=f=200, lowpass=f=3000" clean.wav

# Normalize volume
ffmpeg -i quiet.wav -af "volume=2.0" loud.wav

# Extract specific segment
ffmpeg -i long.wav -ss 00:01:30 -t 00:00:20 segment.wav
```

---

## 🔍 Troubleshooting

### Coqui TTS fails

```
Error: Could not import TTS
```
**Solution:**
```bash
pip install TTS
# If still fails:
pip install torch torchaudio  # May need PyTorch first
pip install TTS
```

### Voice sounds robotic

**Cause:** Voice sample quality is poor

**Solution:**
1. Get better quality voice sample (higher bitrate)
2. Extract longer sample (20-30 seconds)
3. Remove background noise before using
4. Try ElevenLabs (better quality)

### Avatar doesn't appear

**Cause:** Image path wrong or format unsupported

**Solution:**
```bash
# Check file exists
ls -lh elsa.png

# Convert to PNG if needed
convert avatar.jpg avatar.png

# Verify path is absolute or relative to working directory
python paper_to_video_v5.py --avatar-image=/full/path/to/avatar.png
```

---

## 💡 Creative Ideas

### Idea 1: KPOP Group Presenting Together
- Use 4 different KPOP voices for 4 sections
- Modify script to use different voice per section
- Avatar changes per section

### Idea 2: Elsa Teaching Children's Science
- Use Elsa voice + avatar
- Simplify paper summary (ask Ollama for kid-friendly version)
- Add more colorful slides

### Idea 3: Celebrity Panel Discussion
- Multiple voices debating paper
- Different avatars per section
- "Intro by Einstein, Methods by Feynman, Results by Hawking"

### Idea 4: Your Personal Brand
- Use your own voice
- Use your photo as avatar
- Create series of paper review videos for YouTube

---

## 📊 Comparison

| Feature | gTTS (V4) | Coqui (V5) | ElevenLabs (V5) |
|---------|-----------|------------|-----------------|
| Voice quality | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Custom voices | ❌ | ✅ Free | ✅ $5-11/mo |
| KPOP/Elsa voices | ❌ | ✅ | ✅ |
| Offline | ❌ | ✅ | ❌ |
| Setup difficulty | Easy | Medium | Easy |
| Sample needed | None | 10-30s | 1-5min |

---

## ✅ Recommended Workflow for KPOP/Elsa Videos

```bash
# 1. Choose your character
CHARACTER="Elsa"  # or "Blackpink Jennie", "Aespa Karina", etc.

# 2. Get voice sample (YouTube clip)
youtube-dl "VIDEO_URL" -x --audio-format wav -o voice_raw.wav

# 3. Extract clean segment
ffmpeg -i voice_raw.wav -ss 00:01:00 -t 00:00:20 -ar 22050 voice_clean.wav

# 4. Get avatar image
# Download PNG with transparent background
# Save as avatar.png

# 5. Generate video!
python paper_to_video_v5.py \
    --paper-location="paper.pdf" \
    --summarizer=ollama \
    --voice-engine=coqui \
    --voice-sample=voice_clean.wav \
    --avatar-image=avatar.png

# 6. Share on YouTube!
```

---

**Result:** Academic papers narrated by your favorite KPOP idols, Elsa, or any character you choose! 🎤✨

---

**Files:**
- `paper_to_video_v5.py` - Main script with voice cloning
- `V5_CUSTOM_VOICES.md` - This guide

**Quick test:**
```bash
pip install TTS
python paper_to_video_v5.py --paper-location="test.pdf" --avatar-image=character.png
```
