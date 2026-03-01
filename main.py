import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from utils import generate_story, generate_image, generate_voice, build_video

# .env kullanıyorsan bunları yüklemeyi unutma (pip install python-dotenv)
# from dotenv import load_dotenv
# load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
# MODEL_PATH artık SD.Next API kullandığımız için gereksiz ama hata vermemesi için tutuyoruz
MODEL_PATH = os.getenv("MODEL_PATH")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Offline AI Shorts Bot Hazır!\nKullanım: /topic <konu>"
    )

async def set_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Bir konu girin: /topic uzay")
        return

    topic = " ".join(context.args)
    status_msg = await update.message.reply_text("🧠 Hikaye oluşturuluyor...")

    # 1. Hikaye Oluşturma
    story = generate_story(topic)
    scenes = [s for s in story.split(".") if len(s) > 5] # Boş sahneleri engelle

    # 2. Resim Oluşturma (Sırayla ve VRAM dostu)
    await status_msg.edit_text(f"🎨 {len(scenes)} adet görsel üretiliyor (AMD RX 6600 XT)...")
    images = []
    for i, scene in enumerate(scenes):
        # run_in_executor: Uzun süren işlemi botu dondurmadan arka planda yapar
        loop = asyncio.get_event_loop()
        img_path = await loop.run_in_executor(None, generate_image, scene, i, MODEL_PATH)
        if img_path:
            images.append(img_path)
        # Ekran kartının soğuması için çok kısa bir mola
        await asyncio.sleep(1)

    # 3. Ses Oluşturma
    await status_msg.edit_text("🎙 Seslendirme hazırlanıyor...")
    voice = generate_voice(story)

    # 4. Video Birleştirme
    await status_msg.edit_text("🎬 Video montajlanıyor (FFmpeg)...")
    loop = asyncio.get_event_loop()
    video_path = await loop.run_in_executor(None, build_video, images, voice)

    # 5. Gönderim
    await status_msg.edit_text("✅ Video hazır! Gönderiliyor...")
    with open(video_path, 'rb') as video_file:
        await update.message.reply_video(video=video_file, caption=f"🎬 Konu: {topic}")

def main():
    if not BOT_TOKEN:
        print("HATA: BOT_TOKEN bulunamadı! .env dosyasını kontrol et.")
        return
        
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("topic", set_topic))
    
    print("🚀 Bot çalışıyor... SD.Next API bağlantısı bekleniyor.")
    app.run_polling()

if __name__ == "__main__":
    main()
