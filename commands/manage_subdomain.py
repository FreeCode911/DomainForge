import discord
from discord import app_commands
from discord.ui import View, Modal, TextInput
from utils.data_manager import is_admin, load_data, save_data
from utils.embed_helpers import build_embed
import cloudflare


class RenameModal(Modal, title="Rename Subdomain"):
    new_name = TextInput(label="New subdomain (only the host part)", placeholder="my-subdomain", required=True, max_length=63)

    def __init__(self, domain: str):
        super().__init__()
        self.domain = domain

    async def on_submit(self, interaction: discord.Interaction):
        try:
            parts = self.domain.split('.')
            zone = '.'.join(parts[-2:])
            new_full = f"{self.new_name.value}.{zone}"
            await interaction.response.defer()

            async with cloudflare.aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {cloudflare.API_TOKEN}", "Content-Type": "application/json"}
                # Find zone id
                async with session.get(f"{cloudflare.API_BASE_URL}/zones?name={zone}", headers=headers) as zresp:
                    zdata = await zresp.json()
                    if not zdata.get('success') or not zdata.get('result'):
                        await interaction.followup.send("Failed to locate zone for rename.", ephemeral=True)
                        return
                    zone_id = zdata['result'][0]['id']

                # Find existing record
                async with session.get(f"{cloudflare.API_BASE_URL}/zones/{zone_id}/dns_records?name={self.domain}", headers=headers) as rresp:
                    rdata = await rresp.json()
                    if not rdata.get('success') or not rdata.get('result'):
                        await interaction.followup.send("Failed to locate existing DNS record.", ephemeral=True)
                        return
                    record = rdata['result'][0]

                # Create new record
                create_payload = {
                    "type": record['type'],
                    "name": new_full.split('.')[0],
                    "content": record['content'],
                    "proxied": record.get('proxied', False),
                    "comment": f"Renamed from {self.domain} by {interaction.user.id}"
                }

                async with session.post(f"{cloudflare.API_BASE_URL}/zones/{zone_id}/dns_records", headers=headers, json=create_payload) as cresp:
                    cres = await cresp.json()
                    if not cres.get('success'):
                        await interaction.followup.send(f"Failed to create new record: {cres.get('errors')}", ephemeral=True)
                        return

                # Delete old record
                old_id = record['id']
                async with session.delete(f"{cloudflare.API_BASE_URL}/zones/{zone_id}/dns_records/{old_id}", headers=headers) as dresp:
                    dres = await dresp.json()
                    if not dres.get('success'):
                        await interaction.followup.send(f"Warning: created new record but failed to delete old: {dres.get('errors')}", ephemeral=True)
                    else:
                        # Update local data store
                        data = load_data()
                        uid = str(interaction.user.id)
                        if uid in data.get('users', {}) and self.domain in data['users'][uid]:
                            idx = data['users'][uid].index(self.domain)
                            data['users'][uid][idx] = new_full
                            save_data(data)

                        await interaction.followup.send(f"Renamed {self.domain} -> {new_full}")
        except Exception as e:
            await interaction.followup.send(f"An error occurred during rename: {e}", ephemeral=True)


class ManageSubdomainView(View):
    def __init__(self, domain: str):
        super().__init__()
        self.domain = domain

    @discord.ui.button(label="Rename", style=discord.ButtonStyle.secondary)
    async def rename(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = RenameModal(self.domain)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Toggle Proxy", style=discord.ButtonStyle.primary)
    async def toggle_proxy(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        success, message = await cloudflare.toggle_proxy_status(self.domain)
        embed = build_embed(title="Toggle Proxy", description=message, color=discord.Color.green() if success else discord.Color.red(), user=interaction.user)
        await interaction.followup.send(embed=embed)

    @discord.ui.button(label="Delete Subdomain", style=discord.ButtonStyle.danger)
    async def delete_subdomain(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        success = await cloudflare.delete_subdomain(self.domain)
        if success:
            data = load_data()
            user_id = str(interaction.user.id)
            if user_id in data['users'] and self.domain in data['users'][user_id]:
                data['users'][user_id].remove(self.domain)
                save_data(data)

            embed = build_embed(title="Subdomain Deleted", description=f"Successfully deleted {self.domain}", color=discord.Color.green(), user=interaction.user)
            await interaction.followup.send(embed=embed)
        else:
            embed = build_embed(title="Delete Failed", description=f"Failed to delete subdomain {self.domain}", color=discord.Color.red(), user=interaction.user)
            await interaction.followup.send(embed=embed, ephemeral=True)


@app_commands.command(name="manage_subdomain", description="Manage a subdomain (Admin or Owner).")
async def manage_subdomain(interaction: discord.Interaction, domain: str):
    is_user_authorized = False
    if is_admin(interaction.user.id):
        is_user_authorized = True
    else:
        data = load_data()
        user_id = str(interaction.user.id)
        if user_id in data['users'] and domain in data['users'][user_id]:
            is_user_authorized = True

    if not is_user_authorized:
        embed = build_embed(title="Permission Denied", description="You do not have permission to manage this subdomain.", color=discord.Color.red(), user=interaction.user)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    view = ManageSubdomainView(domain)
    embed = build_embed(title=f"Managing {domain}", description="Select an action:", color=discord.Color.blurple(), user=interaction.user)
    await interaction.response.send_message(embed=embed, view=view)