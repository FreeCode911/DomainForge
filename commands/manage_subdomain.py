import discord
from discord import app_commands
from discord.ui import Button, View
from utils.data_manager import is_admin, load_data, save_data
import cloudflare

class ManageSubdomainView(View):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain

    @discord.ui.button(label="Toggle Proxy", style=discord.ButtonStyle.primary)
    async def toggle_proxy(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        success, message = await cloudflare.toggle_proxy_status(self.domain)
        await interaction.followup.send(message)

    @discord.ui.button(label="Delete Subdomain", style=discord.ButtonStyle.danger)
    async def delete_subdomain(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        success = await cloudflare.delete_subdomain(self.domain)
        if success:
             # Remove subdomain from data
            data = load_data()
            user_id = str(interaction.user.id)
            if user_id in data['users'] and self.domain in data['users'][user_id]:
                data['users'][user_id].remove(self.domain)
                save_data(data)

            await interaction.followup.send(f"Successfully deleted subdomain {self.domain}")
        else:
            await interaction.followup.send(f"Failed to delete subdomain {self.domain}", ephemeral=True)

@app_commands.command(name="manage_subdomain", description="Manage a subdomain (Admin or Owner).")
async def manage_subdomain(interaction: discord.Interaction, domain: str):
    # Check if the user is an admin or the owner of the subdomain
    is_user_authorized = False
    if is_admin(interaction.user.id):
        is_user_authorized = True
    else:
        data = load_data()
        user_id = str(interaction.user.id)
        if user_id in data['users'] and domain in data['users'][user_id]:
            is_user_authorized = True

    if not is_user_authorized:
        await interaction.response.send_message("You do not have permission to manage this subdomain.", ephemeral=True)
        return

    # Create the view and send the initial message
    view = ManageSubdomainView(domain)
    embed = discord.Embed(title=f"Managing {domain}", description="Select an action:")
    await interaction.response.send_message(embed=embed, view=view)