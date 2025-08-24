import discord
from discord.ui import Select, View, Button, Modal, TextInput
from config import RECORD_TYPES, RECORD_FEATURES
from cloudflare import create_subdomain
import uuid
import json
import os
from utils.data_manager import load_data, save_data
from utils.embed_helpers import build_embed


class SubdomainCreationView(View):
    def __init__(self):
        super().__init__(timeout=120)
        self.domain = None
        self.record_type = None
        self.record_content = None
        self.proxy_status = None
        self.additional_features = {}
        self.uuid = str(uuid.uuid4())

    def populate_domain_select(self, domains: list[str]):
        """Populate the view with a domain Select synchronously before sending the view."""
        self.clear_items()
        if not domains:
            return False
        options = [discord.SelectOption(label=d) for d in domains]
        select = Select(placeholder="Select a domain", options=options, custom_id="domain_select")

        async def _domain_callback(interaction: discord.Interaction):
            await self.select_domain(interaction)

        select.callback = _domain_callback
        self.add_item(select)
        return True

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Allow interactions; handlers below will manage state.
        return True

    async def on_timeout(self):
        self.clear_items()

    async def select_domain(self, interaction: discord.Interaction):
        self.domain = interaction.data["values"][0]
        self.clear_items()
        record_select = Select(placeholder="Select a record type",
                               options=[discord.SelectOption(label=rt) for rt in RECORD_TYPES],
                               custom_id="record_type_select")

        async def _record_callback(i: discord.Interaction):
            await self.select_record_type(i)

        record_select.callback = _record_callback
        self.add_item(record_select)
        embed = build_embed(title="Subdomain Creation", description=f"Selected domain: {self.domain}\nNow, choose a record type:", color=discord.Color.blue(), user=interaction.user, fields=[("Domain", self.domain, False), ("Next", "Choose a record type below", False)])
        await interaction.response.edit_message(embed=embed, view=self)

    async def select_record_type(self, interaction: discord.Interaction):
        self.record_type = interaction.data["values"][0]
        await interaction.response.send_modal(RecordContentModal(self))

    async def select_proxy_status(self, interaction: discord.Interaction):
        self.proxy_status = interaction.data["values"][0] == "True"
        await self.update_view(interaction)

    async def confirm(self, interaction: discord.Interaction):
        await self.finalize_subdomain(interaction)

    async def cancel(self, interaction: discord.Interaction):
        embed = build_embed(title="Cancelled", description="Subdomain creation cancelled.", color=discord.Color.red(), user=interaction.user)
        await interaction.response.edit_message(embed=embed, view=None)

    async def update_view(self, interaction: discord.Interaction):
        fields = [
            ("Domain", self.domain, False),
            ("Record Type", self.record_type, True),
            ("Record Content", self.record_content or "(not set)", True),
            ("Proxy Status", "Proxied" if self.proxy_status else "DNS only", True),
        ]
        for feature, value in self.additional_features.items():
            fields.append((feature.capitalize(), value, False))
        fields.append(("Confirmation", "Please confirm or cancel the subdomain creation.", False))

        embed = build_embed(title="Confirm Subdomain", description="Review the details below and confirm.", color=discord.Color.green(), user=interaction.user, fields=fields)

        self.clear_items()
        btn_confirm = Button(label="Confirm", style=discord.ButtonStyle.green, custom_id="confirm")
        btn_cancel = Button(label="Cancel", style=discord.ButtonStyle.red, custom_id="cancel")

        async def _confirm_cb(interaction: discord.Interaction):
            await self.confirm(interaction)

        async def _cancel_cb(interaction: discord.Interaction):
            await self.cancel(interaction)

        btn_confirm.callback = _confirm_cb
        btn_cancel.callback = _cancel_cb
        self.add_item(btn_confirm)
        self.add_item(btn_cancel)
        await interaction.response.edit_message(embed=embed, view=self)

    async def finalize_subdomain(self, interaction: discord.Interaction):
        try:
            user_id = str(interaction.user.id)
            success, message = await create_subdomain(self.domain, self.record_type, self.record_content, self.proxy_status, self.additional_features, user_id=user_id)
            if success:
                data = load_data()
                if user_id not in data['users']:
                    data['users'][user_id] = []
                subdomain = f"{self.record_content.split(',')[0]}"
                data['users'][user_id].append(subdomain)
                save_data(data)

                embed = build_embed(title="Subdomain Created", description=f"Subdomain created successfully!\n{message}", color=discord.Color.green(), user=interaction.user, fields=[("Domain", subdomain, False), ("Record Type", self.record_type, True), ("Content", self.record_content.split(',')[1], True), ("Proxy", "Proxied" if self.proxy_status else "DNS only", True)])
                await interaction.response.edit_message(embed=embed, view=None)

                dm_fields = [
                    ("Domain", subdomain, False),
                    ("Record Type", self.record_type, True),
                    ("Content", self.record_content.split(',')[1], True),
                    ("Proxy Status", "Proxied" if self.proxy_status else "DNS only", True),
                ]
                for feature, value in self.additional_features.items():
                    dm_fields.append((feature.capitalize(), value, False))

                dm_embed = build_embed(title="Subdomain Registration Successful", color=discord.Color.green(), user=interaction.user, fields=dm_fields)
                await interaction.user.send(embed=dm_embed)
            else:
                embed = build_embed(title="Creation Failed", description=f"Failed to create DNS record. Cloudflare returned the following error:\n```{message}```", color=discord.Color.red(), user=interaction.user)
                await interaction.response.edit_message(embed=embed, view=None)
        except Exception as e:
            embed = build_embed(title="Error", description=f"An unexpected error occurred: {str(e)}", color=discord.Color.red(), user=interaction.user)
            await interaction.response.edit_message(embed=embed, view=None)


class RecordContentModal(Modal, title="Enter Record Content"):
    def __init__(self, view: SubdomainCreationView):
        super().__init__()
        self.view = view
        self.name = TextInput(label="Subdomain Name", custom_id="name")
        self.content = TextInput(label="Record Content", custom_id="content")
        self.add_item(self.name)
        self.add_item(self.content)

        if self.view.record_type in RECORD_FEATURES:
            for feature in RECORD_FEATURES[self.view.record_type]:
                self.add_item(TextInput(label=feature.capitalize(), custom_id=feature))

    async def on_submit(self, interaction: discord.Interaction):
        self.view.record_content = f"{self.name.value}.{self.view.domain},{self.content.value}"

        # Store additional features
        for child in self.children[2:]:
            self.view.additional_features[child.custom_id] = child.value

        self.view.clear_items()
        proxy_select = Select(placeholder="Proxy status",
                                  options=[discord.SelectOption(label="Proxied", value="True"),
                                           discord.SelectOption(label="DNS only", value="False")],
                                  custom_id="proxy_status_select")

        async def _proxy_cb(interaction: discord.Interaction):
            await self.view.select_proxy_status(interaction)

        proxy_select.callback = _proxy_cb
        self.view.add_item(proxy_select)

        fields = [
            ("Domain", self.view.domain, False),
            ("Record Type", self.view.record_type, True),
            ("Record Content", self.view.record_content, True),
        ]
        for feature, value in self.view.additional_features.items():
            fields.append((feature.capitalize(), value, False))
        fields.append(("Next Step", "Choose proxy status", False))

        embed = build_embed(title="Subdomain Creation", color=discord.Color.blue(), user=interaction.user, fields=fields)
        await interaction.response.edit_message(embed=embed, view=self.view)


# Use load_data/save_data from utils.data_manager to keep a single source of truth
