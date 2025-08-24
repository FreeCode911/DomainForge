import discord
from discord import app_commands
from utils.data_manager import load_data, is_banned
from commands.manage_subdomain import ManageSubdomainView
from utils.embed_helpers import build_embed


@app_commands.command(name="list_subdomains", description="Show your subdomains.")
async def list_subdomains(interaction: discord.Interaction):
    if is_banned(interaction.user.id):
        embed = build_embed(title="Access Denied", description="You are banned from using this bot.", color=discord.Color.red(), user=interaction.user)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    user_id = str(interaction.user.id)
    data = load_data()
    subdomains = data.get('users', {}).get(user_id, [])

    if not subdomains:
        embed = build_embed(title="No Subdomains", description="You don't have any subdomains.", color=discord.Color.red(), user=interaction.user)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Build a select menu of subdomains
    options = [discord.SelectOption(label=d, value=d, description=f"Manage {d}") for d in subdomains]
    select = discord.ui.Select(placeholder="Select a subdomain to manage", options=options, custom_id="manage_select")

    async def _select_callback(i: discord.Interaction):
        domain = i.data['values'][0]
        view = ManageSubdomainView(domain)
        embed = build_embed(title=f"Manage {domain}", description="Choose an action:", user=i.user)
        await i.response.edit_message(embed=embed, view=view)

    select.callback = _select_callback
    view = discord.ui.View()
    view.add_item(select)
    embed = build_embed(title="Your Subdomains", description="Select a subdomain below to manage it.", color=discord.Color.blurple(), user=interaction.user)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)