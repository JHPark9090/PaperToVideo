import os
import requests
import pypdf
import fitz  # PyMuPDF
import io
from gtts import gTTS
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
from pydub import AudioSegment
from PIL import Image, ImageDraw, ImageFont
import argparse
import datetime
import re
import subprocess

# API Keys (OPTIONAL)
GEMINI_API_KEY = None  # Set if using --summarizer=gemini
ELEVENLABS_API_KEY = None  # Set if using --voice-engine=elevenlabs

# Language-specific font mapping
LANGUAGE_FONTS = {
    'en': 'DejaVuSans.ttf',
    'ko': 'NanumGothic.ttf',  # Korean font
    'ja': 'NotoSansJP-Regular.ttf',  # Japanese
    'zh': 'NotoSansSC-Regular.ttf',   # Simplified Chinese
}

def download_paper(url):
    """Downloads the paper from the given URL."""
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def read_local_pdf(file_path):
    """Reads a local PDF file."""
    with open(file_path, "rb") as f:
        return f.read()

def extract_text_from_pdf(pdf_content):
    """Extracts text from PDF."""
    text = ""
    with io.BytesIO(pdf_content) as f:
        reader = pypdf.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_images_from_pdf(pdf_content, output_dir, max_images=5):
    """Extracts images from PDF using PyMuPDF."""
    images = []
    try:
        with io.BytesIO(pdf_content) as f:
            doc = fitz.open(stream=f, filetype="pdf")
            img_count = 0
            for page_num in range(min(len(doc), 10)):
                page = doc[page_num]
                image_list = page.get_images()

                for img_index, img_info in enumerate(image_list):
                    if img_count >= max_images:
                        break

                    xref = img_info[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]

                    img = Image.open(io.BytesIO(image_bytes))
                    if img.width < 200 or img.height < 100:
                        continue

                    image_path = os.path.join(output_dir, f"figure_{img_count+1}.png")
                    img.save(image_path)
                    images.append(image_path)
                    img_count += 1

                    if img_count >= max_images:
                        break
            doc.close()
    except Exception as e:
        print(f"⚠️  Could not extract images: {e}")
    return images

def get_language_prompt(language='en'):
    """Returns language-specific prompt template."""
    prompts = {
        'en': {
            'instruction': 'Summarize the following academic paper into key sections for a short video presentation in ENGLISH.',
            'format': '''
Use this EXACT format with markdown headers (##):

## Title
[Paper title in English]

## Abstract
[2-3 sentences in English]

## Introduction
[3-4 complete sentences in English]

## Methods
[4-5 sentences in English]

## Results
[3-4 sentences in English]

## Conclusion
[2-3 sentences in English]

IMPORTANT: Use complete English sentences with proper punctuation. Do NOT include preamble. Start with "## Title".'''
        },
        'ko': {
            'instruction': '다음 학술 논문을 짧은 비디오 프레젠테이션을 위한 핵심 섹션으로 한국어로 요약하세요.',
            'format': '''
다음과 같은 정확한 형식을 사용하세요 (## 마크다운 헤더 사용):

## 제목
[논문 제목을 한국어로]

## 초록
[한국어로 2-3문장]

## 서론
[한국어로 3-4문장으로 문제와 동기를 설명]

## 방법론
[한국어로 4-5문장으로 접근법 설명]

## 결과
[한국어로 3-4문장으로 주요 발견 강조]

## 결론
[한국어로 2-3문장으로 핵심 요점과 영향 설명]

중요: 완전한 한국어 문장을 사용하고 적절한 구두점을 사용하세요. 서론이나 전처리 문구를 포함하지 마세요. "## 제목"으로 바로 시작하세요.'''
        }
    }
    return prompts.get(language, prompts['en'])

def summarize_with_ollama(text, model="llama3.2", language='en'):
    """Summarizes text using local Ollama LLM in specified language."""
    prompt_template = get_language_prompt(language)

    prompt = f"""{prompt_template['instruction']}

{prompt_template['format']}

Paper text:
---
{text[:15000]}"""

    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            raise Exception(f"Ollama failed: {result.stderr}")
    except FileNotFoundError:
        raise Exception("Ollama not installed. Install: curl -fsSL https://ollama.com/install.sh | sh")

