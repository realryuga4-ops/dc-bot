"""Fun cog containing entertaining commands.

Includes: stats, uptime, and other fun commands.
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from core import log, create_embed, format_number
from core.database import db


class Fun(commands.Cog):
    """Fun and entertainment commands."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.utcnow()
    
    @commands.command(name="stats", help="Display bot statistics")
    async def stats(self, ctx: commands.Context):
        """Display bot statistics."""
        total_users = len(self.bot.users)
        total_guilds = len(self.bot.guilds)
        
        embed = create_embed(
            title="📊 Bot Statistics",
            description="",
            color=discord.Color.blurple()
        )
        
        embed.add_field(name="Guilds", value=format_number(total_guilds), inline=True)
        embed.add_field(name="Users", value=format_number(total_users), inline=True)
        embed.add_field(name="Channels", value=format_number(sum(len(g.channels) for g in self.bot.guilds)), inline=True)
        
        uptime = datetime.utcnow() - self.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        embed.add_field(name="Uptime", value=f"{hours}h {minutes}m {seconds}s", inline=True)
        
        embed.add_field(name="Latency", value=f"{self.bot.latency*1000:.2f}ms", inline=True)
        
        await ctx.send(embed=embed)
        log.debug(f"Stats command used by {ctx.author}")
    
    @commands.command(name="uptime", help="Show bot uptime")
    async def uptime(self, ctx: commands.Context):
        """Display bot uptime."""
        uptime = datetime.utcnow() - self.start_time
        
        days, remainder = divmod(int(uptime.total_seconds()), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
        
        embed = create_embed(
            title="⏱️ Bot Uptime",
            description=f"**{uptime_str}**",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)
        log.debug(f"Uptime command used by {ctx.author}")


async def setup(bot: commands.Bot):
    """Load the cog."""
    await bot.add_cog(Fun(bot))
    log.debug("📥 Fun cog loaded")
