import discord
from discord import app_commands
from utils.data_manager import load_data, is_admin

async def whois(interaction: discord.Interaction, domain: str):
    if not is_admin(interaction.user.id):
        embed = discord.Embed(title="Permission Denied", description="You don't have permission to use this command.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    data = load_data()
    for user_id, subdomains in data['users'].items():
        if domain in subdomains:
            user = await interaction.client.fetch_user(int(user_id))
            embed = discord.Embed(title="Whois Lookup", description=f"Domain {domain} is registered by user {user.name} (ID: {user_id})", color=discord.Color.blue())
            await interaction.response.send_message(embed=embed)
            return
    embed = discord.Embed(title="Whois Lookup", description=f"Domain {domain} is not registered by any user.", color=discord.Color.red())
    await interaction.response.send_message(embed=embed)