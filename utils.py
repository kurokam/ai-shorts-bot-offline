import os
import requests
import base64
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# ---------------- STORY ---------------- #
def generate_story(topic, duration=45):
    """Offline placeholder story generator."""
    return f"{topic} is amazing. Here's a fact about {topic}. Did you know {topic} has secrets?"

# ---------------- IMAGE (SD.Next API Entegrasyonu) ---------------- #
def generate_image(prompt, index, model_path=None):
    """SD.Next API üzerinden görüntü üretir."""
    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    
    # RX 6600 XT için optimize edilmiş ayarlar
    payload = {
        "prompt": prompt + ", high quality, cinematic, masterpiece",
        "negative_prompt": "lowres, bad anatomy, text, error, extra digit, cropped, worst quality, low quality",
        "steps": 25,
        "width": 720,  # Shorts formatı
        "height": 1280,
        "cfg_scale": 7,
        "sampler_name": "Euler a",
        "batch_size": 1
    }

    try:
        print(f"Sahne {index} üretiliyor: {prompt[:30]}...")
        response = requests.post(url, json=payload, timeout=300)
        
        if response.status_code == 200:
            r = response.json()
            os.makedirs("scenes", exist_ok=True)
            file_path = f"scenes/scene_{index}.png"
            
            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(r['images'][0]))
            return file_path
        else:
            print(f"API Hatası: {response.status_code}")
            return None
    except Exception as e:
        print(f"Bağlantı Hatası: SD.Next açık mı? {e}")
        return None

# ---------------- VOICE ---------------- #
def generate_voice(text):
    os.makedirs("videos", exist_ok=True)
    tts = gTTS(text=text, lang="en")
    output_file = "videos/voice.mp3"
    tts.save(output_file)
    return output_file

# ---------------- VIDEO ---------------- #
def build_video(images, audio_file):
    # None dönen resimleri listeden çıkar (hata kontrolü)
    valid_images = [img for img in images if img is not None]
    
    audio = AudioFileClip(audio_file)
    duration_per_image = audio.duration / len(valid_images)
    clips = [ImageClip(img).set_duration(duration_per_image) for img in valid_images]
    
    video = concatenate_videoclips(clips, method="compose").set_audio(audio)
    output_file = "videos/final_video.mp4"
    
    # AMD kartlarda hızlanması için libx264 kullanıyoruz
    video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")
    return output_file
