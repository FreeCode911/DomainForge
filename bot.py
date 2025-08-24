import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from dotenv import load_dotenv
from views.subdomain_creation import SubdomainCreationView
from cloudflare import get_user_subdomains, delete_subdomain
from commands import ban, unban
from commands import create_subdomain, list_subdomains, userinfo, whois, request_subdomain_role, manage_subdomain, admin_manage

# Load environment variables
load_dotenv()

# Bot setup
import config
intents = discord.Intents.default()
banner = """
---------------------------------------------------
    DomainForge Bot is loading, please wait...
---------------------------------------------------
"""
print(banner)
bot = commands.Bot(command_prefix=config.COMMAND_PREFIX, intents=intents)
from utils.data_manager import start_data_saver

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    # Start data saver
    print('Starting data saver...')
    start_data_saver()

    # Register commands and show loading progress
    commands_to_register = [
        (create_subdomain.create_subdomain, 'create_subdomain'),
        (list_subdomains.list_subdomains, 'list_subdomains'),
        (userinfo.userinfo, 'userinfo'),
        (ban.ban_user, 'ban_user'),
        (whois.whois, 'whois'),
        (unban.unban_user, 'unban_user'),
        (request_subdomain_role.request_subdomain_role, 'request_subdomain_role'),
        (manage_subdomain.manage_subdomain, 'manage_subdomain'),
        (admin_manage.admin_manage, 'admin_manage'),
    ]

    for cmd, name in commands_to_register:
        try:
            bot.tree.add_command(cmd)
            print(f'Loaded command: {name}')
        except Exception as e:
            print(f'Failed to load command {name}: {e}')

    # Sync application commands with Discord
    try:
        print('Syncing application commands with Discord...')
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")



# Delete a subdomain
#@bot.tree.command(name="list", description="Show subdomains under the user")

bot.run(os.getenv('DISCORD_BOT_TOKEN'))