# Quick Examples - V5 Custom Voices

## 🚀 1-Minute Setup

```bash
# Install everything
pip install -r requirements_v5.txt
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
sudo apt-get install ffmpeg
```

---

## 📁 File Paths and Formats

### File Paths
- **Just filename**: If file is in current directory → `--voice-sample=voice.wav`
- **Full path**: If file is elsewhere → `--voice-sample=/path/to/voice.wav`

### File Formats

| File Type | Accepted Formats | Need Conversion? |
|-----------|------------------|-----------------|
| Voice sample | **WAV only** | MP3 → WAV required |
| Avatar image | PNG, JPG, GIF, BMP | No |
| Paper | PDF | No |

**Convert MP3 to WAV:**
```bash
ffmpeg -i voice.mp3 -ar 22050 -ac 1 voice.wav
```

---

## ⚡ Quick Examples

### Example 1: Add Just an Avatar (Easiest)

```bash
# Download any character image
wget "https://i.imgur.com/example_elsa.png" -O elsa.png

# Generate video (uses default gTTS voice)
python paper_to_video_v5.py \
    --paper-location="paper.pdf" \
    --avatar-image=elsa.png

# Result: Normal voice + Elsa image on slides
```

---

### Example 2: Clone Elsa's Voice

**Step 1: Get voice sample**
```bash
# Find Frozen clip on YouTube with Elsa speaking
# Example: "Let It Go" speaking parts, or dialogue scenes

# Download audio
youtube-dl "https://youtube.com/watch?v=FROZEN_CLIP" -x --audio-format wav -o elsa_raw.wav

# Extract clean 20-second speech segment (no singing, no music)
ffmpeg -i elsa_raw.wav -ss 00:00:15 -t 00:00:20 -ar 22050 elsa_voice.wav
```

**Step 2: Get Elsa image**
```bash
# Google: "elsa frozen png transparent"
# Download from remove.bg or similar
# Save as elsa_avatar.png
```

**Step 3: Generate video**
```bash
python paper_to_video_v5.py \
    --paper-location="paper.pdf" \
    --voice-engine=coqui \
    --voice-sample=elsa_voice.wav \
    --avatar-image=elsa_avatar.png \
    --summarizer=ollama

# Result: Elsa's cloned voice + image narrating your paper!
```

---

### Example 3: KPOP Idol Voice (Blackpink Example)

**Step 1: Get voice sample**
```bash
# Find Blackpink interview/V-log (Korean or English)
# Example: "Blackpink English interview 2024"

youtube-dl "INTERVIEW_URL" -x --audio-format wav -o bp_raw.wav

# Extract clear speech (avoid music/laughing)
ffmpeg -i bp_raw.wav -ss 00:02:30 -t 00:00:25 -ar 22050 jennie_voice.wav
```

**Step 2: Get idol photo**
```bash
# Download high-quality photo card or official image
# Use remove.bg to remove background
# Save as jennie.png
```

**Step 3: Generate**
```bash
python paper_to_video_v5.py \
    --paper-location="quantum_paper.pdf" \
    --voice-engine=coqui \
    --voice-sample=jennie_voice.wav \
    --avatar-image=jennie.png \
    --summarizer=ollama

# Result: Jennie explaining quantum computing!
```

---

### Example 4: Multiple KPOP Members (Advanced)

**For different voices per section**, modify the script or:

```bash
# Section 1: Jennie narrates Introduction
ffmpeg -i jennie_voice.wav -ss 0 -t 30 section_intro.wav

# Section 2: Jisoo narrates Methods
ffmpeg -i jisoo_voice.wav -ss 0 -t 40 section_methods.wav

# Then manually edit audio files or modify create_video() function
# to use different audio per section
```

---

### Example 5: Your Own Voice

**Step 1: Record yourself**
```bash
# Option A: Use phone voice recorder app, transfer to computer

# Option B: Record on Linux
arecord -d 30 -f cd my_voice.wav

# Option C: Use Audacity (GUI)
# Record → Export as WAV
```

**Step 2: Clean up**
```bash
# Remove silence from beginning/end
ffmpeg -i my_voice.wav -af "silenceremove=1:0:-50dB" my_voice_clean.wav

# Normalize volume
ffmpeg -i my_voice_clean.wav -af "volume=1.5" my_voice_final.wav
```

**Step 3: Generate**
```bash
python paper_to_video_v5.py \
    --paper-location="my_research.pdf" \
    --voice-engine=coqui \
    --voice-sample=my_voice_final.wav \
    --avatar-image=my_photo.png \
    --summarizer=ollama
```

---

## 🎯 Use Cases

### For Fun: Anime Character Explaining Physics
```bash
# Get voice sample from anime (fair use for personal/educational)
# Get character PNG
python paper_to_video_v5.py \
    --paper-location="physics_paper.pdf" \
    --voice-engine=coqui \
    --voice-sample=anime_voice.wav \
    --avatar-image=anime_char.png
```

