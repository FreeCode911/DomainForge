import discord
from discord import app_commands
from views.subdomain_creation import SubdomainCreationView
from utils.data_manager import is_banned
import config
from cloudflare import get_available_domains
from utils.embed_helpers import build_embed


@app_commands.command(name="create_subdomain", description="Create a new subdomain record.")
async def create_subdomain(interaction: discord.Interaction):
    if is_banned(interaction.user.id):
        embed = build_embed(title="Access Denied", description="You are banned from using this bot.", color=discord.Color.red(), user=interaction.user)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Check if the user has the required role
    has_required_role = False
    for role in interaction.user.roles:
        if role.id in config.SUBDOMAIN_CREATION_ROLES:
            has_required_role = True
            break

    if not has_required_role:
        embed = build_embed(title="Missing Role", description="You do not have permission to use this command. Please request the appropriate role from an administrator.", color=discord.Color.red(), user=interaction.user)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Fetch domains and populate the view so the select shows immediately
    domains = await get_available_domains()
    if not domains:
        embed = build_embed(title="No Domains", description="No available domains found.", color=discord.Color.red(), user=interaction.user)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    view = SubdomainCreationView()
    view.populate_domain_select(domains)
    embed = build_embed(title="Subdomain Creation", description="Let's create a subdomain — pick a domain to begin.", color=discord.Color.green(), user=interaction.user)
    try:
        await interaction.response.send_message(embed=embed, view=view)
        sent_via = 'interaction'
    except discord.errors.NotFound:
        # Interaction token invalid / unknown interaction.
        # Fall back to channel send so the view still appears.
        channel = interaction.channel or await interaction.user.create_dm()
        await channel.send(embed=embed, view=view)
        sent_via = 'channel'

    # Wait for the view to finish (timeout or user action)
    result = await view.wait()
    if result:
        try:
            if sent_via == 'interaction':
                await interaction.followup.send(result)
            else:
                # send to the channel used above
                channel = interaction.channel or await interaction.user.create_dm()
                await channel.send(result)
        except Exception:
            # Best-effort: ignore followup failures
            pass