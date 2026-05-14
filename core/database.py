"""Database module for MongoDB connection and operations.

Handles async database operations for users, inventory, cards, and drops.
"""

import motor.motor_asyncio
from pymongo import ASCENDING, DESCENDING
from typing import Optional, Dict, Any, List
from config import config
from .logger import log


class Database:
    """MongoDB database handler with async support."""
    
    def __init__(self):
        self.client: Optional[motor.motor_asyncio.AsyncClient] = None
        self.db = None
        
    async def connect(self) -> bool:
        """Connect to MongoDB.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.client = motor.motor_asyncio.AsyncClient(config.MONGODB_URI)
            self.db = self.client[config.DATABASE_NAME]
            
            # Verify connection
            await self.client.admin.command('ping')
            log.info("✅ Connected to MongoDB")
            
            # Create indexes
            await self._create_indexes()
            return True
            
        except Exception as e:
            log.error(f"❌ Failed to connect to MongoDB: {e}")
            return False
    
    async def close(self):
        """Close database connection."""
        if self.client:
            self.client.close()
            log.info("🔌 MongoDB connection closed")
    
    async def _create_indexes(self):
        """Create database indexes for optimal performance."""
        try:
            # Users collection
            await self.db.users.create_index("user_id", unique=True)
            await self.db.users.create_index("username")
            
            # Inventory collection
            await self.db.inventory.create_index([("user_id", ASCENDING), ("card_id", ASCENDING)], unique=True)
            
            # Cards collection
            await self.db.cards.create_index("card_id", unique=True)
            
            # Drops collection
            await self.db.drops.create_index("created_at")
            
            log.debug("📊 Database indexes created")
        except Exception as e:
            log.warning(f"⚠️ Index creation warning: {e}")
    
    # ==================== USER OPERATIONS ====================
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user profile.
        
        Args:
            user_id: Discord user ID
            
        Returns:
            User document or None
        """
        return await self.db.users.find_one({"user_id": user_id})
    
    async def create_user(self, user_id: int, username: str) -> Dict[str, Any]:
        """Create new user profile.
        
        Args:
            user_id: Discord user ID
            username: Discord username
            
        Returns:
            Created user document
        """
        user_data = {
            "user_id": user_id,
            "username": username,
            "balance": config.STARTING_BALANCE,
            "cards_count": 0,
            "last_daily": None,
            "created_at": None,
            "updated_at": None,
        }
        await self.db.users.insert_one(user_data)
        return user_data
    
    async def get_or_create_user(self, user_id: int, username: str) -> Dict[str, Any]:
        """Get user or create if doesn't exist.
        
        Args:
            user_id: Discord user ID
            username: Discord username
            
        Returns:
            User document
        """
        user = await self.get_user(user_id)
        if not user:
            user = await self.create_user(user_id, username)
        return user
    
    async def update_user(self, user_id: int, update_data: Dict[str, Any]) -> bool:
        """Update user profile.
        
        Args:
            user_id: Discord user ID
            update_data: Data to update
            
        Returns:
            True if successful
        """
        result = await self.db.users.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def add_balance(self, user_id: int, amount: int) -> bool:
        """Add money to user balance.
        
        Args:
            user_id: Discord user ID
            amount: Amount to add
            
        Returns:
            True if successful
        """
        result = await self.db.users.update_one(
            {"user_id": user_id},
            {"$inc": {"balance": amount}}
        )
        return result.modified_count > 0
    
    async def remove_balance(self, user_id: int, amount: int) -> bool:
        """Remove money from user balance.
        
        Args:
            user_id: Discord user ID
            amount: Amount to remove
            
        Returns:
            True if successful
        """
        return await self.add_balance(user_id, -amount)
    
    # ==================== INVENTORY OPERATIONS ====================
    
    async def add_to_inventory(self, user_id: int, card_id: str, card_data: Dict[str, Any]) -> bool:
        """Add card to user inventory.
        
        Args:
            user_id: Discord user ID
            card_id: Unique card ID
            card_data: Card information
            
        Returns:
            True if successful
        """
        inventory_item = {
            "user_id": user_id,
            "card_id": card_id,
            "card_data": card_data,
            "obtained_at": None,
        }
        try:
            await self.db.inventory.insert_one(inventory_item)
            await self.db.users.update_one(
                {"user_id": user_id},
                {"$inc": {"cards_count": 1}}
            )
            return True
        except Exception as e:
            log.error(f"Error adding to inventory: {e}")
            return False
    
    async def get_inventory(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user inventory cards.
        
        Args:
            user_id: Discord user ID
            limit: Number of cards to return
            
        Returns:
            List of inventory items
        """
        return await self.db.inventory.find(
            {"user_id": user_id}
        ).limit(limit).to_list(limit)
    
    # ==================== CARD OPERATIONS ====================
    
    async def save_card(self, card_id: str, card_data: Dict[str, Any]) -> bool:
        """Save card data to database.
        
        Args:
            card_id: Unique card ID
            card_data: Card information
            
        Returns:
            True if successful
        """
        try:
            await self.db.cards.insert_one({
                "card_id": card_id,
                **card_data
            })
            return True
        except Exception as e:
            log.error(f"Error saving card: {e}")
            return False
    
    async def get_card(self, card_id: str) -> Optional[Dict[str, Any]]:
        """Get card data.
        
        Args:
            card_id: Unique card ID
            
        Returns:
            Card document or None
        """
        return await self.db.cards.find_one({"card_id": card_id})
    
    # ==================== DROP OPERATIONS ====================
    
    async def create_drop(self, drop_data: Dict[str, Any]) -> bool:
        """Create a new drop.
        
        Args:
            drop_data: Drop information
            
        Returns:
            True if successful
        """
        try:
            await self.db.drops.insert_one(drop_data)
            return True
        except Exception as e:
            log.error(f"Error creating drop: {e}")
            return False
    
    async def update_drop(self, drop_id: str, update_data: Dict[str, Any]) -> bool:
        """Update drop data.
        
        Args:
            drop_id: Drop ID
            update_data: Data to update
            
        Returns:
            True if successful
        """
        result = await self.db.drops.update_one(
            {"_id": drop_id},
            {"$set": update_data}
        )
        return result.modified_count > 0


# Global database instance
db = Database()
