import discord
from discord import app_commands
from utils.data_manager import load_data, save_data, is_admin
from cloudflare import delete_subdomain

async def ban_user(interaction: discord.Interaction, user: discord.User):
    if not is_admin(interaction.user.id):
        embed = discord.Embed(title="Permission Denied", description="You don't have permission to use this command.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    data = load_data()
    user_id = str(user.id)
    if user_id in data['users']:
        subdomains = data['users'][user_id]
        for subdomain in subdomains:
            await delete_subdomain(subdomain)
        del data['users'][user_id]
        data['banned_users'].append(user_id)
        save_data(data)
        embed = discord.Embed(title="User Banned", description=f"User {user.name} has been banned and all their subdomains have been deleted.", color=discord.Color.green())
    else:
        embed = discord.Embed(title="No Subdomains", description=f"User {user.name} has no subdomains to delete.", color=discord.Color.red())
    await interaction.response.send_message(embed=embed)