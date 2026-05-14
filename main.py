"""Main bot file - Discord bot entry point.

Handles bot initialization, command loading, and status rotation.
"""

import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime

from config import config, Config
from core import log
from core.database import db


class DiscordBot(commands.Bot):
    """Custom Discord bot class with extended functionality."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=config.BOT_PREFIX,
            intents=intents,
            help_command=None,  # We have custom help
            application_id=None,
        )
        
        self.start_time = datetime.utcnow()
    
    async def setup_hook(self) -> None:
        """Called before the bot connects to Discord."""
        log.info("🔄 Setting up bot...")
        
        # Connect to database
        db_connected = await db.connect()
        if not db_connected:
            log.error("Failed to connect to database. Exiting.")
            await self.close()
            return
        
        # Load all cogs
        await self.load_cogs()
        
        # Start status rotation
        self.rotate_status.start()
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            log.info(f"✅ Synced {len(synced)} slash command(s)")
        except Exception as e:
            log.error(f"Failed to sync commands: {e}")
    
    async def load_cogs(self) -> None:
        """Load all cogs from cogs directory."""
        from cogs import Events, Utility, Fun, Economy, Drops, Cards
        
        cogs_to_load = [Events, Utility, Fun, Economy, Drops, Cards]
        
        for cog_class in cogs_to_load:
            try:
                cog_name = cog_class.__name__
                await self.add_cog(cog_class(self))
                log.info(f"✅ Loaded cog: {cog_name}")
            except Exception as e:
                log.error(f"❌ Failed to load cog {cog_class.__name__}: {e}")
    
    @tasks.loop(minutes=5)
    async def rotate_status(self) -> None:
        """Rotate bot status every 5 minutes."""
        import random
        
        status = random.choice(config.BOT_STATUSES)
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=status
        )
        
        await self.change_presence(activity=activity)
    
    async def on_ready(self) -> None:
        """Called when bot is ready."""
        log.info(f"✅ Bot is ready! Logged in as {self.user}")
        log.info(f"📊 Serving {len(self.guilds)} guilds")
    
    async def close(self) -> None:
        """Close bot and cleanup."""
        log.info("🔌 Closing bot...")
        await db.close()
        await super().close()


async def main():
    """Main function to run the bot."""
    # Validate configuration
    if not Config.validate():
        log.error("❌ Configuration validation failed!")
        return
    
    log.info(f"🚀 Starting Discord Bot v{config.BOT_VERSION}")
    log.info(f"📝 Environment: {config.ENVIRONMENT}")
    log.info(f"🔧 Prefix: {config.BOT_PREFIX}")
    
    # Create and run bot
    bot = DiscordBot()
    
    try:
        await bot.start(config.DISCORD_TOKEN)
    except discord.errors.LoginFailure:
        log.error("❌ Invalid Discord token. Check your .env file.")
    except KeyboardInterrupt:
        log.info("⚠️ Bot interrupted by user")
    except Exception as e:
        log.error(f"❌ Fatal error: {e}")
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
