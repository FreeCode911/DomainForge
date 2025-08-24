import discord
from discord import app_commands
from utils.data_manager import load_data, save_data, is_admin

@app_commands.command(name="unban_user", description="Unban a user so they can use the bot again.")
async def unban_user(interaction: discord.Interaction, user: discord.User):
    if not is_admin(interaction.user.id):
        embed = discord.Embed(title="Permission Denied", description="You don't have permission to use this command.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    data = load_data()
    user_id = str(user.id)
    if user_id in data.get('banned_users', []):
        data['banned_users'].remove(user_id)
        save_data(data)
        embed = discord.Embed(title="User Unbanned", description=f"User {user.name} has been unbanned and can now use the bot again.", color=discord.Color.green())
    else:
        embed = discord.Embed(title="Not Banned", description=f"User {user.name} is not currently banned.", color=discord.Color.yellow())
    await interaction.response.send_message(embed=embed)