def summarize_with_gemini(text, model="gemini-1.5-flash", language='en'):
    """Summarizes text using Gemini API in specified language."""
    if not GEMINI_API_KEY:
        raise Exception("Gemini API key not set. Use --summarizer=ollama (free, local)")

    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
    except ImportError:
        raise Exception("google-generativeai not installed. Use --summarizer=ollama")

    prompt_template = get_language_prompt(language)
    prompt = f"""{prompt_template['instruction']}

{prompt_template['format']}

Paper text:
---
{text[:15000]}"""

    gemini_model = genai.GenerativeModel(model)
    response = gemini_model.generate_content(prompt)
    return response.text

def summarize_text(text, method="ollama", language='en'):
    """Summarizes text using specified method and language."""
    if method == "ollama":
        print(f"   Using Ollama (language: {language})...")
        return summarize_with_ollama(text, language=language)
    elif method == "gemini":
        print(f"   Using Gemini API (language: {language})...")
        return summarize_with_gemini(text, language=language)
    elif method == "manual":
        print("   Using manual summary...")
        if os.path.exists("summary.txt"):
            with open("summary.txt", "r", encoding='utf-8') as f:
                return f.read()
        else:
            raise Exception("Manual mode requires summary.txt")
    else:
        raise ValueError(f"Unknown summarizer: {method}")

def clean_gemini_response(text):
    """Cleans AI response by removing preamble."""
    lines = text.split('\n')
    cleaned_lines = []
    started = False

    for line in lines:
        line_lower = line.lower().strip()
        if not started:
            # English and Korean preamble patterns
            skip_patterns = [
                'of course', 'here is', 'here\'s', 'i\'ll provide',
                'let me', 'i can', 'certainly', 'sure', 'formatted into',
                '물론', '여기', '다음은', '제공', '요약'
            ]
            if any(pattern in line_lower for pattern in skip_patterns) and len(line_lower) < 100:
                continue
            started = True
        cleaned_lines.append(line)

    return '\n'.join(cleaned_lines).strip()

def parse_markdown_to_sections(text):
    """Parses markdown into sections (supports multilingual headers)."""
    sections = []
    current_title = None
    current_content = []

    for line in text.split('\n'):
        if line.strip().startswith('##'):
            if current_title:
                sections.append({
                    'title': current_title,
                    'content': '\n'.join(current_content).strip()
                })
            current_title = line.replace('##', '').strip()
            current_content = []
        elif line.strip().startswith('**') and line.strip().endswith('**'):
            if current_title:
                sections.append({
                    'title': current_title,
                    'content': '\n'.join(current_content).strip()
                })
            current_title = line.replace('**', '').strip()
            current_content = []
        else:
            if line.strip():
                current_content.append(line)

    if current_title:
        sections.append({
            'title': current_title,
            'content': '\n'.join(current_content).strip()
        })

    return sections

def clean_text_for_speech(text):
    """Cleans text for TTS (multilingual)."""
    text = re.sub(r'#{1,6}\s+', '', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'([a-z가-힣])\n([A-Z가-힣])', r'\1. \2', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n\s*\n', '. ', text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\.\.+', '.', text)
    return text.strip()

def text_to_speech_coqui(text, output_path, speaker_wav=None, language="en"):
    """Generate speech using Coqui TTS with language support."""
    try:
        from TTS.api import TTS

        # Map language codes for Coqui
        coqui_lang_map = {
            'en': 'en',
            'ko': 'ko',
            'ja': 'ja',
            'zh': 'zh-cn'
        }
        coqui_lang = coqui_lang_map.get(language, 'en')

        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)

        if speaker_wav and os.path.exists(speaker_wav):
            print(f"      Cloning voice from: {speaker_wav}")
            tts.tts_to_file(
                text=text,
                file_path=output_path,
                speaker_wav=speaker_wav,
                language=coqui_lang
            )
        else:
            tts.tts_to_file(
                text=text,
                file_path=output_path,
                language=coqui_lang
            )

        return True
    except ImportError:
        print("      ⚠️  Coqui TTS not installed. Install: pip install TTS")
        return False
    except Exception as e:
        print(f"      ⚠️  Coqui TTS failed: {e}")
        return False

def text_to_speech_elevenlabs(text, output_path, voice_id="EXAVITQu4vr4xnSDxMaL"):
    """Generate speech using ElevenLabs API."""
    if not ELEVENLABS_API_KEY:
        print("      ⚠️  ElevenLabs API key not set")
        return False

    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"      ⚠️  ElevenLabs API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"      ⚠️  ElevenLabs failed: {e}")
        return False

