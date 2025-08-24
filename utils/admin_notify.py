import asyncio
import discord
import config


async def send_admin_embed(client: discord.Client, embed: discord.Embed):
    """Send an embed message to the configured admin channel.

    This is best-effort: if ADMIN_CHANNEL_ID is not set or the channel can't be
    found, the function returns quietly.
    """
    try:
        if not config.ADMIN_CHANNEL_ID:
            return
        channel = client.get_channel(config.ADMIN_CHANNEL_ID)
        if not channel:
            return
        # Ensure we can call send even if called from non-async context
        await channel.send(embed=embed)
    except Exception:
        # swallow exceptions to avoid breaking user flows
        return
