import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from utils import generate_story, generate_image, generate_voice, build_video

BOT_TOKEN = os.getenv("BOT_TOKEN")
MODEL_PATH = os.getenv("MODEL_PATH")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Offline AI Shorts Bot Ready!\nUse /topic <topic>"
    )

async def set_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Enter a topic like: /topic space")
        return

    topic = " ".join(context.args)
    await update.message.reply_text("🧠 Generating story...")

    story = generate_story(topic)
    scenes = story.split("\n")

    await update.message.reply_text("🎨 Generating images...")
    images = [generate_image(scene, i, MODEL_PATH) for i, scene in enumerate(scenes)]

    await update.message.reply_text("🎙 Generating voice...")
    voice = generate_voice(story)

    await update.message.reply_text("🎬 Building video...")
    video = build_video(images, voice)

    await update.message.reply_text(f"✅ Video ready: {video}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("topic", set_topic))
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