def text_to_speech_per_section(sections, output_dir, voice_engine="gtts", voice_sample=None, language="en"):
    """Generates separate audio file for each section with language support."""
    audio_files = []

    # Map language codes for gTTS
    gtts_lang_map = {
        'en': 'en',
        'ko': 'ko',
        'ja': 'ja',
        'zh': 'zh-CN'
    }

    for idx, section in enumerate(sections):
        text_parts = [section['title'] + '.']
        if section['content']:
            text_parts.append(section['content'])

        combined_text = ' '.join(text_parts)
        clean_text = clean_text_for_speech(combined_text)

        audio_path = os.path.join(output_dir, f"audio_section_{idx:02d}.mp3")

        success = False

        if voice_engine == "coqui":
            print(f"   Section {idx} ({section['title']}): Using Coqui TTS...")
            success = text_to_speech_coqui(clean_text, audio_path, speaker_wav=voice_sample, language=language)

        elif voice_engine == "elevenlabs":
            print(f"   Section {idx} ({section['title']}): Using ElevenLabs...")
            success = text_to_speech_elevenlabs(clean_text, audio_path)

        # Fallback to gTTS
        if not success or voice_engine == "gtts":
            if voice_engine != "gtts":
                print(f"      Falling back to gTTS...")
            gtts_lang = gtts_lang_map.get(language, 'en')
            tts = gTTS(text=clean_text, lang=gtts_lang, slow=False)
            tts.save(audio_path)

        # Get duration
        audio = AudioSegment.from_mp3(audio_path)
        duration = len(audio) / 1000.0

        audio_files.append((audio_path, duration))
        print(f"      Duration: {duration:.1f}s")

    return audio_files

def get_font_for_language(language, size, style='regular'):
    """Returns appropriate font for the language."""
    # Try to find language-specific font
    font_name = LANGUAGE_FONTS.get(language, 'DejaVuSans.ttf')

    # Try multiple possible locations
    font_paths = [
        font_name,
        f"/usr/share/fonts/truetype/nanum/{font_name}",
        f"/usr/share/fonts/truetype/noto/{font_name}",
        f"/System/Library/Fonts/{font_name}",
        "DejaVuSans.ttf"  # Fallback
    ]

    for font_path in font_paths:
        try:
            return ImageFont.truetype(font_path, size)
        except:
            continue

    # Ultimate fallback to default
    return ImageFont.load_default()

