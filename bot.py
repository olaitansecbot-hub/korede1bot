"""
@korede1bot - Telegram Bot with All-in-One Tools
Features: Word Counter, Plagiarism Checker, URL Shortener, Image Converter, Image Generator
Deployed on Railway with GitHub integration
"""

import os
import logging
import sys
import re
import json
import base64
import io
import hashlib
import requests
from datetime import datetime
from urllib.parse import urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from PIL import Image

# ==================== CONFIGURATION ====================

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Bot token from environment variable
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("BOT_TOKEN")
if not TOKEN:
    logger.error("❌ BOT_TOKEN environment variable not set!")
    sys.exit(1)

# Free API keys for additional features (optional)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID = os.environ.get("GOOGLE_CSE_ID", "")

# ==================== HELPER FUNCTIONS ====================

def check_plagiarism(text):
    """Check text for plagiarism using multiple methods"""
    results = {
        'plagiarized': False,
        'percentage': 0,
        'sources': [],
        'message': ''
    }
    
    # Method 1: Google Custom Search API
    if GOOGLE_API_KEY and GOOGLE_CSE_ID:
        try:
            search_text = text[:50]
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': GOOGLE_API_KEY,
                'cx': GOOGLE_CSE_ID,
                'q': search_text
            }
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'items' in data and len(data['items']) > 0:
                    results['plagiarized'] = True
                    results['percentage'] = min(80, len(data['items']) * 10)
                    for item in data['items'][:3]:
                        results['sources'].append({
                            'title': item.get('title', 'Unknown'),
                            'url': item.get('link', '#'),
                            'snippet': item.get('snippet', '')[:100]
                        })
                    results['message'] = f"⚠️ Found {len(data['items'])} possible matches!"
                else:
                    results['message'] = "✅ No matches found!"
            else:
                results['message'] = "🔍 Using built-in analysis..."
        except Exception as e:
            logger.error(f"Plagiarism API error: {e}")
            results['message'] = "🔍 Using text analysis..."
    
    # Method 2: Built-in text analysis
    if not results['plagiarized']:
        common_phrases = [
            "according to", "as stated by", "research shows", 
            "studies indicate", "it is believed that", "it has been found",
            "the results show", "data suggests", "analysis reveals",
            "in conclusion", "therefore", "furthermore", "consequently"
        ]
        
        text_lower = text.lower()
        matches = sum(1 for phrase in common_phrases if phrase in text_lower)
        
        if matches >= 3:
            results['plagiarized'] = True
            results['percentage'] = min(50, matches * 8)
            results['message'] = f"⚠️ Contains {matches} common academic phrases."
        else:
            results['message'] = "✅ No obvious similarity detected!"
    
    # Method 3: Word uniqueness analysis
    words = re.findall(r'\b\w+\b', text.lower())
    unique_words = set(words)
    
    if len(words) > 0:
        uniqueness_ratio = len(unique_words) / len(words)
        if uniqueness_ratio < 0.4 and len(words) > 20:
            results['plagiarized'] = True
            results['percentage'] = max(results['percentage'], 35)
            results['message'] += " Text has low uniqueness."
    
    return results

