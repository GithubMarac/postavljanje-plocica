"""
╔══════════════════════════════════════════════════════════════╗
║         YouTube Shorts Creator — Kaggle Edition              ║
║  A-Roll + B-Roll + Natural Voiceover (non-robotic)           ║
║                                                              ║
║  Stack:                                                       ║
║   • edge-tts    → Natural Microsoft Neural TTS               ║
║   • ZeroScope v2 → AI B-roll video generation (HuggingFace)  ║
║   • MoviePy     → Video editing & assembly                   ║
║   • PIL         → Animated A-roll title cards                ║
║                                                              ║
║  Output: 1080×1920 portrait MP4 (YouTube Shorts ready)       ║
╚══════════════════════════════════════════════════════════════╝
"""

# ─────────────────────────────────────────────
# STEP 0 ▸ Install all dependencies
# ─────────────────────────────────────────────
import subprocess, sys

def pip(*pkgs):
    # No --upgrade: avoid breaking already-loaded Kaggle packages (e.g. torch)
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-q"] + list(pkgs)
    )

print("📦 Installing dependencies …")
pip("edge-tts", "nest_asyncio")          # nest_asyncio fixes Jupyter event loop
pip("moviepy==1.0.3", "imageio==2.31.6", "imageio-ffmpeg")
pip("diffusers>=0.25.0", "transformers", "accelerate", "safetensors")
# torch & torchvision are pre-installed on Kaggle GPU kernels — do NOT reinstall
# pip("torch", "torchvision")   ← would corrupt the running kernel
pip("Pillow", "numpy", "scipy", "tqdm")
print("✅ Dependencies installed\n")


# ─────────────────────────────────────────────
# STEP 1 ▸ USER CONFIGURATION  ← edit here
# ─────────────────────────────────────────────
import os, textwrap, asyncio, warnings
warnings.filterwarnings("ignore")

# ── Fix: Jupyter/Kaggle already runs an event loop ──────────
import nest_asyncio
nest_asyncio.apply()   # lets asyncio work inside Jupyter's running loop

# ── Topic & Script ──────────────────────────────────────────
TITLE = "5 Mind-Blowing Space Facts"

# Each segment = one chunk of the short.
# 'text'         → voiceover line (spoken aloud)
# 'b_roll_prompt'→ text-to-video prompt for B-roll clip
# 'a_roll_text'  → optional large overlay text on A-roll card
SEGMENTS = [
    {
        "text": "Space is completely silent. There is no air, so sound waves have nothing to travel through.",
        "b_roll_prompt": "deep outer space stars nebula milky way cinematic 4k slow motion",
        "a_roll_text": "🔇 Complete Silence",
    },
    {
        "text": "One million Earths could fit inside the Sun. It's almost unimaginably huge.",
        "b_roll_prompt": "the sun solar flares massive star cinematic slow motion close up",
        "a_roll_text": "☀️ 1 Million Earths",
    },
    {
        "text": "There are more stars in the universe than grains of sand on all of Earth's beaches combined.",
        "b_roll_prompt": "galaxy stars night sky timelapse beautiful cosmic cinematic",
        "a_roll_text": "⭐ Stars > Sand",
    },
    {
        "text": "A day on Venus is longer than a year on Venus. It rotates incredibly slowly.",
        "b_roll_prompt": "planet venus atmosphere orbit cinematic space telescope",
        "a_roll_text": "🪐 Day > Year",
    },
    {
        "text": "Neutron stars are so dense that a teaspoon of their material would weigh a billion tons on Earth.",
        "b_roll_prompt": "neutron star pulsar explosion supernova cinematic space",
        "a_roll_text": "💫 1 Teaspoon = 1B Tons",
    },
]

