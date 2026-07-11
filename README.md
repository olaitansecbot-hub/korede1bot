# @korede1bot

Telegram Bot with Word Counter, Plagiarism Checker, URL Shortener, Image Converter, and Image Generator.

## Features

- 📝 Word Counter
- 🔍 Plagiarism Checker
- 🔗 URL Shortener
- 🖼️ Image Converter
- 🎨 Image Generator

## Commands

| Command | Description |
|---------|-------------|
| /start | Welcome message |
| /help | Show all commands |
| /wordcounter [text] | Count words & characters |
| /plagiarism [text] | Check for plagiarism |
| /shorten [url] | Shorten a URL |
| /convert [format] | Convert image (reply to image) |
| /generate [prompt] | Generate image from text |
| /analyze [text] | Full text analysis |
| /time | Current time |
| /about | About this bot |

## Deployment

Deployed on Railway with GitHub integration.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| BOT_TOKEN | ✅ Yes | Your bot token from @BotFather |
| TELEGRAM_BOT_TOKEN | ✅ Yes | Same as above (either works) |
| GOOGLE_API_KEY | ❌ No | For better plagiarism check |
| GOOGLE_CSE_ID | ❌ No | For better plagiarism check |
