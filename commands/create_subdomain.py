import discord
from discord import app_commands
from views.subdomain_creation import SubdomainCreationView
from utils.data_manager import is_banned
import config

@app_commands.command(name="create_subdomain", description="Create a new subdomain record")
@app_commands.describe(
    record_type="The type of DNS record to create (A, CNAME, TXT, etc.)"
)
@app_commands.choices(record_type=[app_commands.Choice(name=rt, value=rt) for rt in config.RECORD_TYPES])
async def create_subdomain(interaction: discord.Interaction, record_type: str):
    if is_banned(interaction.user.id):
        await interaction.response.send_message("You are banned from using this bot.", ephemeral=True)
        return

    # Check if the user has the required role
    has_required_role = False
    for role in interaction.user.roles:
        if role.id in config.SUBDOMAIN_CREATION_ROLES:
            has_required_role = True
            break

    if not has_required_role:
        await interaction.response.send_message("You do not have permission to use this command.  Please request the appropriate role from an administrator.", ephemeral=True)
        return

    view = SubdomainCreationView(record_type=record_type)
    embed = discord.Embed(title="Subdomain Creation", description="*Let's create a subdomain!*", color=discord.Color.green())
    await interaction.response.send_message(embed=embed, view=view)
    result = await view.wait()
    if result:
        await interaction.response.send_message(result)