# ── Voice ────────────────────────────────────────────────────
# Great natural-sounding edge-tts voices (pick one):
#   en-US-JennyNeural      ← warm female, very natural
#   en-US-GuyNeural        ← confident male
#   en-US-AriaNeural       ← energetic female
#   en-GB-SoniaNeural      ← British female
#   en-AU-NatashaNeural    ← Australian female
VOICE = "en-US-AriaNeural"
VOICE_RATE = "+10%"    # speaking speed: -20% (slower) to +30% (faster)
VOICE_PITCH = "+0Hz"   # pitch shift

# ── Video Generation ─────────────────────────────────────────
# Options: "zeroscope"  → ZeroScope v2 (GPU needed, best quality)
#          "modelscope" → ModelScope text2video (lighter)
#          "skip"       → skip AI generation, use colour backgrounds
VIDEO_MODEL = "zeroscope"   # change to "skip" if VRAM is tight
VIDEO_STEPS  = 25           # inference steps (20-40 is fine)
VIDEO_FRAMES = 24           # frames per B-roll clip (keep ≤24 on Kaggle)
VIDEO_FPS    = 8            # fps for generated clips

# ── Output ───────────────────────────────────────────────────
OUT_DIR  = "/kaggle/working/shorts_output"
FINAL_MP4 = os.path.join(OUT_DIR, "youtube_short.mp4")
os.makedirs(OUT_DIR, exist_ok=True)

# ── A-roll style ─────────────────────────────────────────────
CANVAS_W, CANVAS_H = 1080, 1920          # 9:16
BG_COLORS   = [                          # gradient pairs per segment
    ("#0f0c29", "#302b63"),
    ("#1a1a2e", "#16213e"),
    ("#0d0d0d", "#1a0533"),
    ("#000428", "#004e92"),
    ("#09203f", "#537895"),
]
ACCENT_COLOR = "#FFD700"                 # gold accent


# ─────────────────────────────────────────────
# STEP 2 ▸ Generate voiceover with edge-tts
# ─────────────────────────────────────────────
print("🎙️  Generating voiceover …")
import edge_tts

async def tts(text: str, output_path: str):
    communicate = edge_tts.Communicate(
        text,
        VOICE,
        rate=VOICE_RATE,
        pitch=VOICE_PITCH,
    )
    await communicate.save(output_path)

def generate_voiceovers():
    paths = []
    for i, seg in enumerate(SEGMENTS):
        path = os.path.join(OUT_DIR, f"vo_{i:02d}.mp3")
        asyncio.run(tts(seg["text"], path))
        paths.append(path)
        print(f"  ✓ VO {i+1}/{len(SEGMENTS)}: {seg['text'][:50]}…")
    return paths

vo_paths = generate_voiceovers()
print("✅ Voiceover done\n")


# ─────────────────────────────────────────────
# STEP 3 ▸ Get audio durations
# ─────────────────────────────────────────────
from moviepy.editor import AudioFileClip

def get_duration(path):
    clip = AudioFileClip(path)
    dur = clip.duration
    clip.close()
    return dur

durations = [get_duration(p) for p in vo_paths]
print(f"📏 Segment durations: {[f'{d:.1f}s' for d in durations]}")
print(f"📏 Total runtime: {sum(durations):.1f}s\n")


# ─────────────────────────────────────────────
# STEP 4 ▸ Generate B-roll via ZeroScope / ModelScope
# ─────────────────────────────────────────────
import torch
import numpy as np
from PIL import Image

def generate_broll_zeroscope(prompt: str, output_path: str, n_frames: int, fps: int):
    """Generate a B-roll clip using ZeroScope v2 XL."""
    from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
    import imageio

    model_id = "cerspense/zeroscope_v2_576w"   # lighter version for Kaggle

    pipe = DiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
    )
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    pipe.enable_model_cpu_offload()
    pipe.enable_vae_slicing()

    with torch.autocast("cuda"):
        frames = pipe(
            prompt,
            num_inference_steps=VIDEO_STEPS,
            num_frames=n_frames,
            height=320,
            width=576,
        ).frames[0]   # list of PIL images

    # Resize each frame to fill 1080×1920 (crop centre)
    processed = []
    for frame in frames:
        # frame is a PIL Image (576×320)
        # Scale so height fills 1920, then centre-crop width to 1080
        scale = 1920 / 320
        new_w = int(576 * scale)   # ≈ 3456
        frame = frame.resize((new_w, 1920), Image.LANCZOS)
        left = (new_w - 1080) // 2
        frame = frame.crop((left, 0, left + 1080, 1920))
        processed.append(np.array(frame))

    imageio.mimwrite(output_path, processed, fps=fps, quality=8)
    del pipe
    torch.cuda.empty_cache()

