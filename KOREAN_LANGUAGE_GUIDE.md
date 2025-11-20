# Korean Language Video Generation Guide

## ✅ YES! You Can Generate Korean Videos!

**Input:** English academic paper (PDF)
**Output:** Korean summary + Korean narration + Korean slides

All features from V5 work exactly the same:
- ✅ KPOP idol voices (in Korean!)
- ✅ Elsa voice (speaking Korean!)
- ✅ Avatar images
- ✅ Figures from PDF
- ✅ Professional slides
- ✅ Perfect sync

---

## 🚀 Quick Start

### Basic Korean Video

```bash
python paper_to_video_v5_multilang.py \
    --paper-location="english_paper.pdf" \
    --language=ko \
    --summarizer=ollama \
    --voice-engine=coqui
```

**What happens:**
1. Reads English PDF
2. Ollama generates Korean summary
3. Coqui TTS speaks in Korean
4. Slides display Korean text
5. Video narrated in Korean!

---

## 🎤 Korean Voice Options

### Option 1: KPOP Idol Voice (Recommended!)

```bash
# 1. Get KPOP voice sample (20 seconds Korean speech)
youtube-dl "BLACKPINK_KOREAN_INTERVIEW" -x --audio-format wav
ffmpeg -i interview.wav -ss 00:01:00 -t 00:00:20 -ar 22050 jennie_ko.wav

# 2. Get idol image
# Save as jennie.png

# 3. Generate Korean video with KPOP voice!
python paper_to_video_v5_multilang.py \
    --paper-location="quantum_paper.pdf" \
    --language=ko \
    --summarizer=ollama \
    --voice-engine=coqui \
    --voice-sample=jennie_ko.wav \
    --avatar-image=jennie.png
```

**Result:** Jennie from Blackpink explaining quantum physics in Korean! 🇰🇷

### Option 2: Elsa Speaking Korean

```bash
# 1. Get Korean-dubbed Frozen voice clip
# (Elsa from Korean version of Frozen)
ffmpeg -i frozen_korean.mp4 -vn -ar 22050 elsa_korean.wav

# 2. Generate video
python paper_to_video_v5_multilang.py \
    --paper-location="paper.pdf" \
    --language=ko \
    --voice-engine=coqui \
    --voice-sample=elsa_korean.wav \
    --avatar-image=elsa.png
```

### Option 3: gTTS Korean Voice (Simplest)

```bash
python paper_to_video_v5_multilang.py \
    --paper-location="paper.pdf" \
    --language=ko
```

No voice sample needed - uses Google's Korean TTS.

---

## 🔧 Installation

### 1. Install Korean Font

```bash
# Ubuntu/Debian
sudo apt-get install fonts-nanum

# Or download manually
wget "http://cdn.naver.com/naver/NanumFont/fontfiles/NanumFont_TTF_ALL.zip"
unzip NanumFont_TTF_ALL.zip
sudo cp *.ttf /usr/share/fonts/truetype/nanum/
fc-cache -f -v
```

### 2. Install Python Packages

```bash
pip install -r requirements_v5.txt
pip install TTS  # For Korean voice cloning
```

### 3. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2  # Supports Korean!
```

---

## 📖 How It Works

### Text Generation (Ollama → Korean)

The multilingual version sends Korean instructions to Ollama:

```python
prompt = """
다음 학술 논문을 짧은 비디오 프레젠테이션을 위한 핵심 섹션으로 한국어로 요약하세요.

다음과 같은 정확한 형식을 사용하세요:

## 제목
[논문 제목을 한국어로]

## 초록
[한국어로 2-3문장]
...
"""
```

**Input:** English paper
**Output:** Korean summary with sections

**Example output:**
```
## 제목
양자 비전 트랜스포머

## 초록
이 논문은 이미지 분류를 위한 양자 비전 트랜스포머를 소개합니다...
```

### Voice Synthesis (Coqui → Korean Speech)

Coqui TTS XTTS v2 model supports Korean:

```python
tts.tts_to_file(
    text="양자 컴퓨팅의 주요 특징은...",
    file_path="audio.mp3",
    language="ko"  # Korean!
)
```

If you provide a Korean voice sample, it clones that voice speaking Korean!

### Slides (Korean Text Rendering)

Uses NanumGothic font for proper Korean display:

```python
font = ImageFont.truetype("NanumGothic.ttf", 52)
draw.text((x, y), "양자 컴퓨팅", font=font)
```

Result: Beautiful Korean text on slides!

---

## 🎬 Complete Example

### Generate Korean Video with KPOP Voice

```bash
# === PREPARE ASSETS ===

# 1. Get KPOP voice (Korean interview/V-log)
youtube-dl "https://youtube.com/watch?v=KPOP_KOREAN" -x --audio-format wav

# 2. Extract clean Korean speech (20 seconds)
ffmpeg -i KPOP_KOREAN.wav -ss 00:00:30 -t 00:00:20 -ar 22050 kpop_voice_ko.wav

# 3. Get idol image with transparent background
# Save as kpop_idol.png

# === GENERATE VIDEO ===

python paper_to_video_v5_multilang.py \
    --paper-location="machine_learning_paper.pdf" \
    --language=ko \
    --summarizer=ollama \
    --voice-engine=coqui \
    --voice-sample=kpop_voice_ko.wav \
    --avatar-image=kpop_idol.png
