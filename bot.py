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
print("\n---------------------------------------------------\n   DomainForge Bot is loading, please wait...\n---------------------------------------------------\n")
bot = commands.Bot(command_prefix=config.COMMAND_PREFIX, intents=intents)
from utils.data_manager import start_data_saver

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    start_data_saver()
    bot.tree.add_command(create_subdomain.create_subdomain)
    bot.tree.add_command(list_subdomains.list_subdomains)
    bot.tree.add_command(userinfo.userinfo)
    bot.tree.add_command(ban.ban_user)
    bot.tree.add_command(whois.whois)
    bot.tree.add_command(unban.unban_user)
    bot.tree.add_command(request_subdomain_role.request_subdomain_role)
    bot.tree.add_command(manage_subdomain.manage_subdomain)
    bot.tree.add_command(admin_manage.admin_manage)
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")



# Delete a subdomain
#@bot.tree.command(name="list", description="Show subdomains under the user")

bot.run(os.getenv('DISCORD_BOT_TOKEN'))