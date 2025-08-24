import discord
from discord import app_commands
from utils.data_manager import load_data, is_banned

async def list_subdomains(interaction: discord.Interaction):
    if is_banned(interaction.user.id):
        await interaction.response.send_message("You are banned from using this bot.", ephemeral=True)
        return
    user_id = str(interaction.user.id)
    data = load_data()
    if user_id in data['users']:
        subdomains = data['users'][user_id]
        embed = discord.Embed(title="Your Subdomains", description=f"{', '.join(subdomains)}", color=discord.Color.blue())
    else:
        embed = discord.Embed(title="No Subdomains", description="You don't have any subdomains.", color=discord.Color.red())
    await interaction.response.send_message(embed=embed)