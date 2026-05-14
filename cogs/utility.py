"""Utility cog containing basic bot commands.

Includes: ping, help, about, and info commands.
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from core import log, create_embed, create_success_embed
from config import config


class Utility(commands.Cog):
    """Utility and info commands."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.utcnow()
    
    # ==================== PREFIX COMMANDS ====================
    
    @commands.command(name="ping", help="Check bot latency")
    async def ping(self, ctx: commands.Context):
        """Check bot latency and response time."""
        embed = create_success_embed(
            title="Pong! 🏓",
            description=f"Latency: **{self.bot.latency*1000:.2f}ms**"
        )
        await ctx.send(embed=embed)
        log.debug(f"Ping command used by {ctx.author}")
    
    @commands.command(name="help", help="Display help information")
    async def help_command(self, ctx: commands.Context, command: str = None):
        """Display help information for commands."""
        if command:
            cmd = self.bot.get_command(command)
            if not cmd:
                embed = create_embed(
                    title="❓ Command Not Found",
                    description=f"Could not find command `{command}`",
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed)
                return
            
            embed = create_embed(
                title=f"Help: {cmd.name}",
                description=cmd.help or "No description available",
                color=discord.Color.blue()
            )
            if cmd.usage:
                embed.add_field(name="Usage", value=f"`{config.BOT_PREFIX}{cmd.usage}`", inline=False)
            await ctx.send(embed=embed)
        else:
            # General help
            embed = create_embed(
                title="📚 Help Menu",
                description=f"Use `{config.BOT_PREFIX}help [command]` for more info\n\n",
                color=discord.Color.blue()
            )
            
            cogs_data = {}
            for cog_name, cog in self.bot.cogs.items():
                commands_list = cog.get_commands()
                if commands_list:
                    cogs_data[cog_name] = [cmd.name for cmd in commands_list]
            
            for cog_name, cmds in cogs_data.items():
                if cmds:
                    embed.add_field(
                        name=f"📌 {cog_name}",
                        value="\n".join([f"`{config.BOT_PREFIX}{cmd}`" for cmd in cmds]),
                        inline=False
                    )
            
            embed.add_field(
                name="🔗 Useful Links",
                value="[Invite Bot](https://discord.com/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=8&scope=bot%20applications.commands) | [Support Server](https://discord.gg/yourserver)",
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        log.debug(f"Help command used by {ctx.author}")
    
    @commands.command(name="about", help="Show bot information")
    async def about(self, ctx: commands.Context):
        """Display bot information."""
        embed = create_embed(
            title="About dc-bot 🎴",
            description="A professional anime card Discord bot with economy system and card drops.",
            color=discord.Color.purple()
        )
        
        embed.add_field(name="Version", value=config.BOT_VERSION, inline=True)
        embed.add_field(name="Prefix", value=f"`{config.BOT_PREFIX}`", inline=True)
        embed.add_field(name="Python", value="3.10+", inline=True)
        embed.add_field(name="Library", value="discord.py 2.4.0+", inline=True)
        
        uptime = datetime.utcnow() - self.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes = remainder // 60
        embed.add_field(name="Uptime", value=f"{hours}h {minutes}m", inline=True)
        
        embed.add_field(name="Guilds", value=str(len(self.bot.guilds)), inline=True)
        
        await ctx.send(embed=embed)
        log.debug(f"About command used by {ctx.author}")
    
    @commands.command(name="userinfo", help="Get user information")
    async def userinfo(self, ctx: commands.Context, user: discord.User = None):
        """Get information about a user."""
        user = user or ctx.author
        
        embed = create_embed(
            title=f"User Info: {user}",
            description=f"ID: `{user.id}`",
            color=discord.Color.blue(),
            thumbnail_url=user.display_avatar.url
        )
        
        embed.add_field(name="Bot", value="✅ Yes" if user.bot else "❌ No", inline=True)
        embed.add_field(name="Verified", value="✅ Yes" if user.verified else "❌ No", inline=True)
        embed.add_field(name="Created", value=f"<t:{int(user.created_at.timestamp())}:R>", inline=True)
        
        await ctx.send(embed=embed)
        log.debug(f"Userinfo command used for {user}")
    
    @commands.command(name="avatar", help="Display user's avatar")
    async def avatar(self, ctx: commands.Context, user: discord.User = None):
        """Display a user's avatar."""
        user = user or ctx.author
        
        embed = create_embed(
            title=f"{user.name}'s Avatar",
            color=discord.Color.blue()
        )
        embed.set_image(url=user.display_avatar.url)
        
        await ctx.send(embed=embed)
        log.debug(f"Avatar command used for {user}")
    
    # ==================== SLASH COMMANDS ====================
    
    @app_commands.command(name="ping", description="Check bot latency")
    async def slash_ping(self, interaction: discord.Interaction):
        """Check bot latency using slash command."""
        embed = create_success_embed(
            title="Pong! 🏓",
            description=f"Latency: **{self.bot.latency*1000:.2f}ms**"
        )
        await interaction.response.send_message(embed=embed)
        log.debug(f"Slash ping used by {interaction.user}")
    
    @app_commands.command(name="help", description="Display help information")
    async def slash_help(self, interaction: discord.Interaction, command: str = None):
        """Display help information using slash command."""
        embed = create_embed(
            title="📚 Help Menu",
            description="Use `/help [command]` for more info\n\n",
            color=discord.Color.blue()
        )
        
        cogs_data = {}
        for cog_name, cog in self.bot.cogs.items():
            commands_list = cog.get_commands()
            if commands_list:
                cogs_data[cog_name] = [cmd.name for cmd in commands_list]
        
        for cog_name, cmds in cogs_data.items():
            if cmds:
                embed.add_field(
                    name=f"📌 {cog_name}",
                    value="\n".join([f"`/{cmd}`" for cmd in cmds[:5]]),
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed)
        log.debug(f"Slash help used by {interaction.user}")


async def setup(bot: commands.Bot):
    """Load the cog."""
    await bot.add_cog(Utility(bot))
    log.debug("📥 Utility cog loaded")
