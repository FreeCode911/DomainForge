import discord
from discord import app_commands
import config
from utils.data_manager import is_feature_enabled
from utils.embed_helpers import build_embed
from utils.admin_notify import send_admin_embed


@app_commands.command(name="request_subdomain_role", description="Request the subdomain creation role from an administrator.")
async def request_subdomain_role(interaction: discord.Interaction):
    if not is_feature_enabled('request_subdomain_role'):
        embed = build_embed(title="Disabled", description="Requesting subdomain role is currently disabled by an administrator.", color=discord.Color.red(), user=interaction.user)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if not config.ADMIN_CHANNEL_ID:
        embed = build_embed(title="Not Configured", description="The administrator has not configured an admin channel for role requests.", color=discord.Color.yellow(), user=interaction.user)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = build_embed(title="Subdomain Role Request", description=f"User {interaction.user.mention} (ID: {interaction.user.id}) is requesting the subdomain creation role.")
    # background notify via helper
    await send_admin_embed(interaction.client, embed)
    await interaction.response.send_message(embed=build_embed(title="Request Sent", description="Your request has been sent to the admins."), ephemeral=True)