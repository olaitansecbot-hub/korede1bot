"""
@korede1bot - Telegram Bot with All Tools
Deployed on Railway with GitHub integration
"""

import os
import logging
import sys
import re
import io
import requests
from datetime import datetime
from PIL import Image
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ==================== LOGGING ====================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================

TOKEN = os.environ.get("BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    logger.error("❌ BOT_TOKEN environment variable not set!")
    logger.error("Please set BOT_TOKEN or TELEGRAM_BOT_TOKEN in Railway variables.")
    sys.exit(1)

logger.info(f"✅ Bot token found! (length: {len(TOKEN)} characters)")

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID = os.environ.get("GOOGLE_CSE_ID", "")

# ==================== HELPER FUNCTIONS ====================

def check_plagiarism(text):
    """Check text for plagiarism"""
    results = {
        'plagiarized': False,
        'percentage': 0,
        'sources': [],
        'message': '✅ No matches found!'
    }
    
    if GOOGLE_API_KEY and GOOGLE_CSE_ID:
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {'key': GOOGLE_API_KEY, 'cx': GOOGLE_CSE_ID, 'q': text[:50]}
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'items' in data and data['items']:
                    results['plagiarized'] = True
                    results['percentage'] = min(80, len(data['items']) * 10)
                    results['sources'] = [
                        {'title': item.get('title', 'Unknown'), 
                         'url': item.get('link', '#'),
                         'snippet': item.get('snippet', '')[:100]}
                        for item in data['items'][:3]
                    ]
                    results['message'] = f"⚠️ Found {len(data['items'])} matches!"
        except Exception as e:
            logger.error(f"Plagiarism API error: {e}")
    
    if not results['plagiarized']:
        common_phrases = ['according to', 'research shows', 'studies indicate', 
                         'it is believed', 'data suggests', 'in conclusion']
        matches = sum(1 for p in common_phrases if p in text.lower())
        if matches >= 3:
            results['plagiarized'] = True
            results['percentage'] = min(50, matches * 8)
            results['message'] = f"⚠️ Contains {matches} common phrases."
    
    return results

def shorten_url(url):
    """Shorten URL"""
    try:
        resp = requests.get("https://is.gd/create.php", 
                           params={'format': 'json', 'url': url}, timeout=10)
        if resp.status_code == 200 and 'shorturl' in resp.json():
            return resp.json()['shorturl']
    except:
        pass
    
    try:
        resp = requests.get("https://tinyurl.com/api-create.php", 
                           params={'url': url}, timeout=10)
        if resp.status_code == 200 and resp.text:
            return resp.text.strip()
    except:
        pass
    
    return None

def convert_image(image_data, output_format):
    """Convert image format"""
    try:
        img = Image.open(io.BytesIO(image_data))
        if output_format.lower() in ['jpg', 'jpeg'] and img.mode == 'RGBA':
            img = img.convert('RGB')
        buffer = io.BytesIO()
        img.save(buffer, format=output_format.upper())
        return buffer.getvalue()
    except Exception as e:
        logger.error(f"Image conversion error: {e}")
        return None

def generate_image(prompt):
    """Generate image from text"""
    try:
        url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=512&height=512&nologo=true"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        logger.error(f"Image generation error: {e}")
    return None

# ==================== COMMAND HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = f"""
🚀 *Welcome to @korede1bot, {user.first_name}!*

Your all-in-one Telegram assistant:

📝 *Word Counter* - Count words & characters
🔍 *Plagiarism Checker* - Check text originality  
🔗 *URL Shortener* - Shorten long URLs
🖼️ *Image Converter* - Convert image formats
🎨 *Image Generator* - Create images from text

Send /help for all commands.
"""
    keyboard = [
        [InlineKeyboardButton("📝 Word Counter", callback_data="word"),
         InlineKeyboardButton("🔍 Plagiarism", callback_data="plag")],
        [InlineKeyboardButton("🔗 URL Shortener", callback_data="url"),
         InlineKeyboardButton("🖼️ Image Converter", callback_data="img")],
        [InlineKeyboardButton("🎨 Image Generator", callback_data="gen"),
         InlineKeyboardButton("ℹ️ About", callback_data="about")]
    ]
    await update.message.reply_text(text, parse_mode='Markdown', 
                                   reply_markup=InlineKeyboardMarkup(keyboard))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
📚 *@korede1bot Commands*

*Text Tools:*
/wordcounter [text] - Count words & characters
/plagiarism [text] - Check for plagiarism
/analyze [text] - Full text analysis

*Utility Tools:*
/shorten [url] - Shorten a URL
/convert [format] - Convert image (reply to image)
/generate [prompt] - Generate image from text

*Basic:*
/start - Welcome message
/help - This help menu
/time - Current time
/about - About this bot

*Examples:*
/wordcounter Hello world!
/plagiarism Your text here
/shorten https://example.com/long/url
/generate A beautiful sunset
"""
    await update.message.reply_text(text, parse_mode='Markdown')

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    await update.message.reply_text(
        f"🕐 *Current Time*\n\n📅 {now.strftime('%B %d, %Y')}\n⏰ {now.strftime('%H:%M:%S')} UTC",
        parse_mode='Markdown'
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
ℹ️ *About @korede1bot*

*Features:*
✅ Word Counter
✅ Plagiarism Checker
✅ URL Shortener
✅ Image Converter
✅ Image Generator

*Tech Stack:*
🐍 Python 3.11
📦 python-telegram-bot
🚂 Railway
🔒 GitHub

*Open Source:*
https://github.com/YOUR_USERNAME/korede1bot
"""
    keyboard = [[InlineKeyboardButton("🔗 View on GitHub", 
                                     url="https://github.com/YOUR_USERNAME/korede1bot")]]
    await update.message.reply_text(text, parse_mode='Markdown', 
                                   reply_markup=InlineKeyboardMarkup(keyboard))

async def wordcounter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📝 Please provide text!\nExample: `/wordcounter Hello world`",
            parse_mode='Markdown'
        )
        return
    
    words = text.split()
    chars = len(text)
    chars_no_space = len(text.replace(' ', ''))
    sentences = len(re.findall(r'[.!?]+', text))
    
    response = f"""
📊 *Word Counter*

Text: `{text[:80]}{'...' if len(text) > 80 else ''}`

📖 Words: {len(words)}
🔤 Characters: {chars} (with spaces)
📏 Characters: {chars_no_space} (no spaces)
📝 Sentences: {sentences}
"""
    await update.message.reply_text(response, parse_mode='Markdown')

async def plagiarism_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "🔍 Please provide text to check!\nExample: `/plagiarism Your text`",
            parse_mode='Markdown'
        )
        return
    
    msg = await update.message.reply_text("🔍 Checking...", parse_mode='Markdown')
    results = check_plagiarism(text)
    
    response = f"""
🔍 *Plagiarism Check*

Text: `{text[:60]}{'...' if len(text) > 60 else ''}`

{'✅' if not results['plagiarized'] else '⚠️'} *Status:* {'Original' if not results['plagiarized'] else 'Potential Match!'}
📊 *Score:* {results['percentage']}%

{results['message']}
"""
    if results['sources']:
        response += "\n*Sources:*\n"
        for i, s in enumerate(results['sources'][:2], 1):
            response += f"{i}. [{s['title']}]({s['url']})\n"
    
    await msg.edit_text(response, parse_mode='Markdown', disable_web_page_preview=True)

async def shorten_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = ' '.join(context.args)
    if not url:
        await update.message.reply_text(
            "🔗 Please provide a URL!\nExample: `/shorten https://example.com`",
            parse_mode='Markdown'
        )
        return
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    msg = await update.message.reply_text("🔗 Shortening...", parse_mode='Markdown')
    short = shorten_url(url)
    
    if short:
        await msg.edit_text(
            f"🔗 *URL Shortened*\n\nOriginal: `{url}`\nShort: `{short}`",
            parse_mode='Markdown'
        )
    else:
        await msg.edit_text("❌ Failed to shorten URL. Please try again.")

async def convert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    format_type = ' '.join(context.args).lower()
    
    if not format_type:
        await update.message.reply_text(
            "🖼️ Reply to an image with format!\nExample: `/convert png`\n"
            "Supported: png, jpg, webp, bmp, gif",
            parse_mode='Markdown'
        )
        return
    
    if format_type == 'jpeg':
        format_type = 'jpg'
    
    if format_type not in ['png', 'jpg', 'webp', 'bmp', 'gif']:
        await update.message.reply_text(f"❌ Unsupported format: {format_type}")
        return
    
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text("🖼️ Please reply to an image!")
        return
    
    msg = await update.message.reply_text(f"🔄 Converting to {format_type.upper()}...", 
                                         parse_mode='Markdown')
    
    photo = update.message.reply_to_message.photo[-1]
    file = await photo.get_file()
    image_data = await file.download_as_bytearray()
    
    converted = convert_image(image_data, format_type)
    
    if converted:
        await msg.delete()
        await update.message.reply_document(
            document=io.BytesIO(converted),
            filename=f"converted.{format_type}",
            caption=f"✅ Converted to {format_type.upper()}!"
        )
    else:
        await msg.edit_text("❌ Failed to convert image.")

async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = ' '.join(context.args)
    if not prompt:
        await update.message.reply_text(
            "🎨 Describe what to generate!\nExample: `/generate A beautiful sunset`",
            parse_mode='Markdown'
        )
        return
    
    msg = await update.message.reply_text(
        f"🎨 Generating image for: `{prompt[:50]}{'...' if len(prompt) > 50 else ''}`\n⏳ Please wait...",
        parse_mode='Markdown'
    )
    
    image_data = generate_image(prompt)
    
    if image_data:
        await msg.delete()
        await update.message.reply_photo(
            photo=io.BytesIO(image_data),
            caption=f"🎨 Generated from: `{prompt}`",
            parse_mode='Markdown'
        )
    else:
        await msg.edit_text("❌ Failed to generate image. Try a different prompt.")

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📊 Please provide text!\nExample: `/analyze Your text`",
            parse_mode='Markdown'
        )
        return
    
    msg = await update.message.reply_text("📊 Analyzing...", parse_mode='Markdown')
    
    words = len(text.split())
    chars = len(text)
    sentences = len(re.findall(r'[.!?]+', text))
    plagiarism = check_plagiarism(text)
    
    response = f"""
📊 *Text Analysis*

Text: `{text[:60]}{'...' if len(text) > 60 else ''}`

*Stats:*
• Words: {words}
• Characters: {chars}
• Sentences: {sentences}

*Plagiarism:*
• Status: {'✅ Original' if not plagiarism['plagiarized'] else '⚠️ Match'}
• Score: {plagiarism['percentage']}%
{plagiarism['message']}
"""
    await msg.edit_text(response, parse_mode='Markdown')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith('/'):
        return
    
    if 'http' in text:
        keyboard = [[InlineKeyboardButton("🔗 Shorten URL", 
                                        callback_data=f"shorten_{text[:100]}")]]
        await update.message.reply_text(
            "🔗 I found a URL! Click to shorten it.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 Word Count", callback_data=f"wc_{text[:50]}"),
         InlineKeyboardButton("🔍 Check Plagiarism", callback_data=f"plag_{text[:50]}")]
    ]
    await update.message.reply_text(
        f"📝 Text: `{text[:80]}{'...' if len(text) > 80 else ''}`\n\nChoose an action:",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔄 PNG", callback_data="img_png"),
         InlineKeyboardButton("🔄 JPG", callback_data="img_jpg")],
        [InlineKeyboardButton("🔄 WebP", callback_data="img_webp"),
         InlineKeyboardButton("🔄 BMP", callback_data="img_bmp")]
    ]
    await update.message.reply_text(
        "🖼️ Choose format to convert this image:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "word":
        await query.edit_message_text(
            "📝 Use `/wordcounter [text]` or send any text!",
            parse_mode='Markdown'
        )
    elif data == "plag":
        await query.edit_message_text(
            "🔍 Use `/plagiarism [text]` to check originality!",
            parse_mode='Markdown'
        )
    elif data == "url":
        await query.edit_message_text(
            "🔗 Use `/shorten [url]` to shorten links!",
            parse_mode='Markdown'
        )
    elif data == "img":
        await query.edit_message_text(
            "🖼️ Reply to an image with `/convert [format]`",
            parse_mode='Markdown'
        )
    elif data == "gen":
        await query.edit_message_text(
            "🎨 Use `/generate [prompt]` to create images!",
            parse_mode='Markdown'
        )
    elif data == "about":
        await query.edit_message_text(
            "ℹ️ @korede1bot - Your all-in-one Telegram assistant.\n"
            "https://github.com/YOUR_USERNAME/korede1bot"
        )
    elif data.startswith("img_"):
        format_type = data[4:]
        await query.edit_message_text(f"🔄 Converting to {format_type.upper()}...",
                                     parse_mode='Markdown')
        try:
            photo = update.effective_message.reply_to_message.photo[-1]
            file = await photo.get_file()
            image_data = await file.download_as_bytearray()
            converted = convert_image(image_data, format_type)
            if converted:
                await query.edit_message_text("✅ Done!")
                await update.effective_message.reply_document(
                    document=io.BytesIO(converted),
                    filename=f"converted.{format_type}",
                    caption=f"✅ Converted to {format_type.upper()}!"
                )
            else:
                await query.edit_message_text("❌ Conversion failed.")
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            await query.edit_message_text("❌ Failed to process image.")
    elif data.startswith("shorten_"):
        url = data[8:]
        short = shorten_url(url)
        if short:
            await query.edit_message_text(f"🔗 Shortened: `{short}`", parse_mode='Markdown')
        else:
            await query.edit_message_text("❌ Failed to shorten URL.")
    elif data.startswith("wc_"):
        text = data[3:]
        words = len(text.split())
        chars = len(text)
        await query.edit_message_text(
            f"📊 Words: {words}\n🔤 Characters: {chars}",
            parse_mode='Markdown'
        )
    elif data.startswith("plag_"):
        text = data[5:]
        results = check_plagiarism(text)
        status = "✅ Original" if not results['plagiarized'] else "⚠️ Match"
        await query.edit_message_text(
            f"🔍 Status: {status}\n📊 Score: {results['percentage']}%\n{results['message']}",
            parse_mode='Markdown'
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")
    try:
        await update.effective_message.reply_text("⚠️ Something went wrong. Please try again.")
    except:
        pass

# ==================== MAIN ====================

def main():
    logger.info("🚀 Starting @korede1bot...")
    
    try:
        app = ApplicationBuilder().token(TOKEN).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("time", time_command))
        app.add_handler(CommandHandler("about", about_command))
        app.add_handler(CommandHandler("wordcounter", wordcounter_command))
        app.add_handler(CommandHandler("plagiarism", plagiarism_command))
        app.add_handler(CommandHandler("shorten", shorten_command))
        app.add_handler(CommandHandler("convert", convert_command))
        app.add_handler(CommandHandler("generate", generate_command))
        app.add_handler(CommandHandler("analyze", analyze_command))
        
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        app.add_handler(MessageHandler(filters.COMMAND, 
            lambda u, c: u.message.reply_text("❌ Unknown command. Use /help")))
        
        app.add_handler(CallbackQueryHandler(button_callback))
        app.add_error_handler(error_handler)
        
        logger.info("✅ Bot is running successfully!")
        app.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
