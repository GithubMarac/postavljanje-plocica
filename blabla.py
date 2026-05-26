# =========================================================
# AI YOUTUBE ANIMATION GENERATOR (NATURAL VOICEOVER)
# =========================================================

# ---------------------------------------------------------
# INSTALL
# ---------------------------------------------------------
!pip install -q diffusers transformers accelerate safetensors
!pip install -q moviepy imageio imageio-ffmpeg pillow numpy
!pip install -q torch torchvision torchaudio
!pip install -q TTS   # Coqui TTS for natural, human-like voice

# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------
import os
import torch
import numpy as np
from PIL import Image
from diffusers import StableDiffusionXLPipeline   # direct – no HunyuanDiT
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
from TTS.api import TTS

# ---------------------------------------------------------
# GPU
# ---------------------------------------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
print("DEVICE:", device)

# ---------------------------------------------------------
# LOAD AI IMAGE MODEL (SDXL)
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
# STORY SCENES
# ---------------------------------------------------------
scenes = [
    "cinematic drone shot over futuristic Tokyo at night, neon lights, realistic, 4k",
    "young cyberpunk warrior walking in rain, cinematic lighting, ultra realistic",
    "flying cars between giant skyscrapers, bladerunner style, movie quality",
    "massive futuristic city sunrise, epic atmosphere, volumetric lighting",
    "hero standing on rooftop overlooking neon city, dramatic cinematic scene"
]

# ---------------------------------------------------------
# GENERATE IMAGES
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
# CREATE CINEMATIC MOTION (SLOW ZOOM)
# ---------------------------------------------------------
clips = []
duration_per_scene = 4  # seconds

for path in image_paths:
    clip = (
        ImageClip(path)
        .set_duration(duration_per_scene)
        .resize(height=720)
    )
    # Slow zoom effect (Ken Burns style)
    clip = clip.resize(lambda t: 1 + (0.08 * t / duration_per_scene))
    clips.append(clip)

# ---------------------------------------------------------
# COMBINE VIDEO
# ---------------------------------------------------------
video = concatenate_videoclips(clips, method="compose")

