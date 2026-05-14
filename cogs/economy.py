"""Economy cog for user profiles and balance management.

Includes: profile, balance, daily reward, and economy commands.
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from core import log, create_embed, create_success_embed, create_error_embed, format_number
from core.database import db
from core.helpers import check_cooldown, format_time_remaining
from config import config


class Economy(commands.Cog):
    """Economy and user profile commands."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(name="profile", help="View your profile")
    async def profile(self, ctx: commands.Context, user: discord.User = None):
        """Display user profile."""
        user = user or ctx.author
        
        # Get or create user
        user_data = await db.get_or_create_user(user.id, user.name)
        
        embed = create_embed(
            title=f"👤 Profile: {user.name}",
            description=f"User ID: `{user.id}`",
            color=discord.Color.gold(),
            thumbnail_url=user.display_avatar.url
        )
        
        embed.add_field(
            name="💰 Balance",
            value=f"**${format_number(user_data.get('balance', 0))}**",
            inline=True
        )
        embed.add_field(
            name="🎴 Cards",
            value=f"**{format_number(user_data.get('cards_count', 0))}**",
            inline=True
        )
        embed.add_field(name="_", value="_", inline=True)
        
        await ctx.send(embed=embed)
        log.debug(f"Profile command used by {ctx.author} for {user}")
    
    @commands.command(name="balance", help="Check your balance")
    async def balance(self, ctx: commands.Context, user: discord.User = None):
        """Check user balance."""
        user = user or ctx.author
        
        # Get or create user
        user_data = await db.get_or_create_user(user.id, user.name)
        balance = user_data.get('balance', 0)
        
        embed = create_success_embed(
            title=f"💰 Balance",
            description=f"{user.mention} has **${format_number(balance)}**"
        )
        
        await ctx.send(embed=embed)
        log.debug(f"Balance command used by {ctx.author}")
    
    @commands.command(name="daily", help="Claim your daily reward")
    @commands.cooldown(1, 86400, commands.BucketType.user)  # 24 hour cooldown
    async def daily(self, ctx: commands.Context):
        """Claim daily reward."""
        user_data = await db.get_or_create_user(ctx.author.id, ctx.author.name)
        
        # Add daily reward
        await db.add_balance(ctx.author.id, config.DAILY_REWARD)
        
        new_balance = user_data.get('balance', 0) + config.DAILY_REWARD
        
        embed = create_success_embed(
            title="Daily Reward! 🎁",
            description=f"You claimed **${format_number(config.DAILY_REWARD)}**!\n\nNew balance: **${format_number(new_balance)}**"
        )
        
        await ctx.send(embed=embed)
        log.info(f"{ctx.author} claimed daily reward")
    
    # ==================== SLASH COMMANDS ====================
    
    @app_commands.command(name="profile", description="View your profile")
    async def slash_profile(self, interaction: discord.Interaction, user: discord.User = None):
        """Display user profile using slash command."""
        user = user or interaction.user
        
        # Get or create user
        user_data = await db.get_or_create_user(user.id, user.name)
        
        embed = create_embed(
            title=f"👤 Profile: {user.name}",
            description=f"User ID: `{user.id}`",
            color=discord.Color.gold(),
            thumbnail_url=user.display_avatar.url
        )
        
        embed.add_field(
            name="💰 Balance",
            value=f"**${format_number(user_data.get('balance', 0))}**",
            inline=True
        )
        embed.add_field(
            name="🎴 Cards",
            value=f"**{format_number(user_data.get('cards_count', 0))}**",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
        log.debug(f"Slash profile used by {interaction.user}")
    
    @app_commands.command(name="balance", description="Check your balance")
    async def slash_balance(self, interaction: discord.Interaction, user: discord.User = None):
        """Check user balance using slash command."""
        user = user or interaction.user
        
        # Get or create user
        user_data = await db.get_or_create_user(user.id, user.name)
        balance = user_data.get('balance', 0)
        
        embed = create_success_embed(
            title="💰 Balance",
            description=f"{user.mention} has **${format_number(balance)}**"
        )
        
        await interaction.response.send_message(embed=embed)
        log.debug(f"Slash balance used by {interaction.user}")


async def setup(bot: commands.Bot):
    """Load the cog."""
    await bot.add_cog(Economy(bot))
    log.debug("📥 Economy cog loaded")
