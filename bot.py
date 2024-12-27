from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes
)
from database import Database
from password_generator import PasswordGenerator
from admin_panel import AdminPanel
from subscription import SubscriptionManager
from config import Config
from datetime import datetime

TOKEN = "YOUR_BOT_TOKEN"
OWNER_ID = 123456789  # Replace with your Telegram ID

db = Database()
config = Config(db, OWNER_ID)
password_generator = PasswordGenerator()
admin_panel = AdminPanel(db, config)
subscription_manager = SubscriptionManager(db)

async def check_subscription_wrapper(func):
    """Decorator to check channel subscription before executing commands"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if await subscription_manager.check_subscription(update, context):
            return await func(update, context)
        context.user_data['original_command'] = func
    return wrapper

@check_subscription_wrapper
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Existing start command implementation...
    pass

@check_subscription_wrapper
async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Existing show_history implementation...
    pass

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin panel"""
    await admin_panel.show_admin_panel(update, context)

async def add_moderator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a new moderator"""
    if not await config.is_admin(update.effective_user.id):
        await update.message.reply_text("⛔️ Only the owner can add moderators.")
        return

    try:
        username = context.args[0].replace('@', '')
        # You would need to implement get_user_id_by_username
        user_id = await get_user_id_by_username(context.bot, username)
        
        if db.add_moderator(user_id, username, update.effective_user.id):
            await update.message.reply_text(f"✅ @{username} has been added as moderator.")
        else:
            await update.message.reply_text("❌ Maximum number of moderators reached (3).")
    except:
        await update.message.reply_text(
            "❌ Invalid command format.\nUse: `/addmod @username`",
            parse_mode='Markdown'
        )

async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a required channel"""
    if not await config.can_manage_channels(update.effective_user.id):
        await update.message.reply_text("⛔️ You don't have permission to manage channels.")
        return

    try:
        channel_username = context.args[0].replace('@', '')
        chat = await context.bot.get_chat(f"@{channel_username}")
        
        # Check if bot is admin in the channel
        bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
        if bot_member.status != 'administrator':
            await update.message.reply_text(
                "❌ The bot must be an administrator in the channel first!"
            )
            return
            
        if db.add_required_channel(str(chat.id), channel_username, update.effective_user.id):
            await update.message.reply_text(f"✅ @{channel_username} added to required channels.")
        else:
            await update.message.reply_text("❌ Maximum number of required channels reached (10).")
    except Exception as e:
        await update.message.reply_text(
            "❌ Invalid command format or channel not found.\n"
            "Use: `/addchannel @channel`\n"
            "Make sure the bot is an admin in the channel!",
            parse_mode='Markdown'
        )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries"""
    query = update.callback_query
    
    if query.data == "check_subscription":
        await subscription_manager.handle_subscription_check(update, context)
    else:
        await admin_panel.handle_admin_callback(update, context)

def main():
    application = Application.builder().token(TOKEN).build()

    # Existing handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("id", show_history))
    
    # Admin handlers
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CommandHandler("addmod", add_moderator))
    application.add_handler(CommandHandler("addchannel", add_channel))
    
    # Callback handler
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Message handler for custom length passwords
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        check_subscription_wrapper(handle_custom_length)
    ))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()