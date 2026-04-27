#!/usr/bin/env python3
"""
🎵 BEAT STORE BOT
Post audio + image + text in one click with color-coded tags
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaAudio
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ConversationHandler, filters, ContextTypes
)

# ============== CONFIG ==============
BOT_TOKEN = "8687982861:AAF-MXgTofOut9Zr10jHOg9wHVCAsqVieZ4"
CHANNEL_ID = "@prod.venus"
ADMIN_ID = 8482805774

# Color tags
COLOR_TAGS = {
    "🟡": "Yellow - Exclusive/Unreleased",
    "🟠": "Orange - New Beat",
    "🟢": "Green - Lease Available",
    "🔴": "Red - Hot/Sold",
    "🔵": "Blue - Custom Order"
}

# States for conversation
TITLE, AUDIO, IMAGE, BPM, KEY, PRICE, COLOR, CONFIRM = range(8)

# ============== LOGGING ==============
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ============== HELPERS ==============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message"""
    await update.message.reply_text(
        "🎵 *BEAT STORE BOT*\n\n"
        "Commands:\n"
        "/newbeat - Upload a new beat\n"
        "/help - Show all commands\n\n"
        "Quick upload guide:\n"
        "1. /newbeat\n"
        "2. Enter title\n"
        "3. Send audio file\n"
        "4. Send cover art\n"
        "5. Add metadata\n"
        "6. Confirm & post!",
        parse_mode="Markdown"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        "📖 *HELP GUIDE*\n\n"
        "*Uploading a Beat:*\n"
        "1. /newbeat - Start upload wizard\n"
        "2. Follow the prompts\n"
        "3. Bot posts to @prod.venus automatically\n\n"
        "*Color Tags:*\n"
        "🟡 Yellow - Exclusive\n"
        "🟠 Orange - New\n"
        "🟢 Green - Lease\n"
        "🔴 Red - Hot/Sold\n"
        "🔵 Blue - Custom\n\n"
        "*Other Commands:*\n"
        "/cancel - Cancel current upload",
        parse_mode="Markdown"
    )

async def newbeat_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the beat upload wizard"""
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Only the admin can upload beats.")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "🎵 *NEW BEAT UPLOAD*\n\n"
        "Enter the beat title:",
        parse_mode="Markdown"
    )
    return TITLE

async def title_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store the beat title"""
    context.user_data["title"] = update.message.text
    await update.message.reply_text("📎 Send the audio file (MP3 or WAV):")
    return AUDIO

async def audio_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store the audio file"""
    if not update.message.audio and not update.message.voice and not (update.message.document and update.message.document.mime_type.startswith('audio/')):
        await update.message.reply_text("❌ Please send an audio file.")
        return AUDIO
    
    if update.message.audio:
        file = await update.message.audio.get_file()
        context.user_data["audio_id"] = update.message.audio.file_id
    elif update.message.voice:
        file = await update.message.voice.get_file()
        context.user_data["audio_id"] = update.message.voice.file_id
    else:
        file = await update.message.document.get_file()
        context.user_data["audio_id"] = update.message.document.file_id
    
    audio_path = f"temp_audio_{update.message.from_user.id}.mp3"
    await file.download_to_drive(audio_path)
    context.user_data["audio_path"] = audio_path
    
    await update.message.reply_text("🖼 Send the cover art image:")
    return IMAGE

async def image_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store the cover art"""
    if not update.message.photo:
        await update.message.reply_text("❌ Please send a photo.")
        return IMAGE
    
    context.user_data["image_id"] = update.message.photo[-1].file_id
    await update.message.reply_text(
        "🔢 Enter BPM (beats per minute):\n"
        "Example: 140"
    )
    return BPM

async def bpm_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store BPM"""
    try:
        bpm = int(update.message.text)
        if bpm < 60 or bpm > 200:
            await update.message.reply_text("❌ BPM must be between 60-200. Try again:")
            return BPM
        context.user_data["bpm"] = bpm
    except ValueError:
        await update.message.reply_text("❌ Please enter a number. Try again:")
        return BPM
    
    await update.message.reply_text(
        "🎹 Enter the musical key:\n"
        "Example: Am, C#, Fm"
    )
    return KEY

async def key_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store musical key"""
    context.user_data["key"] = update.message.text.upper()
    await update.message.reply_text(
        "💰 Enter the price:\n"
        "Example: $30 or $50"
    )
    return PRICE

