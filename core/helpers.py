"""Helper functions for the bot.

Utility functions for common operations.
"""

import random
import string
from datetime import datetime, timedelta
from config import config
from typing import Optional


def format_number(num: int) -> str:
    """Format number with separators.
    
    Args:
        num: Number to format
        
    Returns:
        Formatted number string
    """
    return f"{num:,}"


def get_rarity_color(rarity: str) -> int:
    """Get color for rarity.
    
    Args:
        rarity: Rarity name
        
    Returns:
        Color hex value
    """
    return config.RARITY_COLORS.get(rarity.lower(), 0x95A5A6)


def generate_card_id() -> str:
    """Generate unique card ID.
    
    Returns:
        Unique card ID
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{timestamp}-{random_suffix}"


def get_rarity() -> str:
    """Generate random rarity for a card.
    
    Probabilities:
    - Common: 60%
    - Rare: 25%
    - Epic: 10%
    - Legendary: 5%
    
    Returns:
        Rarity string
    """
    rand = random.random()
    if rand < 0.60:
        return "common"
    elif rand < 0.85:
        return "rare"
    elif rand < 0.95:
        return "epic"
    else:
        return "legendary"


def check_cooldown(last_action: Optional[datetime], cooldown_hours: int) -> bool:
    """Check if cooldown has passed.
    
    Args:
        last_action: Last action timestamp
        cooldown_hours: Cooldown duration in hours
        
    Returns:
        True if cooldown has passed
    """
    if not last_action:
        return True
    
    elapsed = datetime.utcnow() - last_action
    return elapsed >= timedelta(hours=cooldown_hours)


def format_time_remaining(last_action: datetime, cooldown_hours: int) -> str:
    """Format remaining cooldown time.
    
    Args:
        last_action: Last action timestamp
        cooldown_hours: Cooldown duration in hours
        
    Returns:
        Formatted time string
    """
    cooldown_time = last_action + timedelta(hours=cooldown_hours)
    remaining = cooldown_time - datetime.utcnow()
    
    hours, remainder = divmod(int(remaining.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{hours}h {minutes}m {seconds}s"
