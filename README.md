# @korede1bot

A powerful Telegram bot with multiple tools including word counter, plagiarism checker, URL shortener, image converter, and image generator.

## Features

### 📝 Word Counter
- Count words, characters, sentences, and paragraphs
- Shows unique words count
- Command: `/wordcounter [text]`

### 🔍 Plagiarism Checker
- Checks text for potential plagiarism
- Uses Google Search API (optional)
- Built-in text analysis
- Command: `/plagiarism [text]`

### 🔗 URL Shortener
- Shortens long URLs instantly
- Uses is.gd and TinyURL APIs
- Command: `/shorten [url]`

### 🖼️ Image Converter
- Convert images between formats
- Supports PNG, JPG, WebP, BMP, GIF
- Reply to image: `/convert [format]`

### 🎨 Image Generator
- Generate images from text descriptions
- Powered by Pollinations.ai
- Command: `/generate [prompt]`

## Deployment

Deployed on Railway with GitHub integration.

## Environment Variables

| Variable | Description |
|----------|-------------|
| TELEGRAM_BOT_TOKEN | Your bot token from @BotFather |
| GOOGLE_API_KEY | (Optional) For plagiarism check |
| GOOGLE_CSE_ID | (Optional) For plagiarism check |

## Commands

- `/start` - Welcome message
- `/help` - Show all commands
- `/wordcounter [text]` - Count words
- `/plagiarism [text]` - Check plagiarism
- `/shorten [url]` - Shorten URL
- `/convert [format]` - Convert image
- `/generate [prompt]` - Generate image
- `/analyze [text]` - Full text analysis
- `/time` - Current time
- `/about` - About this bot