# ---------------------------------------------------------
# NATURAL VOICEOVER (Coqui TTS – VITS model)
# ---------------------------------------------------------
voice_text = """
October 1990
Blackwood, Pennsylvania

Rain hammered the empty highway like handfuls of nails.

At 11:47 PM, the neon sign outside the Blackwood Diner buzzed weakly in the storm. Half the letters were dead, so from the road it only read:

“LACK OOD DINER.”

Inside, waitress Nancy Cole wiped down the counter while an old jukebox played softly in the corner. The diner smelled of burnt coffee and cigarette smoke.

There were only three customers left.

A truck driver asleep in Booth 4.
A teenage couple arguing quietly near the window.
And a man in a gray coat sitting alone at the far end of the counter.

Nancy noticed him because he hadn’t touched his coffee once.

He just stared at the payphone outside.

Waiting.

At exactly midnight, the phone rang.

The sharp metallic sound sliced through the rain.

The man stood immediately.

Not startled. Prepared.

He walked outside, lifted the receiver, and listened.

Nancy watched through the window.

No talking.

Just listening.

Then the man slowly turned his head toward the diner.

Toward her.

Even through the storm, Nancy could feel it.

That look.

Cold. Empty.

Like he already knew something terrible was about to happen.

The man hung up the phone and walked back inside.

He sat down again and finally took a sip of coffee.

Nancy forced a smile.

“Everything okay, hon?”

The man looked at her for a moment before answering.

“She knows.”

Nancy frowned.

“Who knows what?”

But the man didn’t answer.

Instead, he pulled a folded photograph from his pocket and slid it across the counter.

Nancy looked down.

The photo showed a woman standing beside a lake.

On the back, written in black ink, were four words:

DON’T TRUST THE SHERIFF

Nancy’s stomach tightened.

Because she recognized the woman instantly.

Emily Voss.

Missing for eight years.

Blackwood’s most famous unsolved case.

Everyone in town knew the story.

Emily disappeared after leaving a party in the summer of 1982. Her car was found abandoned near Miller’s Lake, but no body was ever recovered.

The sheriff at the time claimed she had drowned.

Case closed.

But people whispered.

Small towns are factories for whispers.

Nancy looked back up at the man.

“Where did you get this?”

The man leaned closer.

“She called me tonight.”

Nancy blinked.

“What?”

Before he could answer, the diner door opened.

A gust of cold wind swept inside.

Sheriff Walter Briggs stepped through the doorway.

Tall. Heavy boots. Rain dripping from his hat.

The entire diner went quiet.

Sheriff Briggs spotted the man instantly.

And froze.

Just for half a second.

But Nancy saw it.

Recognition.

The sheriff walked slowly toward the counter.

“Well,” he said. “Didn’t expect to see you back in Blackwood.”

The man smiled faintly.

“Been a long time, Walter.”

Nancy looked between them.

“You two know each other?”

Neither answered.

The sheriff sat beside the man and removed his gloves carefully.

“You should’ve stayed gone,” he muttered.

The man chuckled softly.

“Funny. Emily said the same thing.”

The sheriff’s face changed instantly.

Not anger.

Fear.

Real fear.

Then everything happened at once.

The truck driver woke up suddenly.
The jukebox cut out.
Lightning flashed outside.

And the sheriff grabbed the man by the collar.

“You need to stop talking.”

The teenage couple hurried out of the diner.

Nancy stepped backward.

“What the hell is going on?”

The man calmly reached into his coat.

Sheriff Briggs drew his revolver instantly.

Nancy screamed.

But instead of a weapon…

…the man pulled out a cassette tape.

He placed it on the counter between them.

“Her voice is on there,” he said quietly.

The sheriff stared at the tape like it was alive.

“You buried her,” the man whispered.

Rain thundered against the windows.

Nancy could barely breathe.

Sheriff Briggs stood motionless for several seconds.

Then he said something nobody expected.

“She wasn’t supposed to die.”

Silence.

The entire diner seemed frozen in time.

The man nodded slowly, almost sadly.

“I know.”

Nancy’s heart pounded.

“What do you mean you KNOW?”

The man finally turned toward her.

“My name is Daniel Voss.”

Nancy’s eyes widened.

Emily’s brother.

The sheriff lowered his gun slightly.

Daniel pointed toward the cassette tape.

“She called me three nights ago.”

Nancy shook her head.

“That’s impossible.”

Daniel looked exhausted.

“Yeah,” he said softly. “That’s what I thought too.”

Sheriff Briggs suddenly lunged for the tape.

But Daniel moved faster.

The two men crashed into a table.

Coffee mugs shattered across the floor.

Nancy ran toward the kitchen phone to call for help.

Then—

BANG.

The gunshot exploded through the diner.

Everything stopped.

Nancy turned slowly.

Sheriff Briggs stood frozen beside the counter.

Blood spreading across his chest.

Daniel stared at him in shock.

The revolver lay smoking on the floor.

The sheriff collapsed.

Dead before he hit the ground.

Nancy looked at Daniel with terror.

“You killed him!”

But Daniel shook his head immediately.

“No…”

Then they heard it.

A voice.

Crackling softly from the cassette tape.

A woman’s voice.

Weak. Distorted.

“Danny… if you’re hearing this… he found me…”

Nancy felt ice crawl up her spine.

The tape continued.

“He kept me beneath the lake house… please…”

The recording suddenly cut into static.

Daniel’s face went pale.

Because the lake house had burned down in 1984.

Nancy whispered:

“Then who fired the gun?”

Neither of them answered.

Outside, lightning illuminated the parking lot.

For a split second, Nancy saw the silhouette of a woman standing beside the payphone in the rain.

Long dark hair.

White dress.

Watching the diner.

Then another flash of lightning came.

And she was gone.

Police never solved the murder of Sheriff Walter Briggs.

Daniel Voss disappeared the following morning.

And the cassette tape?

It vanished from evidence storage two days later.

But even now, locals in Blackwood still talk about stormy nights at the abandoned diner.

They say if the rain is loud enough…

…the payphone rings at exactly midnight. ☎️
"""

voice_path = "/kaggle/working/voice.wav"

try:
    print("Loading natural TTS model (VITS, English)...")
    tts = TTS(model_name="tts_models/en/ljspeech/vits", progress_bar=True)
    print("Generating voiceover...")
    tts.tts_to_file(text=voice_text, file_path=voice_path)
    print("Voice saved to", voice_path)

    # Attach audio to video
    audio = AudioFileClip(voice_path)
    video = video.set_audio(audio)
    print("Audio added to video.")
except Exception as e:
    print("Voice generation failed, video will be silent:", e)

# ---------------------------------------------------------
# EXPORT FINAL VIDEO
# ---------------------------------------------------------
output_path = "/kaggle/working/final_youtube_animation.mp4"

video.write_videofile(
    output_path,
    fps=24,
    codec="libx264",
    audio_codec="aac" if video.audio is not None else None
)

print("====================================")
print("DONE!")
print("VIDEO:", output_path)
print("====================================")

# ---------------------------------------------------------
# DOWNLOAD LINK
# ---------------------------------------------------------
from IPython.display import FileLink
FileLink(output_path)