### For YouTube: Celebrity Paper Reviews
```bash
# Use celebrity interview clips (transformative/educational use)
# Example: "Einstein explains quantum entanglement"
python paper_to_video_v5.py \
    --paper-location="entanglement_paper.pdf" \
    --voice-engine=coqui \
    --voice-sample=einstein_voice.wav \
    --avatar-image=einstein.png
```

### For Education: Teacher Avatar
```bash
# Record your own voice teaching style
# Use your photo
python paper_to_video_v5.py \
    --paper-location="textbook_chapter.pdf" \
    --voice-engine=coqui \
    --voice-sample=teacher_voice.wav \
    --avatar-image=teacher_photo.png
```

---

## 🔧 Voice Sample Sources

### Free Voice Samples

1. **YouTube Interviews**
   ```bash
   youtube-dl "URL" -x --audio-format wav
   ```

2. **Movie/TV Clips** (Fair use: educational/transformative)
   ```bash
   ffmpeg -i movie_clip.mp4 -vn -ar 22050 voice.wav
   ```

3. **Podcast Clips**
   ```bash
   wget "podcast.mp3"
   ffmpeg -i podcast.mp3 -ar 22050 voice.wav
   ```

4. **Video Game Dialogue** (extract from game files)

5. **Your Own Recordings**

### Best Practices

**Good segments:**
- Interviews (clean speech)
- Audiobooks
- Lectures/presentations
- V-logs (casual speech)

**Avoid:**
- Singing
- Background music
- Multiple speakers talking
- Noisy environments

---

## 🎨 Avatar Image Sources

### Free Avatar Sources

1. **Official Character Art**
   - Disney official site
   - KPOP official photos
   - Movie promotional materials

2. **Fan Art** (with attribution)
   - DeviantArt
   - ArtStation
   - Pinterest

3. **Remove Background**
   - https://remove.bg (100 free/month)
   - Photopea (free Photoshop alternative)
   - GIMP (open source)

### Image Preparation

```bash
# Download image
wget "IMAGE_URL" -O avatar_raw.png

# Remove background (if needed)
# Use remove.bg website

# Resize to optimal size
convert avatar_raw.png -resize 300x400 avatar.png

# Add transparency (if white background)
convert avatar.png -fuzz 10% -transparent white avatar_final.png
```

---

## 🐛 Common Issues

### Issue 1: "TTS module not found"

```bash
pip install TTS
# If still fails:
pip install torch torchaudio
pip install TTS
```

### Issue 2: Voice sounds bad

**Try:**
1. Get longer voice sample (20-30 seconds better than 10)
2. Remove background noise:
   ```bash
   ffmpeg -i noisy.wav -af "highpass=f=200,lowpass=f=3000" clean.wav
   ```
3. Use ElevenLabs instead (better quality, costs $5/mo)

### Issue 3: Avatar doesn't appear

**Check:**
```bash
# File exists?
ls -lh elsa.png

# Is it PNG or JPG?
file elsa.png

# Try absolute path
python paper_to_video_v5.py --avatar-image=/full/path/to/elsa.png
```

---

## 📹 Output Quality

**Voice quality depends on:**
- Sample quality (bitrate, noise level)
- Sample length (longer = better)
- TTS engine (Coqui < ElevenLabs)

**Expected results:**
- **gTTS:** Robotic but clear
- **Coqui:** 70-80% similarity to original voice
- **ElevenLabs:** 90-95% similarity (nearly identical)

---

## 💰 Cost Comparison

| Method | Setup | Per Video | Quality |
|--------|-------|-----------|---------|
| gTTS + Avatar | Free | Free | ⭐⭐⭐ |
| Coqui + Avatar | Free | Free | ⭐⭐⭐⭐ |
| ElevenLabs + Avatar | $5-11/mo | ~$0.10-0.50 | ⭐⭐⭐⭐⭐ |

---

## 🎬 Complete Workflow Example

```bash
# 1. Setup (once)
pip install -r requirements_v5.txt
ollama pull llama3.2

# 2. Get voice (20 seconds of clean speech)
youtube-dl "VOICE_URL" -x --audio-format wav
ffmpeg -i input.wav -ss 00:01:00 -t 00:00:20 -ar 22050 voice.wav

# 3. Get avatar (PNG with transparent background)
# Download from internet, save as avatar.png

# 4. Generate video!
python paper_to_video_v5.py \
    --paper-location="paper.pdf" \
    --summarizer=ollama \
    --voice-engine=coqui \
    --voice-sample=voice.wav \
    --avatar-image=avatar.png

# 5. Upload to YouTube!
```

**Time:** ~5 minutes setup, ~2 minutes per video after that

---

**Quick Command Reference:**

```bash
# Basic (default voice + avatar)
python paper_to_video_v5.py --paper-location=X.pdf --avatar-image=Y.png

# Voice cloning (KPOP/Elsa/etc)
python paper_to_video_v5.py --paper-location=X.pdf --voice-engine=coqui --voice-sample=V.wav --avatar-image=Y.png

# Full custom
python paper_to_video_v5.py --paper-location=X.pdf --summarizer=ollama --voice-engine=coqui --voice-sample=V.wav --avatar-image=Y.png
```

**That's it! You can now create videos with KPOP idols or Elsa explaining academic papers! 🎤✨**
