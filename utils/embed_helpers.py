import discord


def build_embed(title: str, description: str | None = None, color: discord.Colour = discord.Color.blurple(), user: discord.abc.Snowflake | None = None, fields: list[tuple[str, str, bool]] | None = None, footer: str | None = None) -> discord.Embed:
    """Create a consistently styled embed.

    fields: list of (name, value, inline)
    user: optional discord user to show as author/footer
    """
    embed = discord.Embed(title=title, description=description or "", color=color, timestamp=discord.utils.utcnow())

    if user is not None:
        try:
            icon = getattr(user, "avatar", None)
            icon_url = icon.url if icon is not None else None
        except Exception:
            icon_url = None
        embed.set_author(name=str(user), icon_url=icon_url)
        embed.set_footer(text=(footer or f"Requested by {user}"))

    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

    return embed
