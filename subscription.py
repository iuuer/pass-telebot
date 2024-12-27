from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database

class SubscriptionManager:
    def __init__(self, db: Database):
        self.db = db

    async def check_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Check if user is subscribed to all required channels"""
        user_id = update.effective_user.id
        channels = self.db.get_required_channels()
        
        if not channels:
            return True
            
        not_subscribed = []
        for channel_id, channel_username in channels:
            try:
                member = await context.bot.get_chat_member(channel_id, user_id)
                if member.status in ['left', 'kicked', 'restricted']:
                    not_subscribed.append(f"@{channel_username}")
            except:
                continue
                
        if not_subscribed:
            keyboard = []
            for channel in not_subscribed:
                keyboard.append([InlineKeyboardButton(
                    f"📢 Join {channel}", 
                    url=f"https://t.me/{channel.replace('@', '')}"
                )])
            keyboard.append([InlineKeyboardButton("🔄 Check Again", callback_data="check_subscription")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "❗️ *Please subscribe to all required channels:*\n\n" + 
                "\n".join(f"• {channel}" for channel in not_subscribed) +
                "\n\nClick Check Again after subscribing.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return False
            
        return True

    async def handle_subscription_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the check subscription callback"""
        query = update.callback_query
        await query.answer()
        
        if await self.check_subscription(update, context):
            await query.message.delete()
            # Re-trigger the original command
            if 'original_command' in context.user_data:
                await context.user_data['original_command'](update, context)
        else:
            await query.answer("❌ You haven't subscribed to all channels yet!", show_alert=True)