from typing import List, Optional
from telegram import Bot, InlineKeyboardMarkup
from database import Database

class Broadcaster:
    def __init__(self, bot: Bot, db: Database):
        self.bot = bot
        self.db = db

    async def broadcast_to_users(
        self,
        message: str,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        user_filter: Optional[dict] = None
    ) -> dict:
        """Broadcast message to users"""
        users = await self.db.get_users(user_filter)
        results = {
            'total': len(users),
            'success': 0,
            'failed': 0,
            'blocked': 0
        }
        
        for user_id in users:
            try:
                await self.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                results['success'] += 1
            except Exception as e:
                if 'blocked' in str(e).lower():
                    results['blocked'] += 1
                else:
                    results['failed'] += 1
                    
        return results

    async def pin_message(
        self,
        chat_id: int,
        message: str,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        notify: bool = False
    ) -> bool:
        """Pin a message in a chat"""
        try:
            message = await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            await self.bot.pin_chat_message(
                chat_id=chat_id,
                message_id=message.message_id,
                disable_notification=not notify
            )
            return True
        except:
            return False