# 🎵 Beat Store Bot

A Telegram bot for posting beats with audio, image, and text to your channel. Color-coded tags for beat categorization.

## Features

- 🎵 Post audio + image + text in one message
- 🏷️ Color-coded tags (Yellow, Orange, Green, Red, Blue)
- 📊 Metadata: BPM, Key, Price
- 🔘 Interactive buttons: Preview, Buy, Contact, Share

## Setup

1. Get a bot token from [@BotFather](https://t.me/BotFather)
2. Create a channel and add the bot as admin
3. Run: `pip install python-telegram-bot && python beat_store_bot.py`

## Commands

| Command | Description |
|---------|-------------|
| `/newbeat` | Start upload wizard |
| `/confirm` | Post to channel |
| `/cancel` | Cancel upload |
| `/help` | Show guide |

## Color Tags

- 🟡 Yellow - Exclusive/Unreleased
- 🟠 Orange - New Beat
- 🟢 Green - Lease Available
- 🔴 Red - Hot/Sold
- 🔵 Blue - Custom Order

## Deploy to Render (Free)


1. Push to GitHub
2. Go to [render.com](https://render.com)
3. New → Web Service → Connect GitHub
4. Build: `pip install python-telegram-bot`
5. Start: `python beat_store_bot.py`
