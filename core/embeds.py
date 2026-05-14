"""Discord embed creation utilities.

Provides functions to create styled embeds for different purposes.
"""

import discord
from datetime import datetime
from config import config
from typing import Optional


def create_embed(
    title: str = "",
    description: str = "",
    color: int = discord.Color.blue(),
    footer_text: str = "dc-bot",
    thumbnail_url: Optional[str] = None,
    image_url: Optional[str] = None,
    author_name: Optional[str] = None,
    author_icon: Optional[str] = None,
) -> discord.Embed:
    """Create a styled Discord embed.
    
    Args:
        title: Embed title
        description: Embed description
        color: Embed color
        footer_text: Footer text
        thumbnail_url: Thumbnail URL
        image_url: Image URL
        author_name: Author name
        author_icon: Author icon URL
        
    Returns:
        discord.Embed object
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow()
    )
    
    embed.set_footer(text=footer_text, icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
    
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    
    if image_url:
        embed.set_image(url=image_url)
    
    if author_name:
        embed.set_author(name=author_name, icon_url=author_icon)
    
    return embed


def create_error_embed(title: str = "Error", description: str = "") -> discord.Embed:
    """Create an error embed.
    
    Args:
        title: Error title
        description: Error description
        
    Returns:
        discord.Embed object
    """
    return create_embed(
        title=f"❌ {title}",
        description=description,
        color=discord.Color.red()
    )


def create_success_embed(title: str = "Success", description: str = "") -> discord.Embed:
    """Create a success embed.
    
    Args:
        title: Success title
        description: Success description
        
    Returns:
        discord.Embed object
    """
    return create_embed(
        title=f"✅ {title}",
        description=description,
        color=discord.Color.green()
    )


def create_rarity_embed(
    title: str,
    description: str,
    rarity: str = "common",
    **kwargs
) -> discord.Embed:
    """Create a rarity-colored embed.
    
    Args:
        title: Embed title
        description: Embed description
        rarity: Card rarity (common, rare, epic, legendary)
        **kwargs: Additional arguments for create_embed
        
    Returns:
        discord.Embed object
    """
    color = config.RARITY_COLORS.get(rarity.lower(), discord.Color.gray())
    return create_embed(
        title=title,
        description=description,
        color=color,
        **kwargs
    )