def wrap_text(text, font, max_width):
    """Wraps text to fit within max_width (multilingual)."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        try:
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]
        except:
            width = len(test_line) * 10  # Rough estimate if getbbox fails

        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)

    if current_line:
        lines.append(' '.join(current_line))

    return lines

def create_gradient_background(width, height, color1, color2):
    """Creates a vertical gradient background."""
    base = Image.new('RGB', (width, height), color1)
    top = Image.new('RGB', (width, height), color2)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def create_slides_with_avatar(sections, output_dir, figures=None, avatar_image=None, language='en'):
    """Creates slides with language-appropriate fonts."""
    slides = []
    slide_to_section = []
    figures = figures or []
    figure_idx = 0

    # Load avatar
    avatar = None
    if avatar_image and os.path.exists(avatar_image):
        try:
            avatar = Image.open(avatar_image)
            avatar = avatar.resize((300, 400), Image.Resampling.LANCZOS)
            print(f"   Using avatar: {avatar_image}")
        except Exception as e:
            print(f"   ⚠️  Could not load avatar: {e}")

    # Fonts for language
    title_font = get_font_for_language(language, 52)
    header_font = get_font_for_language(language, 38)
    body_font = get_font_for_language(language, 26)
    small_font = get_font_for_language(language, 20)

    width, height = 1280, 720
    margin = 60

    for idx, section in enumerate(sections):
        # Title slide
        title_image = create_gradient_background(width, height, '#1e3a5f', '#2c5282')
        draw = ImageDraw.Draw(title_image)

        if avatar:
            avatar_x = 50
            avatar_y = (height - 400) // 2
            title_image.paste(avatar, (avatar_x, avatar_y), avatar if avatar.mode == 'RGBA' else None)

        title_text = section['title']
        try:
            title_bbox = title_font.getbbox(title_text)
            title_width = title_bbox[2] - title_bbox[0]
            title_height = title_bbox[3] - title_bbox[1]
        except:
            title_width = len(title_text) * 30
            title_height = 52

        if avatar:
            title_x = 400
            title_y = (height - title_height) // 2
        else:
            title_x = (width - title_width) // 2
            title_y = (height - title_height) // 2

        draw.text((title_x + 3, title_y + 3), title_text, fill='#00000080', font=title_font)
        draw.text((title_x, title_y), title_text, fill='white', font=title_font)

        line_width = min(400, title_width)
        line_x = title_x
        line_y = title_y + title_height + 30
        draw.rectangle([line_x, line_y, line_x + line_width, line_y + 4], fill='#60a5fa')

        title_slide_path = os.path.join(output_dir, f"slide_{len(slides):03d}_title.png")
        title_image.save(title_slide_path)
        slides.append(title_slide_path)
        slide_to_section.append(idx)

        # Content slides
        content = section['content']
        if not content:
            continue

        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]

        content_image = create_gradient_background(width, height, '#f8fafc', '#e2e8f0')
        draw = ImageDraw.Draw(content_image)

        draw.rectangle([0, 0, width, 100], fill='#1e3a5f')
        draw.text((margin, 30), section['title'], fill='white', font=header_font)

        if avatar:
            avatar_x = margin
            avatar_y = height - 400 - margin
            content_image.paste(avatar, (avatar_x, avatar_y), avatar if avatar.mode == 'RGBA' else None)

        y_offset = 130
        line_spacing = 12
        max_text_width = width - (2 * margin)

        if avatar:
            max_text_width = width - 400 - margin

        if figure_idx < len(figures) and idx > 0:
            try:
                fig_img = Image.open(figures[figure_idx])
                fig_width = 500
                fig_height = int(fig_img.height * (fig_width / fig_img.width))
                if fig_height > 300:
                    fig_height = 300
                    fig_width = int(fig_img.width * (fig_height / fig_img.height))

                fig_img = fig_img.resize((fig_width, fig_height), Image.Resampling.LANCZOS)
                fig_x = width - margin - fig_width
                fig_y = y_offset
                content_image.paste(fig_img, (fig_x, fig_y))

                draw.text((fig_x, fig_y + fig_height + 5), f"Figure {figure_idx + 1}",
                         fill='#475569', font=small_font)

                max_text_width = min(max_text_width, fig_x - margin - 40)
                figure_idx += 1
            except Exception as e:
                print(f"⚠️  Could not add figure: {e}")

        for para_idx, para in enumerate(paragraphs):
            wrapped_lines = wrap_text(para, body_font, max_text_width)
            para_height = len(wrapped_lines) * (26 + line_spacing)

            if y_offset + para_height > height - margin:
                content_slide_path = os.path.join(output_dir, f"slide_{len(slides):03d}_content.png")
                content_image.save(content_slide_path)
                slides.append(content_slide_path)
                slide_to_section.append(idx)

                content_image = create_gradient_background(width, height, '#f8fafc', '#e2e8f0')
                draw = ImageDraw.Draw(content_image)
                draw.rectangle([0, 0, width, 100], fill='#1e3a5f')
                draw.text((margin, 30), section['title'], fill='white', font=header_font)

                if avatar:
                    content_image.paste(avatar, (avatar_x, avatar_y), avatar if avatar.mode == 'RGBA' else None)

                y_offset = 130
                max_text_width = width - (2 * margin) if not avatar else width - 400 - margin

            for line_idx, line in enumerate(wrapped_lines):
                if line_idx == 0 and para_idx < 3:
                    try:
                        bbox = body_font.getbbox(line)
                        draw.rectangle([margin - 5, y_offset - 5,
                                      margin + bbox[2] - bbox[0] + 5,
                                      y_offset + 26 + 5],
                                     fill='#dbeafe', outline='#3b82f6', width=1)
                    except:
                        pass

                draw.text((margin, y_offset), line, fill='#1e293b', font=body_font)
                y_offset += 26 + line_spacing

            y_offset += line_spacing * 2

        content_slide_path = os.path.join(output_dir, f"slide_{len(slides):03d}_content.png")
        content_image.save(content_slide_path)
        slides.append(content_slide_path)
        slide_to_section.append(idx)

    return slides, slide_to_section

def create_video(slides, slide_to_section, section_audio_files, output_dir, output_file="output.mp4"):
    """Creates video with per-section audio sync."""
    output_path = os.path.join(output_dir, output_file)

    section_slides = {}
    for slide_idx, section_idx in enumerate(slide_to_section):
        if section_idx not in section_slides:
            section_slides[section_idx] = []
        section_slides[section_idx].append(slide_idx)

    print(f"   Total slides: {len(slides)}")
    print(f"   Total sections: {len(section_audio_files)}")

    clips = []
    audio_clips = []
    current_time = 0

    for section_idx, (audio_path, audio_duration) in enumerate(section_audio_files):
        if section_idx not in section_slides:
            continue

        section_slide_indices = section_slides[section_idx]
        num_slides = len(section_slide_indices)
        slide_duration = audio_duration / num_slides

        print(f"   Section {section_idx}: {num_slides} slides, {slide_duration:.1f}s each")

        for slide_idx in section_slide_indices:
            clip = ImageClip(slides[slide_idx], duration=slide_duration)
            clips.append(clip)

        audio_clip = AudioFileClip(audio_path).with_start(current_time)
        audio_clips.append(audio_clip)
        current_time += audio_duration

    video = concatenate_videoclips(clips, method="compose")
    final_audio = CompositeAudioClip(audio_clips)

    if video.duration < final_audio.duration:
        extension = final_audio.duration - video.duration
        last_clip = ImageClip(slides[-1], duration=clips[-1].duration + extension)
        clips[-1] = last_clip
        video = concatenate_videoclips(clips, method="compose")
    elif video.duration > final_audio.duration:
        video = video.subclipped(0, final_audio.duration)

    video = video.with_audio(final_audio)
    video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac',
                         threads=4, preset='medium')

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate multilingual academic paper videos.")
    parser.add_argument("--paper-location", required=True, help="PDF URL or path")
    parser.add_argument("--summarizer", default="ollama", choices=["gemini", "ollama", "manual"])
    parser.add_argument("--voice-engine", default="gtts", choices=["gtts", "coqui", "elevenlabs"])
    parser.add_argument("--voice-sample", default=None, help="Path to voice sample WAV")
    parser.add_argument("--avatar-image", default=None, help="Path to avatar image")
    parser.add_argument("--language", default="en", choices=["en", "ko", "ja", "zh"],
                       help="Output language (en=English, ko=Korean, ja=Japanese, zh=Chinese)")
    args = parser.parse_args()

    try:
        base_name = os.path.basename(args.paper_location).replace('.pdf', '')
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"{base_name}_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        print(f"✓ Created output directory: {output_dir}")

        if args.paper_location.startswith('http'):
            print("📥 Downloading paper...")
            pdf_content = download_paper(args.paper_location)
        else:
            print("📄 Reading local paper...")
            pdf_content = read_local_pdf(args.paper_location)

        print("📝 Extracting text...")
        paper_text = extract_text_from_pdf(pdf_content)
        print(f"   Extracted {len(paper_text)} characters")

        print("🖼️  Extracting figures...")
        figures = extract_images_from_pdf(pdf_content, output_dir, max_images=5)
        print(f"   Extracted {len(figures)} figures")

        print(f"🤖 Generating {args.language.upper()} summary using {args.summarizer}...")
        raw_summary = summarize_text(paper_text, method=args.summarizer, language=args.language)

        print("🧹 Cleaning and parsing...")
        cleaned_summary = clean_gemini_response(raw_summary)
        sections = parse_markdown_to_sections(cleaned_summary)
        print(f"   Parsed {len(sections)} sections")

        print(f"🎤 Generating {args.language.upper()} voiceover using {args.voice_engine}...")
        if args.voice_sample:
            print(f"   Voice sample: {args.voice_sample}")
        section_audio_files = text_to_speech_per_section(
            sections, output_dir,
            voice_engine=args.voice_engine,
            voice_sample=args.voice_sample,
            language=args.language
        )

        print(f"🎨 Creating {args.language.upper()} slides...")
        if args.avatar_image:
            print(f"   Avatar: {args.avatar_image}")
        slides, slide_to_section = create_slides_with_avatar(
            sections, output_dir,
            figures=figures,
            avatar_image=args.avatar_image,
            language=args.language
        )
        print(f"   Created {len(slides)} slides")

        print("🎬 Compiling video...")
        final_video_path = create_video(slides, slide_to_section, section_audio_files, output_dir)

        print("\n" + "="*80)
        print("✅ VIDEO GENERATION COMPLETE!")
        print("="*80)
        print(f"📹 Video: {final_video_path}")
        print(f"🗣️  Language: {args.language.upper()}")
        print(f"🎵 Voice engine: {args.voice_engine}")
        print(f"📊 Slides: {len(slides)}")
        print(f"🖼️  Figures: {len(figures)}")
        if args.avatar_image:
            print(f"👤 Avatar: {args.avatar_image}")
        print(f"📂 Directory: {output_dir}")
        print("="*80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