def generate_broll_modelscope(prompt: str, output_path: str, n_frames: int, fps: int):
    """Lighter alternative: ModelScope text-to-video."""
    from diffusers import DiffusionPipeline
    import imageio

    pipe = DiffusionPipeline.from_pretrained(
        "damo-vilab/text-to-video-ms-1.7b",
        torch_dtype=torch.float16,
        variant="fp16",
    )
    pipe.enable_model_cpu_offload()

    frames = pipe(
        prompt,
        num_inference_steps=VIDEO_STEPS,
        num_frames=n_frames,
    ).frames[0]

    processed = []
    for frame in frames:
        frame = frame.resize((1080, 1920), Image.LANCZOS)
        processed.append(np.array(frame))

    imageio.mimwrite(output_path, processed, fps=fps, quality=8)
    del pipe
    torch.cuda.empty_cache()

def solid_broll(color: tuple, output_path: str, duration: float, fps: int = 24):
    """Fallback: animated gradient background when GPU generation is skipped."""
    import imageio
    frames = []
    total_frames = int(duration * fps)
    for t in range(total_frames):
        img = Image.new("RGB", (1080, 1920), color)
        # subtle vignette pulse
        draw_vignette(img)
        frames.append(np.array(img))
    imageio.mimwrite(output_path, frames, fps=fps, quality=8)

def draw_vignette(img: Image.Image):
    """Add a dark vignette overlay."""
    from PIL import ImageFilter
    vignette = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(vignette)
    for r in range(300, 0, -10):
        alpha = int(180 * (1 - r / 300))
        draw.ellipse(
            [540 - r * 4, 960 - r * 4, 540 + r * 4, 960 + r * 4],
            fill=(0, 0, 0, alpha),
        )
    img.paste(Image.new("RGB", img.size, (0,0,0)), mask=vignette.split()[3])

from PIL import ImageDraw

print("🎬 Generating B-roll clips …")
broll_paths = []

for i, (seg, dur) in enumerate(zip(SEGMENTS, durations)):
    path = os.path.join(OUT_DIR, f"broll_{i:02d}.mp4")


    try:
        if VIDEO_MODEL == "zeroscope":
            generate_broll_zeroscope(seg["b_roll_prompt"], path, VIDEO_FRAMES, VIDEO_FPS)
        elif VIDEO_MODEL == "modelscope":
            generate_broll_modelscope(seg["b_roll_prompt"], path, VIDEO_FRAMES, VIDEO_FPS)
        else:
            raise ValueError("skip")
        print(f"    ✓ AI generated")
    except Exception as e:
        print(f"    ⚠ AI gen failed ({e}), using animated background")
        hex_bg = BG_COLORS[i % len(BG_COLORS)][0].lstrip("#")
        rgb = tuple(int(hex_bg[j:j+2], 16) for j in (0, 2, 4))
        solid_broll(rgb, path, dur, fps=24)

    broll_paths.append(path)

print("✅ B-roll done\n")


# ─────────────────────────────────────────────
# STEP 5 ▸ Build animated A-roll title cards
# ─────────────────────────────────────────────
print("🖼️  Building A-roll title cards …")

try:
    from PIL import ImageFont
    # Try to get a nicer font; fall back to default
    FONT_BIG  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 96)
    FONT_MED  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 52)
    FONT_SM   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 38)
