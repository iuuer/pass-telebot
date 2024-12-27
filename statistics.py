from datetime import datetime, timedelta
from typing import Dict, List, Optional
from database import Database

class Statistics:
    def __init__(self, db: Database):
        self.db = db

    async def get_general_stats(self) -> Dict:
        """Get general statistics about users and groups"""
        stats = await self.db.get_general_stats()
        return {
            'total_users': stats['total_users'],
            'private_users': stats['private_users'],
            'channels_groups': stats['channels_groups'],
            'banned_users': stats['banned_users']
        }

    async def get_daily_stats(self, date: datetime) -> Dict:
        """Get statistics for a specific date"""
        stats = await self.db.get_daily_stats(date)
        return {
            'users': stats['users'],
            'groups': stats['groups'],
            'active_users': stats['active_users'],
            'subscriptions': stats['subscriptions'],
            'referrals': stats['referrals'],
            'messages': stats['messages']
        }

    async def get_user_growth_stats(self) -> Dict:
        """Get user growth statistics"""
        return await self.db.get_user_growth_stats()

    def format_stats_message(self) -> str:
        """Format statistics into a readable message"""
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        general_stats = self.get_general_stats()
        today_stats = self.get_daily_stats(today)
        yesterday_stats = self.get_daily_stats(yesterday)
        growth_stats = self.get_user_growth_stats()
        
        return f"""
📊 *Statistics Dashboard*

👥 *Users:*
• Total Users: {general_stats['total_users']}
• Private Users: {general_stats['private_users']}
• Channels & Groups: {general_stats['channels_groups']}
• Banned Users: {general_stats['banned_users']}

📈 *Today's Activity ({today.strftime('%Y-%m-%d')}):*
• Users: {today_stats['users']}
• Groups: {today_stats['groups']}
• Active Users: {today_stats['active_users']}
• New Subscriptions: {today_stats['subscriptions']}
• Referrals: {today_stats['referrals']}
• Messages: {today_stats['messages']}

📉 *Yesterday ({yesterday.strftime('%Y-%m-%d')}):*
• Users: {yesterday_stats['users']}
• Groups: {yesterday_stats['groups']}
• Active Users: {yesterday_stats['active_users']}
• New Subscriptions: {yesterday_stats['subscriptions']}
• Referrals: {yesterday_stats['referrals']}
• Messages: {yesterday_stats['messages']}

📊 *Growth:*
• New Users Today: {growth_stats['today_new']}
• New Users Yesterday: {growth_stats['yesterday_new']}
• New Users This Month: {growth_stats['month_new']}
• New Users Last Month: {growth_stats['last_month_new']}
"""