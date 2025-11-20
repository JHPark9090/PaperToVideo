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

# Gemini API Key (OPTIONAL - only needed if using --summarizer=gemini)
GEMINI_API_KEY = None  # Set this if you want to use Gemini: "your_api_key_here"

# Configure ElevenLabs (optional - for custom voices)
ELEVENLABS_API_KEY = None  # Set this if you have ElevenLabs account

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

def summarize_with_ollama(text, model="llama3.2"):
    """Summarizes text using local Ollama LLM."""
    prompt = f"""Summarize the following academic paper into key sections for a short video presentation.

Use this EXACT format with markdown headers (##):

## Title
[Paper title]

## Abstract
[2-3 sentences with proper punctuation]

## Introduction
[3-4 complete sentences explaining the problem and motivation]

## Methods
[4-5 sentences describing the approach]

## Results
[3-4 sentences highlighting main findings]

## Conclusion
[2-3 sentences on key takeaways and impact]

IMPORTANT: Use complete sentences with proper punctuation. Do NOT include any preamble. Start directly with "## Title".

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

def summarize_with_gemini(text, model="gemini-1.5-flash"):
    """Summarizes text using Gemini API."""
    if not GEMINI_API_KEY:
        raise Exception("Gemini API key not set. Either:\n"
                       "1. Set GEMINI_API_KEY in the script, or\n"
                       "2. Use --summarizer=ollama (free, local)")

    # Import and configure Gemini only when needed
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
    except ImportError:
        raise Exception("google-generativeai not installed. Install: pip install google-generativeai\n"
                       "Or use --summarizer=ollama (no installation needed)")

    prompt = f"""Summarize the following academic paper into key sections for a short video presentation.