except Exception:
    FONT_BIG  = ImageFont.load_default()
    FONT_MED  = ImageFont.load_default()
    FONT_SM   = ImageFont.load_default()

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def make_gradient(w, h, top_color, bot_color):
    top = np.array(hex_to_rgb(top_color), dtype=np.float32)
    bot = np.array(hex_to_rgb(bot_color), dtype=np.float32)
    gradient = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        t = y / h
        gradient[y] = (top * (1 - t) + bot * t).astype(np.uint8)
    return Image.fromarray(gradient, "RGB")

def draw_wrapped_text(draw, text, font, x, y, max_w, fill, line_spacing=1.35):
    words = text.split()
    lines, line = [], []
    for w in words:
        test = " ".join(line + [w])
        bbox = font.getbbox(test)
        if bbox[2] - bbox[0] > max_w and line:
            lines.append(" ".join(line))
            line = [w]
        else:
            line.append(w)
    if line:
        lines.append(" ".join(line))

    bbox = font.getbbox("A")
    line_h = (bbox[3] - bbox[1]) * line_spacing
    total_h = line_h * len(lines)
    cur_y = y - total_h / 2

    for ln in lines:
        bbox = font.getbbox(ln)
        w = bbox[2] - bbox[0]
        draw.text((x - w / 2, cur_y), ln, font=font, fill=fill)
        cur_y += line_h

def make_aroll_frame(seg_idx: int, seg: dict, progress: float = 0.5) -> np.ndarray:
    """
    Create a single A-roll card frame.
    progress ∈ [0, 1] drives subtle animation (opacity/scale feel).
    """
    top_c, bot_c = BG_COLORS[seg_idx % len(BG_COLORS)]
    img = make_gradient(CANVAS_W, CANVAS_H, top_c, bot_c)
    draw = ImageDraw.Draw(img, "RGBA")

    # Decorative accent bar
    bar_alpha = int(200 * min(progress * 3, 1.0))
    draw.rectangle([(80, 900), (1000, 908)], fill=(*hex_to_rgb(ACCENT_COLOR), bar_alpha))

    # Segment number pill
    pill_y = 820
    draw.rounded_rectangle(
        [(80, pill_y - 28), (80 + 110, pill_y + 28)],
        radius=28,
        fill=(*hex_to_rgb(ACCENT_COLOR), 220),
    )
    num_text = f"{seg_idx + 1}/{len(SEGMENTS)}"
    draw.text((135, pill_y), num_text, font=FONT_SM, fill=(0, 0, 0, 255), anchor="mm")

    # Big overlay text
    overlay = seg.get("a_roll_text", "")
    if overlay:
        draw_wrapped_text(draw, overlay, FONT_BIG, CANVAS_W // 2, 960, CANVAS_W - 120,
                          fill=(255, 255, 255, 240))

    # Title at top
    draw_wrapped_text(draw, TITLE, FONT_SM, CANVAS_W // 2, 160, CANVAS_W - 80,
                      fill=(*hex_to_rgb(ACCENT_COLOR), 200))

    # Corner dots decoration
    for cx, cy in [(60, 60), (1020, 60), (60, 1860), (1020, 1860)]:
        draw.ellipse([(cx - 8, cy - 8), (cx + 8, cy + 8)], fill=(*hex_to_rgb(ACCENT_COLOR), 120))

    return np.array(img.convert("RGB"))

def create_aroll_video(seg_idx: int, seg: dict, duration: float, fps: int = 24) -> str:
    import imageio
    path = os.path.join(OUT_DIR, f"aroll_{seg_idx:02d}.mp4")
    total = int(duration * fps)
    frames = []
    for t in range(total):
        prog = t / max(total - 1, 1)
        frames.append(make_aroll_frame(seg_idx, seg, prog))
    imageio.mimwrite(path, frames, fps=fps, quality=9)
    return path

aroll_paths = []
for i, (seg, dur) in enumerate(zip(SEGMENTS, durations)):
    p = create_aroll_video(i, seg, dur)
    aroll_paths.append(p)
    print(f"  ✓ A-roll {i+1}/{len(SEGMENTS)}")
