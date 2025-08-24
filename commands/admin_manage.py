import discord
from discord import app_commands
from discord.ui import Button, View
from utils.data_manager import is_admin, load_data, save_data, set_feature, is_feature_enabled
from utils.embed_helpers import build_embed

class AdminManageView(View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Toggle Request Role", style=discord.ButtonStyle.primary)
    async def toggle_request_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Only admins via is_admin()
        if not is_admin(interaction.user.id):
            await interaction.response.send_message("You are not authorized.", ephemeral=True)
            return

        current = is_feature_enabled('request_subdomain_role')
        set_feature('request_subdomain_role', not current)
        await interaction.response.send_message(f"request_subdomain_role set to {not current}")

    @discord.ui.button(label="View Hidden", style=discord.ButtonStyle.secondary)
    async def view_hidden(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_admin(interaction.user.id):
            await interaction.response.send_message("You are not authorized.", ephemeral=True)
            return
        data = load_data()
        hidden = data.get('hidden', {})
        if not hidden:
            await interaction.response.send_message("No hidden items configured.", ephemeral=True)
            return
        fields = [(k, str(v), False) for k, v in hidden.items()]
        embed = build_embed(title="Hidden Items", description="Items hidden from users", color=discord.Color.blurple(), user=interaction.user, fields=fields)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Toggle Hidden", style=discord.ButtonStyle.secondary)
    async def toggle_hidden(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_admin(interaction.user.id):
            await interaction.response.send_message("You are not authorized.", ephemeral=True)
            return
        await interaction.response.send_modal(ToggleHiddenModal())

    @discord.ui.button(label="Ban User", style=discord.ButtonStyle.danger)
    async def ban_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BanUserModal())

    @discord.ui.button(label="Unban User", style=discord.ButtonStyle.success)
    async def unban_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(UnbanUserModal())

    @discord.ui.button(label="View User Info", style=discord.ButtonStyle.primary)
    async def view_user_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ViewUserInfoModal())

import logging

class BanUserModal(discord.ui.Modal, title="Ban User"):
    user_id = discord.ui.TextInput(label="User ID to Ban", placeholder="Enter the user's Discord ID")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            user_id = self.user_id.value
            if not user_id.isdigit():
                await interaction.response.send_message("Invalid User ID. User ID must be a number.", ephemeral=True)
                return

            data = load_data()
            if user_id in data.get('banned_users', []):
                await interaction.response.send_message(f"User with ID {user_id} is already banned.", ephemeral=True)
                return
            
            data['banned_users'].append(user_id)
            save_data(data)
            await interaction.response.send_message(f"User with ID {user_id} has been banned.")

        except Exception as e:
            logging.exception("Error in BanUserModal:")
            await interaction.response.send_message("An error occurred while banning the user.", ephemeral=True)

class UnbanUserModal(discord.ui.Modal, title="Unban User"):
    user_id = discord.ui.TextInput(label="User ID to Unban", placeholder="Enter the user's Discord ID")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            user_id = self.user_id.value
            if not user_id.isdigit():
                await interaction.response.send_message("Invalid User ID. User ID must be a number.", ephemeral=True)
                return

            data = load_data()
            if user_id not in data.get('banned_users', []):
                await interaction.response.send_message(f"User with ID {user_id} is not banned.", ephemeral=True)
                return

            data['banned_users'].remove(user_id)
            save_data(data)
            await interaction.response.send_message(f"User with ID {user_id} has been unbanned.")

        except Exception as e:
            logging.exception("Error in UnbanUserModal:")
            await interaction.response.send_message("An error occurred while unbanning the user.", ephemeral=True)

class ViewUserInfoModal(discord.ui.Modal, title="View User Info"):
    user_id = discord.ui.TextInput(label="User ID", placeholder="Enter the user's Discord ID")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            user_id = self.user_id.value
            if not user_id.isdigit():
                await interaction.response.send_message("Invalid User ID. User ID must be a number.", ephemeral=True)
                return

            data = load_data()
            if user_id not in data['users']:
                await interaction.response.send_message(f"No subdomains registered for user with ID {user_id}.", ephemeral=True)
                return

            subdomains = data['users'][user_id]
            embed = discord.Embed(title=f"User Info for {user_id}", description=f"Subdomains: {', '.join(subdomains)}")
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            logging.exception("Error in ViewUserInfoModal:")
            await interaction.response.send_message("An error occurred while viewing user info.", ephemeral=True)


class ToggleHiddenModal(discord.ui.Modal, title="Toggle Hidden Item"):
    key = discord.ui.TextInput(label="Key to hide/unhide", placeholder="e.g. create_subdomain_embed")
    state = discord.ui.TextInput(label="Hidden state (true/false)", placeholder="true or false")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            k = self.key.value.strip()
            s = self.state.value.strip().lower()
            if s not in ("true", "false"):
                await interaction.response.send_message("State must be 'true' or 'false'", ephemeral=True)
                return
            hidden = (s == "true")
            from utils.data_manager import set_hidden
            set_hidden(k, hidden)
            await interaction.response.send_message(f"Set hidden[{k}] = {hidden}", ephemeral=True)
        except Exception as e:
            logging.exception("Error in ToggleHiddenModal:")
            await interaction.response.send_message("An error occurred while toggling hidden item.", ephemeral=True)

logging.basicConfig(filename='discord.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

@app_commands.command(name="admin_manage", description="Manage bot settings (Admin only).")
async def admin_manage(interaction: discord.Interaction):
    if not is_admin(interaction.user.id):
        embed = build_embed(title="Permission Denied", description="You do not have permission to use this command.", color=discord.Color.red(), user=interaction.user)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    view = AdminManageView()
    # Build an admin dashboard embed showing current feature flags
    data = load_data()
    features = data.get('features', {})
    fields = [(k, str(v), True) for k, v in features.items()]
    embed = build_embed(title="Admin Dashboard", description="Toggle features below.", color=discord.Color.blurple(), user=interaction.user, fields=fields)
    await interaction.response.send_message(embed=embed, view=view)