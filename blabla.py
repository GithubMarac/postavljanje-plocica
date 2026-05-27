# =========================================================
# AI YOUTUBE ANIMATION GENERATOR
# =========================================================

# ---------------------------------------------------------
# 1. INSTALL DEPENDENCIES (self-contained)
# ---------------------------------------------------------
import subprocess, sys, os, importlib

def ensure(package):
    try:
        importlib.import_module(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", package])

# Core dependencies
for pkg in ["diffusers", "transformers", "accelerate", "safetensors",
            "moviepy", "imageio", "imageio_ffmpeg", "PIL", "numpy",
            "torch", "torchvision", "torchaudio"]:
    ensure(pkg)

# Voice dependency (try to install TTS – if it fails, video will be silent)
try:
    ensure("TTS")
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False
    print("Warning: TTS could not be installed. Video will have no voiceover.")

# ---------------------------------------------------------
# 2. IMPORTS
# ---------------------------------------------------------
import torch
import numpy as np
from PIL import Image
from diffusers import StableDiffusionXLPipeline
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
if TTS_AVAILABLE:
    from TTS.api import TTS

# ---------------------------------------------------------
# 3. GPU
# ---------------------------------------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
print("DEVICE:", device)

# ---------------------------------------------------------
# 4. LOAD IMAGE GENERATION MODEL (SDXL)
# ---------------------------------------------------------
model_id = "stabilityai/stable-diffusion-xl-base-1.0"
pipe = StableDiffusionXLPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    variant="fp16",
    use_safetensors=True
)
pipe.to(device)

# ---------------------------------------------------------
# 5. STORY SCENES
# ---------------------------------------------------------
scenes = [
    "cinematic drone shot over futuristic Tokyo at night, neon lights, realistic, 4k",
    "young cyberpunk warrior walking in rain, cinematic lighting, ultra realistic",
    "flying cars between giant skyscrapers, bladerunner style, movie quality",
    "massive futuristic city sunrise, epic atmosphere, volumetric lighting",
    "hero standing on rooftop overlooking neon city, dramatic cinematic scene"
]

# ---------------------------------------------------------
# 6. GENERATE IMAGES
# ---------------------------------------------------------
image_paths = []
os.makedirs("/kaggle/working/scenes", exist_ok=True)

for i, prompt in enumerate(scenes):
    print(f"Generating Scene {i+1}")
    image = pipe(
        prompt=prompt,
        num_inference_steps=30,
        guidance_scale=7.5,
        height=768,
        width=1344
    ).images[0]
    path = f"/kaggle/working/scenes/scene_{i}.png"
    image.save(path)
    image_paths.append(path)

# ---------------------------------------------------------
# 7. CREATE CINEMATIC MOTION (SLOW ZOOM)
# ---------------------------------------------------------
clips = []
duration_per_scene = 4  # seconds

for path in image_paths:
    clip = (
        ImageClip(path)
        .set_duration(duration_per_scene)
        .resize(height=720)
    )
    clip = clip.resize(lambda t: 1 + (0.08 * t / duration_per_scene))
    clips.append(clip)

video = concatenate_videoclips(clips, method="compose")

# ---------------------------------------------------------
# 8. NATURAL VOICEOVER (only if TTS is available)
# ---------------------------------------------------------
voice_path = "/kaggle/working/voice.wav"

if TTS_AVAILABLE:
    voice_text = """
    In the year 2099, humanity transformed the night into endless neon dreams.
    Gigantic cities floated above the clouds while machines ruled the streets below.
    One warrior would rise against the system.
    """
    try:
        print("Loading natural TTS model (VITS)...")
        tts = TTS(model_name="tts_models/en/ljspeech/vits", progress_bar=True)
        print("Generating voiceover...")
        tts.tts_to_file(text=voice_text, file_path=voice_path)
        print("Voice saved!")
        audio = AudioFileClip(voice_path)
        video = video.set_audio(audio)
    except Exception as e:
        print("Voice generation failed, video will be silent:", e)
else:
    print("TTS not available – exporting silent video.")

# ---------------------------------------------------------
# 9. EXPORT FINAL VIDEO
# ---------------------------------------------------------
output_path = "/kaggle/working/final_youtube_animation.mp4"
video.write_videofile(
    output_path,
    fps=24,
    codec="libx264",
    audio_codec="aac" if video.audio is not None else None
)

print("====================================")
print("DONE! Video saved to:", output_path)
print("====================================")

# ---------------------------------------------------------
# 10. DOWNLOAD LINK
# ---------------------------------------------------------
from IPython.display import FileLink
FileLink(output_path)