print("✅ A-roll done\n")


# ─────────────────────────────────────────────
# STEP 6 ▸ Add subtitles overlay onto B-roll
# ─────────────────────────────────────────────
print("💬 Adding subtitle overlays …")
from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip,
    concatenate_videoclips, TextClip
)
from moviepy.video.fx.all import fadeout, fadein

def word_chunks(text: str, chunk_size: int = 5):
    """Split text into groups of words for caption timing."""
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def add_subtitles(video_clip, text: str):
    """Overlay animated subtitle captions on a clip."""
    chunks = word_chunks(text, chunk_size=4)
    dur = video_clip.duration
    chunk_dur = dur / len(chunks)
    sub_clips = []

    for j, chunk in enumerate(chunks):
        try:
            txt = TextClip(
                chunk,
                fontsize=58,
                color="white",
                stroke_color="black",
                stroke_width=2.5,
                font="DejaVu-Sans-Bold",
                method="caption",
                size=(900, None),
                align="center",
            )
        except Exception:
            # minimal fallback
            txt = TextClip(chunk, fontsize=52, color="white", method="label")

        txt = (txt
               .set_start(j * chunk_dur)
               .set_duration(chunk_dur)
               .set_position(("center", 1500))
               .crossfadein(0.12)
               .crossfadeout(0.12))
        sub_clips.append(txt)

    return CompositeVideoClip([video_clip] + sub_clips)


# ─────────────────────────────────────────────
# STEP 7 ▸ Compose each segment (A-roll + B-roll + audio)
# ─────────────────────────────────────────────
print("🎞️  Composing segments …")

def compose_segment(i, seg, dur):
    """
    Combine A-roll + B-roll side-by-side in time or layered.
    Layout: B-roll fills background, A-roll text card overlaid top/bottom.
    """
    vo   = AudioFileClip(vo_paths[i])

    # --- B-roll (background) ---
    broll = VideoFileClip(broll_paths[i], audio=False).loop(duration=dur)

    # Ensure 1080×1920
    if broll.size != (1080, 1920):
        broll = broll.resize((1080, 1920))

    broll = broll.set_duration(dur).set_audio(vo)

    # Fade in/out
    broll = fadein(broll, 0.3)
    broll = fadeout(broll, 0.3)

    # --- A-roll card (overlay in lower third) ---
    aroll = VideoFileClip(aroll_paths[i], audio=False).loop(duration=dur)
    if aroll.size != (1080, 1920):
        aroll = aroll.resize((1080, 1920))

    # Blend A-roll as a semi-transparent overlay on top half
    aroll = aroll.set_opacity(0.0)   # start fully transparent
    # We use it only for the text info via ImageClip approach below

    # --- Overlay the A-roll title card in the TOP 700px zone ---
    aroll_top = (aroll
                 .crop(x1=0, y1=0, x2=1080, y2=700)
                 .set_position((0, 0))
                 .set_opacity(0.78))

    # --- Subtitles on bottom ---
    composed = CompositeVideoClip([broll, aroll_top])
    composed = add_subtitles(composed, seg["text"])
    composed = composed.set_duration(dur)

    return composed

seg_clips = []
for i, (seg, dur) in enumerate(zip(SEGMENTS, durations)):
    print(f"  Composing segment {i+1}/{len(SEGMENTS)} …")
    clip = compose_segment(i, seg, dur)
    seg_clips.append(clip)

print("✅ Segments composed\n")


# ─────────────────────────────────────────────
# STEP 8 ▸ Add intro card + outro CTA
# ─────────────────────────────────────────────
print("🎬 Building intro & outro …")