Use this EXACT format with markdown headers (##):

## Title
[Paper title]

## Abstract
[2-3 sentences]

## Introduction
[3-4 sentences]

## Methods
[4-5 sentences]

## Results
[3-4 sentences]

## Conclusion
[2-3 sentences]

IMPORTANT: Use complete sentences. Do NOT include preamble. Start with "## Title".

Paper text:
---
{text[:15000]}"""

    gemini_model = genai.GenerativeModel(model)
    response = gemini_model.generate_content(prompt)
    return response.text

def summarize_text(text, method="ollama"):
    """Summarizes text using specified method."""
    if method == "ollama":
        print("   Using Ollama (local LLM)...")
        return summarize_with_ollama(text)
    elif method == "gemini":
        print("   Using Gemini API...")
        return summarize_with_gemini(text)
    elif method == "manual":
        print("   Using manual summary...")
        if os.path.exists("summary.txt"):
            with open("summary.txt", "r") as f:
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
            skip_patterns = ['of course', 'here is', 'here\'s', 'i\'ll provide',
                           'let me', 'i can', 'certainly', 'sure', 'formatted into']
            if any(pattern in line_lower for pattern in skip_patterns) and len(line_lower) < 100:
                continue
            started = True
        cleaned_lines.append(line)

    return '\n'.join(cleaned_lines).strip()

def parse_markdown_to_sections(text):
    """Parses markdown into sections."""
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
    """Cleans text for TTS."""
    text = re.sub(r'#{1,6}\s+', '', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'([a-z])\n([A-Z])', r'\1. \2', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n\s*\n', '. ', text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\.\.+', '.', text)
    return text.strip()

def text_to_speech_coqui(text, output_path, speaker_wav=None, language="en"):
    """
    Generate speech using Coqui TTS (supports voice cloning).

    Args:
        text: Text to synthesize
        output_path: Where to save MP3
        speaker_wav: Path to voice sample (for cloning)
        language: Language code
    """
    try:
        from TTS.api import TTS

        # Initialize TTS with multilingual model
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)

        if speaker_wav and os.path.exists(speaker_wav):
            # Voice cloning mode
            print(f"      Cloning voice from: {speaker_wav}")
            tts.tts_to_file(
                text=text,
                file_path=output_path,
                speaker_wav=speaker_wav,
                language=language
            )
        else:
            # Default voice
            tts.tts_to_file(
                text=text,
                file_path=output_path,
                language=language
            )

        return True
    except ImportError:
        print("      ⚠️  Coqui TTS not installed. Install: pip install TTS")
        return False
    except Exception as e:
        print(f"      ⚠️  Coqui TTS failed: {e}")
        return False

def text_to_speech_elevenlabs(text, output_path, voice_id="EXAVITQu4vr4xnSDxMaL"):
    """
    Generate speech using ElevenLabs API (premium quality, custom voices).

    Args:
        text: Text to synthesize
        output_path: Where to save MP3
        voice_id: ElevenLabs voice ID
    """
    if not ELEVENLABS_API_KEY:
        print("      ⚠️  ElevenLabs API key not set")
        return False

    try:
        import requests

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

def text_to_speech_per_section(sections, output_dir, voice_engine="gtts", voice_sample=None):
    """
    Generates separate audio file for each section.

    Args:
        sections: List of section dicts
        output_dir: Output directory
        voice_engine: "gtts", "coqui", or "elevenlabs"
        voice_sample: Path to voice sample WAV (for Coqui cloning)

    Returns:
        List of (audio_path, duration) tuples
    """
    audio_files = []

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
            success = text_to_speech_coqui(clean_text, audio_path, speaker_wav=voice_sample)

        elif voice_engine == "elevenlabs":
            print(f"   Section {idx} ({section['title']}): Using ElevenLabs...")
            success = text_to_speech_elevenlabs(clean_text, audio_path)

        # Fallback to gTTS if others fail
        if not success or voice_engine == "gtts":
            if voice_engine != "gtts":
                print(f"      Falling back to gTTS...")
            tts = gTTS(text=clean_text, lang='en', slow=False, tld='com')
            tts.save(audio_path)

        # Get duration
        audio = AudioSegment.from_mp3(audio_path)
        duration = len(audio) / 1000.0

        audio_files.append((audio_path, duration))
        print(f"      Duration: {duration:.1f}s")

    return audio_files

def wrap_text(text, font, max_width):
    """Wraps text to fit within max_width."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = font.getbbox(test_line)
        width = bbox[2] - bbox[0]

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

def create_slides_with_avatar(sections, output_dir, figures=None, avatar_image=None):
    """
    Creates slides with optional avatar image (KPOP/Elsa/etc).

    Args:
        sections: List of section dicts
        output_dir: Output directory
        figures: List of figure paths
        avatar_image: Path to avatar image (e.g., Elsa, KPOP idol)

    Returns:
        (slides, slide_to_section)
    """
    slides = []
    slide_to_section = []
    figures = figures or []
    figure_idx = 0

    # Load avatar if provided
    avatar = None
    if avatar_image and os.path.exists(avatar_image):
        try:
            avatar = Image.open(avatar_image)
            # Resize avatar to 300x400
            avatar = avatar.resize((300, 400), Image.Resampling.LANCZOS)
            print(f"   Using avatar: {avatar_image}")
        except Exception as e:
            print(f"   ⚠️  Could not load avatar: {e}")

    # Fonts
    title_font = ImageFont.truetype("DejaVuSans.ttf", 52)
    header_font = ImageFont.truetype("DejaVuSans.ttf", 38)
    body_font = ImageFont.truetype("DejaVuSans.ttf", 26)
    small_font = ImageFont.truetype("DejaVuSans.ttf", 20)

    width, height = 1280, 720
    margin = 60

    for idx, section in enumerate(sections):
        # Title slide
        title_image = create_gradient_background(width, height, '#1e3a5f', '#2c5282')
        draw = ImageDraw.Draw(title_image)

        # Add avatar on title slide if available
        if avatar:
            avatar_x = 50
            avatar_y = (height - 400) // 2
            title_image.paste(avatar, (avatar_x, avatar_y), avatar if avatar.mode == 'RGBA' else None)

        # Draw title (shifted right if avatar present)
        title_text = section['title']
        title_bbox = title_font.getbbox(title_text)
        title_width = title_bbox[2] - title_bbox[0]
        title_height = title_bbox[3] - title_bbox[1]

        if avatar:
            title_x = 400
            title_y = (height - title_height) // 2
        else:
            title_x = (width - title_width) // 2
            title_y = (height - title_height) // 2

        draw.text((title_x + 3, title_y + 3), title_text, fill='#00000080', font=title_font)
        draw.text((title_x, title_y), title_text, fill='white', font=title_font)

        # Decorative line
        line_width = min(400, title_width)
        line_x = title_x
        line_y = title_y + title_height + 30
        draw.rectangle([line_x, line_y, line_x + line_width, line_y + 4], fill='#60a5fa')

        title_slide_path = os.path.join(output_dir, f"slide_{len(slides):03d}_title.png")
        title_image.save(title_slide_path)
        slides.append(title_slide_path)
        slide_to_section.append(idx)

        # Content slide(s)
        content = section['content']
        if not content:
            continue

        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]

        content_image = create_gradient_background(width, height, '#f8fafc', '#e2e8f0')
        draw = ImageDraw.Draw(content_image)

        # Header bar
        draw.rectangle([0, 0, width, 100], fill='#1e3a5f')
        draw.text((margin, 30), section['title'], fill='white', font=header_font)

        # Add avatar on content slides (bottom left)
        if avatar:
            avatar_x = margin
            avatar_y = height - 400 - margin
            content_image.paste(avatar, (avatar_x, avatar_y), avatar if avatar.mode == 'RGBA' else None)

        y_offset = 130
        line_spacing = 12
        max_text_width = width - (2 * margin)

        # Adjust text width if avatar present
        if avatar:
            max_text_width = width - 400 - margin

        # Add figure if available
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
            para_height = len(wrapped_lines) * (body_font.size + line_spacing)

            if y_offset + para_height > height - margin:
                # Save and start new slide
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

            # Highlight first line
            for line_idx, line in enumerate(wrapped_lines):
                if line_idx == 0 and para_idx < 3:
                    bbox = body_font.getbbox(line)
                    draw.rectangle([margin - 5, y_offset - 5,
                                  margin + bbox[2] - bbox[0] + 5,
                                  y_offset + body_font.size + 5],
                                 fill='#dbeafe', outline='#3b82f6', width=1)

                draw.text((margin, y_offset), line, fill='#1e293b', font=body_font)
                y_offset += body_font.size + line_spacing

            y_offset += line_spacing * 2

        # Save final content slide
        content_slide_path = os.path.join(output_dir, f"slide_{len(slides):03d}_content.png")
        content_image.save(content_slide_path)
        slides.append(content_slide_path)
        slide_to_section.append(idx)

    return slides, slide_to_section

