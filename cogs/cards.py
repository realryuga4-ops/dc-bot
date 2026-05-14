"""Cards cog for card inventory and management.

Includes: card viewing, inventory management, and card statistics.
"""

import discord
from discord.ext import commands
from discord import app_commands
from core import log, create_embed, create_rarity_embed, format_number
from core.database import db
from config import config


class Cards(commands.Cog):
    """Card inventory and management commands."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(name="inventory", help="View your card inventory")
    async def inventory(self, ctx: commands.Context, user: discord.User = None):
        """Display user card inventory."""
        user = user or ctx.author
        
        # Get user inventory
        inventory = await db.get_inventory(user.id, limit=10)
        
        embed = create_embed(
            title=f"🎴 Inventory: {user.name}",
            description=f"Showing {len(inventory)} cards",
            color=discord.Color.purple(),
            thumbnail_url=user.display_avatar.url
        )
        
        if not inventory:
            embed.description = "No cards in inventory yet. Use `!drop` to get cards!"
            await ctx.send(embed=embed)
            return
        
        # Add cards to embed
        for idx, item in enumerate(inventory, 1):
            card_data = item.get('card_data', {})
            card_name = card_data.get('name', 'Unknown')
            rarity = card_data.get('rarity', 'common')
            
            rarity_emoji = {"common": "⚪", "rare": "🔵", "epic": "🟣", "legendary": "🟡"}
            emoji = rarity_emoji.get(rarity, "❓")
            
            embed.add_field(
                name=f"{idx}. {emoji} {card_name}",
                value=f"Rarity: **{rarity.capitalize()}**",
                inline=True
            )
        
        await ctx.send(embed=embed)
        log.debug(f"Inventory command used by {ctx.author} for {user}")
    
    @commands.command(name="card", help="View a specific card")
    async def card(self, ctx: commands.Context, card_id: str = None):
        """Display detailed card information."""
        if not card_id:
            embed = create_embed(
                title="❌ Error",
                description="Please provide a card ID.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        # Get card from database
        card = await db.get_card(card_id)
        
        if not card:
            embed = create_embed(
                title="❌ Card Not Found",
                description=f"Card with ID `{card_id}` not found.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        # Display card
        rarity = card.get('rarity', 'common')
        embed = create_rarity_embed(
            title=f"🎴 {card.get('name', 'Unknown')}",
            description=f"Card ID: `{card_id}`",
            rarity=rarity
        )
        
        embed.add_field(name="Rarity", value=rarity.capitalize(), inline=True)
        if card.get('created_at'):
            embed.add_field(name="Created", value=f"<t:{int(card['created_at'].timestamp())}:R>", inline=True)
        
        await ctx.send(embed=embed)
        log.debug(f"Card command used by {ctx.author}")
    
    # ==================== SLASH COMMANDS ====================
    
    @app_commands.command(name="inventory", description="View your card inventory")
    async def slash_inventory(self, interaction: discord.Interaction, user: discord.User = None):
        """Display user card inventory using slash command."""
        user = user or interaction.user
        
        # Get user inventory
        inventory = await db.get_inventory(user.id, limit=10)
        
        embed = create_embed(
            title=f"🎴 Inventory: {user.name}",
            description=f"Showing {len(inventory)} cards",
            color=discord.Color.purple(),
            thumbnail_url=user.display_avatar.url
        )
        
        if not inventory:
            embed.description = "No cards in inventory yet. Use `/drop` to get cards!"
            await interaction.response.send_message(embed=embed)
            return
        
        # Add cards to embed
        for idx, item in enumerate(inventory, 1):
            card_data = item.get('card_data', {})
            card_name = card_data.get('name', 'Unknown')
            rarity = card_data.get('rarity', 'common')
            
            rarity_emoji = {"common": "⚪", "rare": "🔵", "epic": "🟣", "legendary": "🟡"}
            emoji = rarity_emoji.get(rarity, "❓")
            
            embed.add_field(
                name=f"{idx}. {emoji} {card_name}",
                value=f"Rarity: **{rarity.capitalize()}**",
                inline=True
            )
        
        await interaction.response.send_message(embed=embed)
        log.debug(f"Slash inventory used by {interaction.user}")


async def setup(bot: commands.Bot):
    """Load the cog."""
    await bot.add_cog(Cards(bot))
    log.debug("📥 Cards cog loaded")