def make_intro(duration=2.5, fps=24):
    import imageio
    path = os.path.join(OUT_DIR, "intro.mp4")
    total = int(duration * fps)
    top_c, bot_c = "#0f0c29", "#302b63"
    frames = []
    for t in range(total):
        prog = t / max(total - 1, 1)
        img = make_gradient(CANVAS_W, CANVAS_H, top_c, bot_c)
        draw = ImageDraw.Draw(img)

        # Animated title reveal
        alpha = int(255 * min(prog * 2, 1.0))
        color = (255, 215, 0, alpha)

        draw_wrapped_text(draw, TITLE, FONT_BIG, CANVAS_W // 2, 900,
                          CANVAS_W - 100, fill=color)
        draw_wrapped_text(draw, "Watch to the end 👇", FONT_MED,
                          CANVAS_W // 2, 1060, CANVAS_W - 100,
                          fill=(255, 255, 255, alpha))
        frames.append(np.array(img.convert("RGB")))

    imageio.mimwrite(path, frames, fps=fps, quality=9)
    return VideoFileClip(path, audio=False).set_duration(duration)

def make_outro(duration=2.5, fps=24):
    import imageio
    path = os.path.join(OUT_DIR, "outro.mp4")
    total = int(duration * fps)
    top_c, bot_c = "#000000", "#1a0533"
    frames = []
    for t in range(total):
        img = make_gradient(CANVAS_W, CANVAS_H, top_c, bot_c)
        draw = ImageDraw.Draw(img)
        draw_wrapped_text(draw, "Follow for more! 🚀", FONT_BIG,
                          CANVAS_W // 2, 880, CANVAS_W - 100,
                          fill=(255, 215, 0, 255))
        draw_wrapped_text(draw, "Like & Subscribe 👍", FONT_MED,
                          CANVAS_W // 2, 1040, CANVAS_W - 100,
                          fill=(255, 255, 255, 200))
        frames.append(np.array(img.convert("RGB")))
    imageio.mimwrite(path, frames, fps=fps, quality=9)
    return VideoFileClip(path, audio=False).set_duration(duration)

intro_clip = make_intro()
outro_clip = make_outro()
print("✅ Intro & outro done\n")


# ─────────────────────────────────────────────
# STEP 9 ▸ Final assembly & export
# ─────────────────────────────────────────────
print("🔧 Assembling final video …")

all_clips = [intro_clip] + seg_clips + [outro_clip]

# Ensure consistent size
all_clips = [c.resize((1080, 1920)) for c in all_clips]

final = concatenate_videoclips(all_clips, method="compose")

total_dur = final.duration
print(f"  Total duration: {total_dur:.1f}s")
if total_dur > 60:
    print(f"  ⚠ Warning: {total_dur:.0f}s > 60s. YouTube Shorts limit is 60s.")
    print("    ↳ Reduce number of SEGMENTS or shorten VOICE_RATE.")

print(f"  Writing → {FINAL_MP4}")
final.write_videofile(
    FINAL_MP4,
    fps=24,
    codec="libx264",
    audio_codec="aac",
    bitrate="8000k",
    audio_bitrate="192k",
    preset="fast",
    ffmpeg_params=["-crf", "18", "-movflags", "+faststart"],
    threads=4,
    logger=None,
)

print(f"\n✅ Done! Your YouTube Short is ready:")
print(f"   {FINAL_MP4}")
print(f"   Duration : {total_dur:.1f}s")
print(f"   Size     : {os.path.getsize(FINAL_MP4) / 1_000_000:.1f} MB")
print(f"   Format   : 1080×1920 MP4 (9:16 — YouTube Shorts native)")
print()
print("📤 Download from Kaggle → Output tab → youtube_short.mp4")


# ─────────────────────────────────────────────
# STEP 10 ▸ Cleanup temp files (optional)
# ─────────────────────────────────────────────
def cleanup():
    import glob
    temp_patterns = ["vo_*.mp3", "broll_*.mp4", "aroll_*.mp4", "intro.mp4", "outro.mp4"]
    for pat in temp_patterns:
        for f in glob.glob(os.path.join(OUT_DIR, pat)):
            os.remove(f)
    print("🧹 Temp files cleaned up")

# Uncomment to clean up intermediate files:
# cleanup()