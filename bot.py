"""
@korede1bot - Telegram Bot
Deployed on Railway with GitHub integration
"""

import os
import logging
import sys
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

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

# ==================== COMMAND HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    first_name = user.first_name or "there"
    
    welcome_text = f"""
🚀 *Welcome to @korede1bot, {first_name}!*

I'm your friendly Telegram assistant. Here's what I can do:

• 📝 Echo your messages back
• 🕐 Show current date and time
• 📊 Count words in your text
• 🎯 Respond to commands

*How to use:*
Send /help to see all available commands.
"""
    
    keyboard = [
        [
            InlineKeyboardButton("📝 Try Me", callback_data="try"),
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
📚 *Available Commands*

/start - Welcome message
/help - Show this help menu
/time - Get current date and time
/echo - Echo your message back
/count - Count words in your text
/about - Learn about this bot

*Quick Tips:*
• Just send any text and I'll echo it!
• I'm available 24/7 thanks to Railway 🚂
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

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

async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /echo command"""
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "🔊 Please provide text to echo!\nExample: `/echo Hello world!`",
            parse_mode='Markdown'
        )
        return
    await update.message.reply_text(f"🔊 *You said:* {text}", parse_mode='Markdown')

async def count_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /count command"""
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📝 Please provide text to count!\nExample: `/count Hello world!`",
            parse_mode='Markdown'
        )
        return
    
    word_count = len(text.split())
    char_count = len(text)
    
    response = f"""
📊 *Word Count*

Text: `{text[:50]}{'...' if len(text) > 50 else ''}`

📖 Words: {word_count}
🔤 Characters: {char_count}
"""
    await update.message.reply_text(response, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    about_text = """
ℹ️ *About @korede1bot*

Built with ❤️ using:
• Python
• python-telegram-bot
• Railway
• GitHub

*Open Source:*
https://github.com/YOUR_USERNAME/korede1bot
"""
    keyboard = [[InlineKeyboardButton("🔗 View on GitHub", url="https://github.com/YOUR_USERNAME/korede1bot")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(about_text, parse_mode='Markdown', reply_markup=reply_markup)

# ==================== MESSAGE HANDLERS ====================

async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo any text message back"""
    if update.message.text.startswith('/'):
        return
    
    await update.message.reply_text(
        f"🔊 *You said:* {update.message.text}",
        parse_mode='Markdown'
    )

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands"""
    await update.message.reply_text(
        "❌ I don't understand that command.\nUse /help to see all commands."
    )

# ==================== CALLBACK QUERY HANDLERS ====================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "try":
        await query.edit_message_text(
            "📝 *Try me!*\n\n"
            "Send any message and I'll echo it back.\n"
            "Or use: /time, /count, /echo",
            parse_mode='Markdown'
        )
    elif query.data == "about":
        await query.edit_message_text(
            "ℹ️ *@korede1bot*\n\n"
            "A simple Telegram bot built with Python.\n\n"
            "https://github.com/YOUR_USERNAME/korede1bot",
            parse_mode='Markdown'
        )

# ==================== ERROR HANDLER ====================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")

# ==================== MAIN FUNCTION ====================

def main():
    """Start the bot"""
    logger.info("🚀 Starting @korede1bot...")
    
    try:
        application = ApplicationBuilder().token(TOKEN).build()
        
        # Register command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("time", time_command))
        application.add_handler(CommandHandler("echo", echo_command))
        application.add_handler(CommandHandler("count", count_command))
        application.add_handler(CommandHandler("about", about_command))
        
        # Register message handlers
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))
        application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
        
        # Register callback handler
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
