from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from config import Config

class AdminPanel:
    def __init__(self, db: Database, config: Config):
        self.db = db
        self.config = config

    async def show_admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.config.is_admin(update.effective_user.id):
            await update.message.reply_text("⛔️ You don't have permission to access the admin panel.")
            return

        keyboard = [
            [InlineKeyboardButton("👥 Manage Moderators", callback_data="admin_mods")],
            [InlineKeyboardButton("📢 Required Channels", callback_data="admin_channels")],
            [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🔐 *Admin Control Panel*\n\n"
            "Select an option:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_admin_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = update.effective_user.id
        
        if not await self.config.is_admin_or_mod(user_id):
            await query.answer("⛔️ You don't have permission.", show_alert=True)
            return

        await query.answer()
        
        if query.data == "admin_mods":
            await self._show_moderators_menu(query)
        elif query.data == "admin_channels":
            await self._show_channels_menu(query)
        elif query.data == "admin_stats":
            await self._show_statistics(query)
        elif query.data.startswith("remove_mod_"):
            mod_id = int(query.data.split("_")[2])
            await self._remove_moderator(query, mod_id)
        elif query.data.startswith("remove_channel_"):
            channel_id = query.data.split("_")[2]
            await self._remove_channel(query, channel_id)

    async def _show_moderators_menu(self, query):
        moderators = self.db.get_moderators()
        text = "👥 *Current Moderators*:\n\n"
        
        keyboard = []
        for mod_id, mod_username in moderators:
            text += f"• @{mod_username}\n"
            keyboard.append([InlineKeyboardButton(
                f"❌ Remove @{mod_username}", 
                callback_data=f"remove_mod_{mod_id}"
            )])
        
        if len(moderators) < 3:
            text += "\nTo add a new moderator, use:\n`/addmod @username`"
        
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="admin_panel")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def _show_channels_menu(self, query):
        channels = self.db.get_required_channels()
        text = "📢 *Required Subscription Channels*:\n\n"
        
        keyboard = []
        for channel_id, channel_username in channels:
            text += f"• @{channel_username}\n"
            keyboard.append([InlineKeyboardButton(
                f"❌ Remove @{channel_username}", 
                callback_data=f"remove_channel_{channel_id}"
            )])
        
        if len(channels) < 10:
            text += "\nTo add a new channel, use:\n`/addchannel @username`"
        
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="admin_panel")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def _show_statistics(self, query):
        stats = self.db.get_statistics()
        text = "📊 *Bot Statistics*\n\n"
        text += f"👥 Total Users: {stats['total_users']}\n"
        text += f"🔐 Total Passwords Generated: {stats['total_passwords']}\n"
        text += f"📅 Active Today: {stats['active_today']}\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def _remove_moderator(self, query, mod_id):
        if not await self.config.is_admin(query.from_user.id):
            await query.answer("⛔️ Only the owner can remove moderators.", show_alert=True)
            return
            
        self.db.remove_moderator(mod_id)
        await self._show_moderators_menu(query)

    async def _remove_channel(self, query, channel_id):
        self.db.remove_required_channel(channel_id)
        await self._show_channels_menu(query)