from typing import List, Set
from database import Database

class Config:
    def __init__(self, db: Database, owner_id: int):
        self.db = db
        self.owner_id = owner_id
        
    async def is_admin(self, user_id: int) -> bool:
        """Check if user is the bot owner"""
        return user_id == self.owner_id
        
    async def is_admin_or_mod(self, user_id: int) -> bool:
        """Check if user is admin or moderator"""
        if await self.is_admin(user_id):
            return True
        return self.db.is_moderator(user_id)
        
    async def can_manage_channels(self, user_id: int) -> bool:
        """Check if user can manage required channels"""
        return await self.is_admin_or_mod(user_id)