def create_video(slides, slide_to_section, section_audio_files, output_dir, output_file="output.mp4"):
    """Creates video with per-section audio sync."""
    output_path = os.path.join(output_dir, output_file)

    # Group slides by section
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
    parser = argparse.ArgumentParser(description="Generate academic paper video with custom voices.")
    parser.add_argument("--paper-location", required=True, help="PDF URL or path")
    parser.add_argument("--summarizer", default="ollama", choices=["gemini", "ollama", "manual"])
    parser.add_argument("--voice-engine", default="gtts", choices=["gtts", "coqui", "elevenlabs"],
                       help="Voice synthesis engine")
    parser.add_argument("--voice-sample", default=None,
                       help="Path to voice sample WAV for cloning (Coqui)")
    parser.add_argument("--avatar-image", default=None,
                       help="Path to avatar image (e.g., Elsa, KPOP idol)")
    args = parser.parse_args()

    try:
        # Setup
        base_name = os.path.basename(args.paper_location).replace('.pdf', '')
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"{base_name}_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        print(f"✓ Created output directory: {output_dir}")

        # Read paper
        if args.paper_location.startswith('http'):
            print("📥 Downloading paper...")
            pdf_content = download_paper(args.paper_location)
        else:
            print("📄 Reading local paper...")
            pdf_content = read_local_pdf(args.paper_location)

        # Extract
        print("📝 Extracting text...")
        paper_text = extract_text_from_pdf(pdf_content)
        print(f"   Extracted {len(paper_text)} characters")

        print("🖼️  Extracting figures...")
        figures = extract_images_from_pdf(pdf_content, output_dir, max_images=5)
        print(f"   Extracted {len(figures)} figures")

        # Summarize
        print(f"🤖 Generating summary using {args.summarizer}...")
        raw_summary = summarize_text(paper_text, method=args.summarizer)

        print("🧹 Cleaning and parsing...")
        cleaned_summary = clean_gemini_response(raw_summary)
        sections = parse_markdown_to_sections(cleaned_summary)
        print(f"   Parsed {len(sections)} sections")

        # Generate voice
        print(f"🎤 Generating voiceover using {args.voice_engine}...")
        if args.voice_sample:
            print(f"   Voice sample: {args.voice_sample}")
        section_audio_files = text_to_speech_per_section(
            sections, output_dir,
            voice_engine=args.voice_engine,
            voice_sample=args.voice_sample
        )

        # Create slides
        print("🎨 Creating slides...")
        if args.avatar_image:
            print(f"   Avatar: {args.avatar_image}")
        slides, slide_to_section = create_slides_with_avatar(
            sections, output_dir,
            figures=figures,
            avatar_image=args.avatar_image
        )
        print(f"   Created {len(slides)} slides")

        # Compile
        print("🎬 Compiling video...")
        final_video_path = create_video(slides, slide_to_section, section_audio_files, output_dir)

        print("\n" + "="*80)
        print("✅ VIDEO GENERATION COMPLETE!")
        print("="*80)
        print(f"📹 Video: {final_video_path}")
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
