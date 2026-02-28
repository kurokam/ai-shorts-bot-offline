import os
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from PIL import Image
import torch
from diffusers import StableDiffusionPipeline

# ---------------- STORY ---------------- #
def generate_story(topic, duration):
    """Offline placeholder: sadece topic ile basit cümleler döndürür."""
    return f"{topic} is amazing.\nHere's a fact about {topic}.\nDid you know {topic} has secrets?"

# ---------------- IMAGE ---------------- #
def generate_image(prompt, index, model_path):
    """Stable Diffusion ile görsel üretir."""
    pipe = StableDiffusionPipeline.from_pretrained(model_path, torch_dtype=torch.float16)
    pipe.to("cuda" if torch.cuda.is_available() else "cpu")

    image = pipe(prompt, guidance_scale=7.5).images[0]
    file_path = f"scenes/scene_{index}.png"
    os.makedirs("scenes", exist_ok=True)
    image.save(file_path)
    return file_path

# ---------------- VOICE ---------------- #
def generate_voice(text):
    tts = gTTS(text=text, lang="en")
    os.makedirs("videos", exist_ok=True)
    output_file = "videos/voice.mp3"
    tts.save(output_file)
    return output_file

# ---------------- VIDEO ---------------- #
def build_video(images, audio_file):
    audio = AudioFileClip(audio_file)
    duration_per_image = audio.duration / len(images)
    clips = [ImageClip(img).set_duration(duration_per_image) for img in images]
    video = concatenate_videoclips(clips, method="compose").set_audio(audio)
    output_file = "videos/final_video.mp4"
    video.write_videofile(output_file, fps=24)
    return output_file
