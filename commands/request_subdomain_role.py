import discord
from discord import app_commands
import config

@app_commands.command(name="request_subdomain_role", description="Request the subdomain creation role from an administrator.")
async def request_subdomain_role(interaction: discord.Interaction):
    if not config.ADMIN_CHANNEL_ID:
        await interaction.response.send_message("The administrator has not configured an admin channel for role requests. Please contact them directly.", ephemeral=True)
        return

    admin_channel = interaction.client.get_channel(config.ADMIN_CHANNEL_ID)
    if not admin_channel:
        await interaction.response.send_message("The administrator has not configured a valid admin channel for role requests. Please contact them directly.", ephemeral=True)
        return

    embed = discord.Embed(title="Subdomain Role Request", description=f"User {interaction.user.mention} (ID: {interaction.user.id}) is requesting the subdomain creation role.")
    await admin_channel.send(embed=embed)
    await interaction.response.send_message("Your request for the subdomain creation role has been sent to the administrators. They will review your request and grant you the role if appropriate.", ephemeral=True)