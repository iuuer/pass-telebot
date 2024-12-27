import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class Database:
    def __init__(self, db_file: str = "bot_data.db"):
        self.db_file = db_file
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # User tracking tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_stats (
                    user_id INTEGER PRIMARY KEY,
                    phone TEXT,
                    username TEXT,
                    first_seen TIMESTAMP,
                    created_at TIMESTAMP,
                    last_activity TIMESTAMP,
                    is_banned BOOLEAN DEFAULT FALSE,
                    chat_type TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    activity_type TEXT,
                    timestamp TIMESTAMP,
                    details TEXT,
                    FOREIGN KEY (user_id) REFERENCES user_stats (user_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    date DATE PRIMARY KEY,
                    new_users INTEGER DEFAULT 0,
                    active_users INTEGER DEFAULT 0,
                    messages_count INTEGER DEFAULT 0,
                    subscriptions INTEGER DEFAULT 0,
                    referrals INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()

    async def get_general_stats(self) -> Dict:
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Get total users
            cursor.execute('SELECT COUNT(*) FROM user_stats')
            total_users = cursor.fetchone()[0]
            
            # Get private users
            cursor.execute('SELECT COUNT(*) FROM user_stats WHERE chat_type = "private"')
            private_users = cursor.fetchone()[0]
            
            # Get channels and groups
            cursor.execute('SELECT COUNT(*) FROM user_stats WHERE chat_type IN ("channel", "group")')
            channels_groups = cursor.fetchone()[0]
            
            # Get banned users
            cursor.execute('SELECT COUNT(*) FROM user_stats WHERE is_banned = TRUE')
            banned_users = cursor.fetchone()[0]
            
            return {
                'total_users': total_users,
                'private_users': private_users,
                'channels_groups': channels_groups,
                'banned_users': banned_users
            }

    async def get_daily_stats(self, date: datetime) -> Dict:
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM daily_stats WHERE date = ?
            ''', (date.date(),))
            
            row = cursor.fetchone()
            if row:
                return {
                    'users': row[1],
                    'groups': row[2],
                    'active_users': row[3],
                    'subscriptions': row[4],
                    'referrals': row[5],
                    'messages': row[6]
                }
            return {
                'users': 0,
                'groups': 0,
                'active_users': 0,
                'subscriptions': 0,
                'referrals': 0,
                'messages': 0
            }

    async def get_user_growth_stats(self) -> Dict:
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        month_start = today.replace(day=1)
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)
        
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Today's new users
            cursor.execute('''
                SELECT COUNT(*) FROM user_stats 
                WHERE date(first_seen) = ?
            ''', (today.date(),))
            today_new = cursor.fetchone()[0]
            
            # Yesterday's new users
            cursor.execute('''
                SELECT COUNT(*) FROM user_stats 
                WHERE date(first_seen) = ?
            ''', (yesterday.date(),))
            yesterday_new = cursor.fetchone()[0]
            
            # This month's new users
            cursor.execute('''
                SELECT COUNT(*) FROM user_stats 
                WHERE first_seen >= ?
            ''', (month_start,))
            month_new = cursor.fetchone()[0]
            
            # Last month's new users
            cursor.execute('''
                SELECT COUNT(*) FROM user_stats 
                WHERE first_seen >= ? AND first_seen < ?
            ''', (last_month_start, month_start))
            last_month_new = cursor.fetchone()[0]
            
            return {
                'today_new': today_new,
                'yesterday_new': yesterday_new,
                'month_new': month_new,
                'last_month_new': last_month_new
            }

    async def log_user_activity(self, user_id: int, activity_type: str, details: str = None):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Update last activity
            cursor.execute('''
                UPDATE user_stats 
                SET last_activity = ? 
                WHERE user_id = ?
            ''', (datetime.now(), user_id))
            
            # Log activity
            cursor.execute('''
                INSERT INTO user_activities 
                (user_id, activity_type, timestamp, details)
                VALUES (?, ?, ?, ?)
            ''', (user_id, activity_type, datetime.now(), details))
            
            conn.commit()

    async def get_user_data(self, user_id: int) -> Dict:
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM user_stats WHERE user_id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'user_id': row[0],
                    'phone': row[1],
                    'username': row[2],
                    'first_seen': row[3],
                    'created_at': row[4],
                    'last_activity': row[5],
                    'is_banned': row[6],
                    'chat_type': row[7]
                }
            return None

    async def get_user_activities(self, user_id: int) -> List[Dict]:
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM user_activities 
                WHERE user_id = ?
                ORDER BY timestamp DESC
            ''', (user_id,))
            
            activities = []
            for row in cursor.fetchall():
                activities.append({
                    'id': row[0],
                    'user_id': row[1],
                    'type': row[2],
                    'timestamp': row[3],
                    'details': row[4]
                })
            return activities