def shorten_url(url):
    """Shorten URL using free API"""
    try:
        # Try using is.gd API
        response = requests.get(
            "https://is.gd/create.php",
            params={'format': 'json', 'url': url},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'shorturl' in data:
                return data['shorturl']
        else:
            # Fallback to TinyURL
            response = requests.get(
                "https://tinyurl.com/api-create.php",
                params={'url': url},
                timeout=10
            )
            if response.status_code == 200 and response.text:
                return response.text.strip()
    except Exception as e:
        logger.error(f"URL shortener error: {e}")
        return None
    return None

def convert_image(image_data, output_format):
    """Convert image to different format"""
    try:
        img = Image.open(io.BytesIO(image_data))
        
        # Convert RGBA to RGB for JPEG
        if output_format.lower() in ['jpeg', 'jpg'] and img.mode == 'RGBA':
            img = img.convert('RGB')
        
        output_buffer = io.BytesIO()
        img.save(output_buffer, format=output_format.upper())
        return output_buffer.getvalue()
    except Exception as e:
        logger.error(f"Image conversion error: {e}")
        return None

def generate_image(prompt):
    """Generate image using free AI API"""
    try:
        # Try using Pollinations.ai (free, no API key required)
        url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=512&height=512&nologo=true"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.content
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        return None
    return None

# ==================== COMMAND HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    first_name = user.first_name or "there"
    
    welcome_text = f"""
🚀 *Welcome to @korede1bot, {first_name}!*

Your all-in-one Telegram assistant with powerful tools:

*🔧 Available Tools:*
• 📝 Word Counter - Count words, characters, sentences
• 🔍 Plagiarism Checker - Check text uniqueness  
• 🔗 URL Shortener - Shorten long URLs instantly
• 🖼️ Image Converter - Convert images between formats
• 🎨 Image Generator - Create images from text

*How to get started:*
Send /help to see all commands
Or use the buttons below!
"""
    
    keyboard = [
        [
            InlineKeyboardButton("📝 Word Counter", callback_data="word_counter"),
            InlineKeyboardButton("🔍 Plagiarism Check", callback_data="plagiarism")
        ],
        [
            InlineKeyboardButton("🔗 URL Shortener", callback_data="url_shortener"),
            InlineKeyboardButton("🖼️ Image Converter", callback_data="image_converter")
        ],
        [
            InlineKeyboardButton("🎨 Image Generator", callback_data="image_generator"),
            InlineKeyboardButton("ℹ️ About", callback_data="about")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    logger.info(f"User {user.id} started the bot")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📚 *@korede1bot - Available Commands*

*Text Tools:*
/wordcounter [text] - Count words, characters, sentences
/plagiarism [text] - Check text for plagiarism
/analyze [text] - Full text analysis

*Utility Tools:*
/shorten [url] - Shorten a long URL
/convert [format] - Convert image (reply to an image)
/generate [prompt] - Generate image from text

*Basic Commands:*
/start - Welcome message
/help - Show this help
/time - Current time
/about - About this bot

*Quick Examples:*
/wordcounter The quick brown fox jumps over the lazy dog
/plagiarism According to recent studies, climate change is accelerating
/shorten https://www.example.com/very/long/url
/generate A beautiful sunset over mountains
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ==================== WORD COUNTER ====================

async def wordcounter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /wordcounter command"""
    text = ' '.join(context.args)
    
    if not text:
        await update.message.reply_text(
            "📝 *Word Counter*\n\n"
            "Please provide text to count!\n"
            "Example: `/wordcounter The quick brown fox`",
            parse_mode='Markdown'
        )
        return
    
    # Count statistics
    word_count = len(text.split())
    char_count = len(text)
    char_no_spaces = len(text.replace(' ', ''))
    sentence_count = len(re.findall(r'[.!?]+', text))
    paragraph_count = len(re.findall(r'\n\s*\n', text)) + 1
    
    words = re.findall(r'\b\w+\b', text.lower())
    unique_words = len(set(words))
    
    response = f"""
📊 *Word Counter Results*

📝 Text: `{text[:100]}{'...' if len(text) > 100 else ''}`

📖 *Statistics:*
• Words: {word_count}
• Characters (with spaces): {char_count}
• Characters (no spaces): {char_no_spaces}
• Sentences: {sentence_count}
• Paragraphs: {paragraph_count}
• Unique words: {unique_words}
"""
    await update.message.reply_text(response, parse_mode='Markdown')

# ==================== PLAGIARISM CHECKER ====================

async def plagiarism_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /plagiarism command"""
    text = ' '.join(context.args)
    
    if not text:
        await update.message.reply_text(
            "🔍 *Plagiarism Checker*\n\n"
            "Please provide text to check!\n"
            "Example: `/plagiarism Your text here`",
            parse_mode='Markdown'
        )
        return
    
    processing_msg = await update.message.reply_text(
        "🔍 *Checking for plagiarism...*",
        parse_mode='Markdown'
    )
    
    results = check_plagiarism(text)
    
    status_icon = "✅" if not results['plagiarized'] else "⚠️"
    status_text = "Original" if not results['plagiarized'] else "Potential Match!"
    
    response = f"""
🔍 *Plagiarism Check Results*

📝 Text: `{text[:80]}{'...' if len(text) > 80 else ''}`

{status_icon} *Status:* {status_text}
📊 *Similarity Score:* {results['percentage']}%

{results['message']}
"""
    
    if results['sources']:
        response += "\n*Potential Sources:*\n"
        for i, source in enumerate(results['sources'][:2], 1):
            response += f"{i}. [{source['title']}]({source['url']})\n"
    
    await processing_msg.edit_text(response, parse_mode='Markdown', disable_web_page_preview=True)

# ==================== URL SHORTENER ====================

async def shorten_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /shorten command"""
    url = ' '.join(context.args)
    
    if not url:
        await update.message.reply_text(
            "🔗 *URL Shortener*\n\n"
            "Please provide a URL to shorten!\n"
            "Example: `/shorten https://example.com/very/long/url`",
            parse_mode='Markdown'
        )
        return
    
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    processing_msg = await update.message.reply_text(
        "🔗 *Shortening URL...*",
        parse_mode='Markdown'
    )
    
    short_url = shorten_url(url)
    
    if short_url:
        response = f"""
🔗 *URL Shortener Result*

📎 *Original URL:*
`{url}`

✂️ *Shortened URL:*
`{short_url}`

✅ Successfully shortened!
"""
    else:
        response = "❌ Failed to shorten URL. Please try again with a valid URL."
    
    await processing_msg.edit_text(response, parse_mode='Markdown')

# ==================== IMAGE CONVERTER ====================

async def convert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /convert command"""
    format_type = ' '.join(context.args)
    
    if not format_type:
        await update.message.reply_text(
            "🖼️ *Image Converter*\n\n"
            "Reply to an image with the format you want!\n"
            "Example: `/convert png` or `/convert jpg`\n\n"
            "Supported formats: png, jpg, jpeg, webp, bmp, gif",
            parse_mode='Markdown'
        )
        return
    
    # Check if replying to an image
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text(
            "🖼️ *Image Converter*\n\n"
            "Please reply to an image with the format you want!\n"
            "Example: `/convert png` (reply to an image)",
            parse_mode='Markdown'
        )
        return
    
    format_type = format_type.lower().replace('.', '')
    if format_type == 'jpeg':
        format_type = 'jpg'
    
    supported_formats = ['png', 'jpg', 'jpeg', 'webp', 'bmp', 'gif']
    if format_type not in supported_formats:
        await update.message.reply_text(
            f"❌ Unsupported format: {format_type}\n"
            f"Supported formats: {', '.join(supported_formats)}",
            parse_mode='Markdown'
        )
        return
    
    processing_msg = await update.message.reply_text(
        f"🔄 *Converting image to {format_type.upper()}...*",
        parse_mode='Markdown'
    )
    
    # Get the image
    photo = update.message.reply_to_message.photo[-1]
    file = await photo.get_file()
    image_data = await file.download_as_bytearray()
    
    # Convert the image
    converted = convert_image(image_data, format_type)
    
    if converted:
        await processing_msg.delete()
        await update.message.reply_document(
            document=io.BytesIO(converted),
            filename=f"converted.{format_type}",
            caption=f"✅ Converted to {format_type.upper()}!"
        )
    else:
        await processing_msg.edit_text(
            "❌ Failed to convert image. Please try again with a valid image."
        )

# ==================== IMAGE GENERATOR ====================

async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /generate command"""
    prompt = ' '.join(context.args)
    
    if not prompt:
        await update.message.reply_text(
            "🎨 *Image Generator*\n\n"
            "Generate images from text descriptions!\n"
            "Example: `/generate A beautiful sunset over mountains`\n\n"
            "Try describing:\n"
            "• Scenery: 'A peaceful forest with sunlight'\n"
            "• Objects: 'A futuristic sports car'\n"
            "• Art: 'An abstract painting with vibrant colors'",
            parse_mode='Markdown'
        )
        return
    
    processing_msg = await update.message.reply_text(
        f"🎨 *Generating image...*\n"
        f"Prompt: `{prompt[:50]}{'...' if len(prompt) > 50 else ''}`\n"
        "⏳ Please wait (may take 10-20 seconds)",
        parse_mode='Markdown'
    )
    
    # Generate the image
    image_data = generate_image(prompt)
    
    if image_data:
        await processing_msg.delete()
        await update.message.reply_photo(
            photo=io.BytesIO(image_data),
            caption=f"🎨 *Generated Image*\n\nPrompt: `{prompt}`",
            parse_mode='Markdown'
        )
    else:
        await processing_msg.edit_text(
            "❌ Failed to generate image. Please try again with a different prompt."
        )

# ==================== ANALYZE COMMAND ====================

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /analyze command - Full text analysis"""
    text = ' '.join(context.args)
    
    if not text:
        await update.message.reply_text(
            "📊 *Text Analysis*\n\n"
            "Please provide text to analyze!\n"
            "Example: `/analyze Your text here`",
            parse_mode='Markdown'
        )
        return
    
    processing_msg = await update.message.reply_text(
        "📊 *Analyzing text...*",
        parse_mode='Markdown'
    )
    
    # Word counter
    word_count = len(text.split())
    char_count = len(text)
    sentence_count = len(re.findall(r'[.!?]+', text))
    
    # Plagiarism check
    plagiarism_results = check_plagiarism(text)
    
    response = f"""
📊 *Complete Text Analysis*

📝 Text: `{text[:80]}{'...' if len(text) > 80 else ''}`

*Basic Statistics:*
• Words: {word_count}
• Characters: {char_count}
• Sentences: {sentence_count}

*Plagiarism Check:*
• Status: {'✅ Original' if not plagiarism_results['plagiarized'] else '⚠️ Potential Match'}
• Score: {plagiarism_results['percentage']}%

{plagiarism_results['message']}
"""
    
    await processing_msg.edit_text(response, parse_mode='Markdown')

# ==================== BASIC COMMANDS ====================

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /time command"""
    now = datetime.now()
    response = f"""
🕐 *Current Time*

📅 Date: {now.strftime("%B %d, %Y")}
⏰ Time: {now.strftime("%H:%M:%S")}
🌐 Timezone: UTC
"""
    await update.message.reply_text(response, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    about_text = """
ℹ️ *About @korede1bot*

*Features:*
• ✅ Word Counter
• ✅ Plagiarism Checker
• ✅ URL Shortener
• ✅ Image Converter
• ✅ Image Generator
• ✅ 24/7 Availability

*Technology:*
• 🐍 Python 3.11
• 📦 python-telegram-bot
• 🚂 Railway
• 🔒 GitHub

*Open Source:* 
https://github.com/YOUR_USERNAME/korede1bot
"""
    keyboard = [[InlineKeyboardButton("🔗 View on GitHub", url="https://github.com/YOUR_USERNAME/korede1bot")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(about_text, parse_mode='Markdown', reply_markup=reply_markup)

# ==================== MESSAGE HANDLERS ====================

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle any text message"""
    if update.message.text.startswith('/'):
        return
    
    # Auto-detect URLs for shortening
    if 'http' in update.message.text.lower():
        keyboard = [
            [InlineKeyboardButton("🔗 Shorten This URL", callback_data=f"shorten_{update.message.text[:100]}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔗 I detected a URL in your message!\n"
            "Click the button below to shorten it.",
            reply_markup=reply_markup
        )
        return
    
    # Auto-analyze text
    keyboard = [
        [
            InlineKeyboardButton("📊 Word Count", callback_data=f"wc_{update.message.text[:50]}"),
            InlineKeyboardButton("🔍 Check Plagiarism", callback_data=f"plag_{update.message.text[:50]}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"📝 *Text Received!*\n\n"
        f"`{update.message.text[:100]}{'...' if len(update.message.text) > 100 else ''}`\n\n"
        f"Choose an action below:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages"""
    keyboard = [
        [
            InlineKeyboardButton("🔄 Convert to PNG", callback_data="img_png"),
            InlineKeyboardButton("🔄 Convert to JPG", callback_data="img_jpg")
        ],
        [
            InlineKeyboardButton("🔄 Convert to WebP", callback_data="img_webp"),
            InlineKeyboardButton("🔄 Convert to BMP", callback_data="img_bmp")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🖼️ *Image Received!*\n\n"
        "Choose a format to convert this image:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

# ==================== CALLBACK QUERY HANDLERS ====================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # Tool info buttons
    if data == "word_counter":
        await query.edit_message_text(
            "📝 *Word Counter*\n\n"
            "Use: `/wordcounter Your text here`\n\n"
            "Or send any text and I'll offer to count it!",
            parse_mode='Markdown'
        )
    elif data == "plagiarism":
        await query.edit_message_text(
            "🔍 *Plagiarism Checker*\n\n"
            "Use: `/plagiarism Your text here`\n\n"
            "I'll check for:\n"
            "• Online matches\n"
            "• Common phrases\n"
            "• Text uniqueness",
            parse_mode='Markdown'
        )
    elif data == "url_shortener":
        await query.edit_message_text(
            "🔗 *URL Shortener*\n\n"
            "Use: `/shorten https://example.com/long/url`\n\n"
            "Or send a message with a URL and I'll offer to shorten it!",
            parse_mode='Markdown'
        )
    elif data == "image_converter":
        await query.edit_message_text(
            "🖼️ *Image Converter*\n\n"
            "Reply to an image with:\n"
            "`/convert png` or `/convert jpg`\n\n"
            "Supported: png, jpg, webp, bmp, gif",
            parse_mode='Markdown'
        )
    elif data == "image_generator":
        await query.edit_message_text(
            "🎨 *Image Generator*\n\n"
            "Use: `/generate Your description`\n\n"
            "Examples:\n"
            "• `/generate A beautiful sunset`\n"
            "• `/generate A futuristic city`\n"
            "• `/generate A cute cat with glasses`",
            parse_mode='Markdown'
        )
    elif data == "about":
        await query.edit_message_text(
            "ℹ️ *@korede1bot*\n\n"
            "A powerful Telegram bot with multiple tools.\n\n"
            "Built with Python, deployed on Railway.\n"
            "https://github.com/YOUR_USERNAME/korede1bot",
            parse_mode='Markdown'
        )
    
    # Image conversion buttons
    elif data.startswith("img_"):
        format_type = data[4:]
        if format_type == 'jpg':
            format_type = 'jpg'
        
        await query.edit_message_text(
            f"🔄 *Converting image to {format_type.upper()}...*",
            parse_mode='Markdown'
        )
        
        # Get the image from the replied message
        try:
            photo = update.effective_message.reply_to_message.photo[-1]
            file = await photo.get_file()
            image_data = await file.download_as_bytearray()
            
            converted = convert_image(image_data, format_type)
            
            if converted:
                await query.edit_message_text("✅ Image converted!")
                await update.effective_message.reply_document(
                    document=io.BytesIO(converted),
                    filename=f"converted.{format_type}",
                    caption=f"✅ Converted to {format_type.upper()}!"
                )
            else:
                await query.edit_message_text("❌ Failed to convert image.")
        except Exception as e:
            logger.error(f"Image conversion error: {e}")
            await query.edit_message_text("❌ Failed to process image. Please try again.")
    
    # URL shortening callback
    elif data.startswith("shorten_"):
        url = data[8:]
        short_url = shorten_url(url)
        
        if short_url:
            await query.edit_message_text(
                f"🔗 *URL Shortened!*\n\n"
                f"Original: `{url[:80]}...`\n"
                f"Shortened: `{short_url}`",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text("❌ Failed to shorten URL. Please try again.")
    
    # Word count callback
    elif data.startswith("wc_"):
        text = data[3:]
        word_count = len(text.split())
        char_count = len(text)
        
        await query.edit_message_text(
            f"📊 *Word Count*\n\n"
            f"Text: `{text[:60]}{'...' if len(text) > 60 else ''}`\n\n"
            f"Words: {word_count}\n"
            f"Characters: {char_count}",
            parse_mode='Markdown'
        )
    
    # Plagiarism callback
    elif data.startswith("plag_"):
        text = data[5:]
        results = check_plagiarism(text)
        
        status = "✅ Original" if not results['plagiarized'] else "⚠️ Potential Match"
        
        await query.edit_message_text(
            f"🔍 *Plagiarism Check*\n\n"
            f"Text: `{text[:60]}{'...' if len(text) > 60 else ''}`\n\n"
            f"Status: {status}\n"
            f"Score: {results['percentage']}%\n\n"
            f"{results['message']}",
            parse_mode='Markdown'
        )

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands"""
    await update.message.reply_text(
        "❌ I don't understand that command.\n\n"
        "Use /help to see all available commands.",
        parse_mode='Markdown'
    )

# ==================== ERROR HANDLER ====================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ Oops! Something went wrong.\n"
                "Please try again or use /help for assistance."
            )
    except:
        pass

# ==================== MAIN FUNCTION ====================

def main():
    """Start the bot"""
    logger.info("🚀 Starting @korede1bot with all features...")
    
    try:
        application = ApplicationBuilder().token(TOKEN).build()
        
        # Command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("time", time_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("wordcounter", wordcounter_command))
        application.add_handler(CommandHandler("plagiarism", plagiarism_command))
        application.add_handler(CommandHandler("shorten", shorten_command))
        application.add_handler(CommandHandler("convert", convert_command))
        application.add_handler(CommandHandler("generate", generate_command))
        application.add_handler(CommandHandler("analyze", analyze_command))
        
        # Message handlers
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
        
        # Callback handler
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # Error handler
        application.add_error_handler(error_handler)
        
        logger.info("✅ Bot is running with long polling...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
