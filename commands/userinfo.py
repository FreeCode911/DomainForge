import discord
from discord import app_commands
from utils.data_manager import load_data, is_admin

@app_commands.command(name="userinfo", description="Show info about a user and their subdomains.")
async def userinfo(interaction: discord.Interaction, user: discord.User):
    print(f"User ID attempting admin command: {interaction.user.id}")
    if not is_admin(interaction.user.id):
        embed = discord.Embed(title="Permission Denied", description="You don't have permission to use this command.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    data = load_data()
    user_id = str(user.id)
    if user_id in data['users']:
        subdomains = data['users'][user_id]
        embed = discord.Embed(title=f"User Info: {user.name}", description=f"Total domains: {len(subdomains)}\nDomains: {', '.join(subdomains)}", color=discord.Color.blue())
    else:
        embed = discord.Embed(title=f"User Info: {user.name}", description="No subdomains registered.", color=discord.Color.red())
    await interaction.response.send_message(embed=embed)