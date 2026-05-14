"""Events cog for handling bot events.

Handles on_ready, error events, and other bot-level events.
"""

import discord
from discord.ext import commands
from core import log
from config import config


class Events(commands.Cog):
    """Handle bot events."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Event fired when bot successfully connects to Discord."""
        log.info(f"🤖 Bot logged in as {self.bot.user.name}#{self.bot.user.discriminator}")
        log.info(f"📊 Serving {len(self.bot.guilds)} guilds with {len(self.bot.users)} users")
        log.info(f"🎴 Bot version: {config.BOT_VERSION}")
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Event fired when bot joins a guild."""
        log.info(f"✅ Joined guild: {guild.name} (ID: {guild.id})")
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        """Event fired when bot leaves a guild."""
        log.info(f"❌ Left guild: {guild.name} (ID: {guild.id})")
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """Global error handler for prefix commands."""
        from core import create_error_embed
        
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found
        
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = create_error_embed(
                title="Missing Argument",
                description=f"Missing required argument: `{error.param.name}`"
            )
            await ctx.send(embed=embed)
        
        elif isinstance(error, commands.MissingPermissions):
            embed = create_error_embed(
                title="Missing Permissions",
                description=f"You need {', '.join(error.missing_permissions)} permission(s) to use this command."
            )
            await ctx.send(embed=embed)
        
        elif isinstance(error, commands.BotMissingPermissions):
            embed = create_error_embed(
                title="Bot Missing Permissions",
                description=f"I need {', '.join(error.missing_permissions)} permission(s) to execute this command."
            )
            await ctx.send(embed=embed)
        
        elif isinstance(error, commands.CommandOnCooldown):
            embed = create_error_embed(
                title="Command on Cooldown",
                description=f"Please wait {error.retry_after:.1f} seconds before using this command again."
            )
            await ctx.send(embed=embed)
        
        else:
            log.error(f"Unhandled error in command {ctx.command}: {error}")
            embed = create_error_embed(
                title="Error",
                description="An unexpected error occurred. Please try again later."
            )
            await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    """Load the cog."""
    await bot.add_cog(Events(bot))
    log.debug("📥 Events cog loaded")
