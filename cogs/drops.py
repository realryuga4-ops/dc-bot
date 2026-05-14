"""Drops cog for card drop system.

Includes: random drops, claim buttons, and cooldown management.
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import random
import asyncio

from core import log, create_embed, create_rarity_embed, create_error_embed
from core.database import db
from core.helpers import get_rarity, generate_card_id
from config import config


class ClaimButton(discord.ui.Button):
    """Button to claim a card drop."""
    
    def __init__(self, card_id: str, card_name: str, rarity: str):
        super().__init__(style=discord.ButtonStyle.green, label="🎴 Claim Card", emoji="✨")
        self.card_id = card_id
        self.card_name = card_name
        self.rarity = rarity
    
    async def callback(self, interaction: discord.Interaction):
        """Handle card claim."""
        # Check if user already has the card
        existing_card = await db.db.inventory.find_one({
            "user_id": interaction.user.id,
            "card_id": self.card_id
        })
        
        if existing_card:
            embed = create_error_embed(
                title="Already Have This Card",
                description=f"You already have **{self.card_name}** in your inventory!"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Add card to inventory
        card_data = {
            "name": self.card_name,
            "rarity": self.rarity,
            "obtained_at": datetime.utcnow()
        }
        
        success = await db.add_to_inventory(interaction.user.id, self.card_id, card_data)
        
        if success:
            embed = create_rarity_embed(
                title="🎉 Card Claimed!",
                description=f"You claimed **{self.card_name}**!",
                rarity=self.rarity
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            log.info(f"{interaction.user} claimed card {self.card_name}")
        else:
            embed = create_error_embed(
                title="Claim Failed",
                description="Failed to claim card. Try again."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


class DropView(discord.ui.View):
    """View for drop buttons."""
    
    def __init__(self, card_id: str, card_name: str, rarity: str):
        super().__init__(timeout=config.DROP_CLAIM_TIMEOUT)
        self.add_item(ClaimButton(card_id, card_name, rarity))
    
    async def on_timeout(self):
        """Called when view times out."""
        log.debug("Drop claim view timed out")


class Drops(commands.Cog):
    """Card drop system."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.drops_active = {}  # Track active drops per channel
    
    @commands.command(name="drop", help="Trigger a random card drop")
    @commands.cooldown(1, config.DROP_COOLDOWN_MINUTES * 60, commands.BucketType.channel)
    async def drop(self, ctx: commands.Context):
        """Trigger a random card drop in the channel."""
        # Prevent duplicate drops in same channel
        if ctx.channel.id in self.drops_active:
            await ctx.send("⚠️ There's already an active drop in this channel!")
            return
        
        # Generate random card
        rarity = get_rarity()
        card_id = generate_card_id()
        card_names = {
            "common": ["Kirito", "Asuna", "Rem", "Emilia", "Saber", "Rin"],
            "rare": ["Aqua", "Darkness", "Megumin", "Spike", "Faye", "Jet"],
            "epic": ["Saitama", "Genos", "Tatsumaki", "Boros", "Bang", "Blast"],
            "legendary": ["Goku", "Vegeta", "Naruto", "Sasuke", "Ichigo", "Aizen"],
        }
        
        card_name = random.choice(card_names.get(rarity, ["Mystery Card"]))
        
        # Save card to database
        card_data = {
            "name": card_name,
            "rarity": rarity,
            "created_at": datetime.utcnow()
        }
        await db.save_card(card_id, card_data)
        
        # Create drop message
        rarity_emoji = {"common": "⚪", "rare": "🔵", "epic": "🟣", "legendary": "🟡"}
        embed = create_rarity_embed(
            title=f"{rarity_emoji.get(rarity, '❓')} {rarity.upper()} CARD DROP!",
            description=f"A wild **{card_name}** appeared!\n\nClick the button below to claim it!",
            rarity=rarity
        )
        
        # Send drop message with button
        view = DropView(card_id, card_name, rarity)
        message = await ctx.send(embed=embed, view=view)
        
        # Mark drop as active
        self.drops_active[ctx.channel.id] = True
        log.info(f"Drop triggered in {ctx.guild.name}: {card_name} ({rarity})")
        
        # Remove from active after timeout
        await asyncio.sleep(config.DROP_CLAIM_TIMEOUT)
        if ctx.channel.id in self.drops_active:
            del self.drops_active[ctx.channel.id]
    
    # ==================== SLASH COMMANDS ====================
    
    @app_commands.command(name="drop", description="Trigger a random card drop")
    async def slash_drop(self, interaction: discord.Interaction):
        """Trigger a random card drop using slash command."""
        # Prevent duplicate drops in same channel
        if interaction.channel.id in self.drops_active:
            embed = create_error_embed(
                title="Active Drop",
                description="There's already an active drop in this channel!"
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # Generate random card
        rarity = get_rarity()
        card_id = generate_card_id()
        card_names = {
            "common": ["Kirito", "Asuna", "Rem", "Emilia", "Saber", "Rin"],
            "rare": ["Aqua", "Darkness", "Megumin", "Spike", "Faye", "Jet"],
            "epic": ["Saitama", "Genos", "Tatsumaki", "Boros", "Bang", "Blast"],
            "legendary": ["Goku", "Vegeta", "Naruto", "Sasuke", "Ichigo", "Aizen"],
        }
        
        card_name = random.choice(card_names.get(rarity, ["Mystery Card"]))
        
        # Save card to database
        card_data = {
            "name": card_name,
            "rarity": rarity,
            "created_at": datetime.utcnow()
        }
        await db.save_card(card_id, card_data)
        
        # Create drop message
        rarity_emoji = {"common": "⚪", "rare": "🔵", "epic": "🟣", "legendary": "🟡"}
        embed = create_rarity_embed(
            title=f"{rarity_emoji.get(rarity, '❓')} {rarity.upper()} CARD DROP!",
            description=f"A wild **{card_name}** appeared!\n\nClick the button below to claim it!",
            rarity=rarity
        )
        
        # Send drop message with button
        view = DropView(card_id, card_name, rarity)
        await interaction.response.send_message(embed=embed, view=view)
        
        # Mark drop as active
        self.drops_active[interaction.channel.id] = True
        log.info(f"Slash drop triggered in {interaction.guild.name}: {card_name} ({rarity})")
        
        # Remove from active after timeout
        await asyncio.sleep(config.DROP_CLAIM_TIMEOUT)
        if interaction.channel.id in self.drops_active:
            del self.drops_active[interaction.channel.id]


async def setup(bot: commands.Bot):
    """Load the cog."""
    await bot.add_cog(Drops(bot))
    log.debug("📥 Drops cog loaded")