```

**Output:**
```
✓ Created output directory: paper_20251119_123456
📄 Reading local paper...
📝 Extracting text...
   Extracted 45000 characters
🖼️  Extracting figures...
   Extracted 3 figures
🤖 Generating KO summary using ollama...
   Using Ollama (language: ko)...
🧹 Cleaning and parsing...
   Parsed 6 sections
🎤 Generating KO voiceover using coqui...
   Voice sample: kpop_voice_ko.wav
   Section 0 (제목): Using Coqui TTS...
      Cloning voice from: kpop_voice_ko.wav
      Duration: 2.8s
   Section 1 (초록): Using Coqui TTS...
      Duration: 15.2s
   ...
🎨 Creating KO slides...
   Using avatar: kpop_idol.png
   Created 12 slides
🎬 Compiling video...

✅ VIDEO GENERATION COMPLETE!
📹 Video: paper_20251119_123456/output.mp4
🗣️  Language: KO
🎵 Voice engine: coqui
```

**Result:** KPOP idol presenting machine learning paper in Korean! 🎤🇰🇷

---

## 🌍 Other Languages Supported

The multilingual version also supports:

```bash
# Japanese
--language=ja

# Chinese (Simplified)
--language=zh

# English (default)
--language=en
```

**Usage:**
```bash
# Japanese video
python paper_to_video_v5_multilang.py \
    --paper-location="paper.pdf" \
    --language=ja \
    --summarizer=ollama

# Chinese video
python paper_to_video_v5_multilang.py \
    --paper-location="paper.pdf" \
    --language=zh \
    --summarizer=ollama
```

---

## 🔍 Troubleshooting

### Korean text shows as boxes (□□□)

**Cause:** Korean font not installed

**Solution:**
```bash
sudo apt-get install fonts-nanum
fc-cache -f -v
```

### Korean TTS sounds robotic

**Cause:** Using gTTS (basic quality)

**Solution:** Use Coqui with Korean voice sample:
```bash
# Get 20-second Korean voice sample
# Use with --voice-engine=coqui --voice-sample=korean_voice.wav
```

### Ollama generates English instead of Korean

**Cause:** Model doesn't support Korean well

**Solution:** Try different model:
```bash
# Better Korean support
ollama pull llama3.1
# Or
ollama pull qwen2.5
```

Then modify the script line 102 to use that model.

---

## 💡 Best Practices for Korean Videos

### Voice Sample Tips

**Good Korean voice samples:**
- ✅ Korean interviews (natural speech)
- ✅ Korean V-logs
- ✅ Korean audiobooks
- ✅ Korean dubbed movies/anime
- ✅ Korean news broadcasts

**Avoid:**
- ❌ K-pop songs (singing, not speaking)
- ❌ Mixed Korean-English speech
- ❌ Noisy background

### Finding Korean Voice Samples

```bash
# Korean interviews
youtube-dl "아이유 인터뷰" -x --audio-format wav

# Korean audiobooks
youtube-dl "한국어 오디오북" -x --audio-format wav

# Korean movie clips
youtube-dl "겨울왕국 한국어" -x --audio-format wav  # Frozen in Korean
```

Extract clean 20-second segment:
```bash
ffmpeg -i korean_audio.wav -ss 00:01:00 -t 00:00:20 -ar 22050 korean_voice.wav
```

---

## 📊 Korean vs English Comparison

| Feature | English | Korean |
|---------|---------|--------|
| **Ollama summarization** | ✅ Excellent | ✅ Very Good |
| **Coqui TTS quality** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Voice cloning** | ✅ Works | ✅ Works |
| **Font rendering** | ✅ Native | ✅ NanumGothic |
| **gTTS quality** | ⭐⭐⭐ | ⭐⭐⭐ |

**Verdict:** Korean works just as well as English!

---

## 🎯 Use Cases

### 1. Korean Educational Content
```bash
# Explain English research papers in Korean for Korean students
python paper_to_video_v5_multilang.py \
    --paper-location="english_paper.pdf" \
    --language=ko \
    --summarizer=ollama
```

### 2. KPOP Edu-tainment
```bash
# KPOP idol teaching science in Korean
python paper_to_video_v5_multilang.py \
    --paper-location="science_paper.pdf" \
    --language=ko \
    --voice-sample=kpop_voice.wav \
    --avatar-image=idol.png
```

### 3. Korean YouTube Channel
```bash
# Generate unlimited Korean videos for YouTube
for paper in papers/*.pdf; do
    python paper_to_video_v5_multilang.py \
        --paper-location="$paper" \
        --language=ko \
        --voice-sample=my_korean_voice.wav \
        --avatar-image=my_avatar.png
done
```

---

## ✅ Summary

**To generate Korean videos:**

```bash
# Install Korean font
sudo apt-get install fonts-nanum

# Generate video
python paper_to_video_v5_multilang.py \
    --paper-location="english_paper.pdf" \
    --language=ko \
    --summarizer=ollama \
    --voice-engine=coqui \
    --voice-sample=korean_voice.wav \
    --avatar-image=avatar.png
```

**Result:**
- ✅ Reads English PDF
- ✅ Generates Korean summary
- ✅ Korean voice narration
- ✅ Korean text on slides
- ✅ KPOP/Elsa voice (optional)
- ✅ 100% free, unlimited!

**Perfect for Korean YouTube channels, education, and KPOP edu-tainment! 🇰🇷🎤**
