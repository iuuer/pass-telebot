from datetime import datetime
from typing import Dict, Optional
from database import Database

class UserTracker:
    def __init__(self, db: Database):
        self.db = db

    async def track_user_activity(self, user_id: int, activity_type: str):
        """Track user activity"""
        await self.db.log_user_activity(user_id, activity_type)

    async def get_user_stats(self, user_id: int) -> Dict:
        """Get detailed statistics for a specific user"""
        user_data = await self.db.get_user_data(user_id)
        activities = await self.db.get_user_activities(user_id)
        
        return {
            'user_id': user_id,
            'phone': user_data.get('phone'),
            'username': user_data.get('username'),
            'first_seen': user_data.get('first_seen'),
            'account_created': user_data.get('created_at'),
            'last_activity': user_data.get('last_activity'),
            'total_activities': len(activities),
            'activity_breakdown': self._analyze_activities(activities)
        }

    def _analyze_activities(self, activities: List[Dict]) -> Dict:
        """Analyze user activities"""
        analysis = {
            'commands': 0,
            'messages': 0,
            'passwords_generated': 0,
            'settings_changed': 0
        }
        
        for activity in activities:
            activity_type = activity['type']
            analysis[activity_type] = analysis.get(activity_type, 0) + 1
            
        return analysis

    def format_user_stats(self, user_id: int) -> str:
        """Format user statistics into a readable message"""
        stats = self.get_user_stats(user_id)
        
        return f"""
👤 *User Statistics*

*Basic Information:*
• ID: `{stats['user_id']}`
• Phone: `{stats['phone'] or 'Not provided'}`
• Username: @{stats['username'] or 'None'}
• First Seen: {stats['first_seen'].strftime('%Y-%m-%d %H:%M:%S')}
• Account Created: {stats['account_created'].strftime('%Y-%m-%d %H:%M:%S')}
• Last Activity: {stats['last_activity'].strftime('%Y-%m-%d %H:%M:%S')}

*Activity Summary:*
• Total Activities: {stats['total_activities']}
• Commands Used: {stats['activity_breakdown']['commands']}
• Messages Sent: {stats['activity_breakdown']['messages']}
• Passwords Generated: {stats['activity_breakdown']['passwords_generated']}
• Settings Changes: {stats['activity_breakdown']['settings_changed']}
"""