async def price_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store price"""
    context.user_data["price"] = update.message.text
    await update.message.reply_text(
        "🏷️ Choose a color tag:\n\n"
        "🟡 Yellow - Exclusive/Unreleased\n"
        "🟠 Orange - New Beat\n"
        "🟢 Green - Lease Available\n"
        "🔴 Red - Hot/Sold\n"
        "🔵 Blue - Custom Order\n\n"
        "Reply with: 🟡 or 🟠 or 🟢 or 🔴 or 🔵"
    )
    return COLOR

async def color_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store color tag"""
    emoji = update.message.text.strip()
    if emoji not in COLOR_TAGS:
        await update.message.reply_text("❌ Invalid color. Use: 🟡 🟠 🟢 🔴 🔵")
        return COLOR
    
    context.user_data["color"] = emoji
    
    title = context.user_data["title"]
    bpm = context.user_data["bpm"]
    key = context.user_data["key"]
    price = context.user_data["price"]
    color = context.user_data["color"]
    
    preview_text = (
        f"📦 *BEAT PREVIEW*\n\n"
        f"*{title}*\n"
        f"{color} {COLOR_TAGS[color]}\n\n"
        f"🎛 BPM: {bpm}\n"
        f"🎹 Key: {key}\n"
        f"💰 Price: {price}\n\n"
        f"Send /confirm to post to channel\n"
        f"Send /cancel to abort"
    )
    await update.message.reply_text(preview_text, parse_mode="Markdown")
    return CONFIRM

async def confirm_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Post the beat to the channel"""
    try:
        title = context.user_data["title"]
        bpm = context.user_data["bpm"]
        key = context.user_data["key"]
        price = context.user_data["price"]
        color = context.user_data["color"]
        audio_id = context.user_data["audio_id"]
        image_id = context.user_data["image_id"]
        
        caption = (
            f"*{title}*\n"
            f"{color} {COLOR_TAGS[color]}\n\n"
            f"🎛 BPM: {bpm} | 🎹 Key: {key}\n"
            f"💰 {price}"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("🎵 Preview", callback_data="preview"),
                InlineKeyboardButton("🛒 Buy Now", callback_data="buy"),
            ],
            [
                InlineKeyboardButton("📩 Contact", callback_data="contact"),
                InlineKeyboardButton("📤 Share", callback_data="share"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_media_group(
            chat_id=CHANNEL_ID,
            media=[
                InputMediaPhoto(media=image_id, caption=caption, parse_mode="Markdown"),
                InputMediaAudio(media=audio_id)
            ]
        )
        
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text="⬆️ Tap below to interact:",
            reply_markup=reply_markup
        )
        
        await update.message.reply_text("✅ Beat posted to @prod.venus!")
        
    except Exception as e:
        logger.error(f"Error posting beat: {e}")
        await update.message.reply_text(f"❌ Error: {e}")
    
    cleanup(context)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the upload"""
    cleanup(context)
    await update.message.reply_text("❌ Upload cancelled.")
    return ConversationHandler.END

def cleanup(context: ContextTypes.DEFAULT_TYPE):
    """Clean up temp files"""
    audio_path = context.user_data.get("audio_path")
    if audio_path and os.path.exists(audio_path):
        os.remove(audio_path)
    context.user_data.clear()

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")

# ============== MAIN ==============
def main():
    """Run the bot"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CommandHandler("confirm", confirm_post))
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("newbeat", newbeat_start)],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, title_received)],
            AUDIO: [MessageHandler(filters.AUDIO | filters.VOICE | filters.Document.AUDIO, audio_received)],
            IMAGE: [MessageHandler(filters.PHOTO, image_received)],
            BPM: [MessageHandler(filters.TEXT & ~filters.COMMAND, bpm_received)],
            KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, key_received)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, price_received)],
            COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, color_received)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_post)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)
    
    application.add_error_handler(error_handler)
    
    print("🎵 Beat Store Bot is running...")
    print("Channel: @prod.venus")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
