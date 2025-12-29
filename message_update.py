import logging
from typing import Optional

import discord

from management_log import send_management_log

FIELD_LIMIT = 1024
# Placeholder when content is missing
NULL_TEXT = "(\ub0b4\uc6a9 \uc5c6\uc74c)"


async def _fetch_if_partial(message: discord.Message) -> Optional[discord.Message]:
    if not getattr(message, "partial", False):
        return message
    try:
        return await message.fetch()
    except Exception:
        return None


def _truncate(text: Optional[str], limit: int = FIELD_LIMIT) -> str:
    if not text:
        return NULL_TEXT
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3]}..."


def _format_author(author: discord.abc.User) -> str:
    if not author:
        return "Unknown Author"
    discriminator = getattr(author, "discriminator", None)
    if discriminator and discriminator != "0":
        return f"{author.name}#{discriminator}"
    return getattr(author, "global_name", None) or getattr(author, "display_name", None) or author.name


def register(bot: discord.Client) -> None:
    @bot.listen("on_message_edit")
    async def handle_message_edit(before: discord.Message, after: discord.Message) -> None:
        try:
            before_full = await _fetch_if_partial(before)
            after_full = await _fetch_if_partial(after)
            if not before_full or not after_full or not after_full.guild:
                return

            author = after_full.author or before_full.author
            if not author or getattr(author, "bot", False):
                return

            before_content = before_full.content or ""
            after_content = after_full.content or ""
            if before_content == after_content:
                return

            embed = discord.Embed(
                title="\uba54\uc2dc\uc9c0 \uc218\uc815 \ub85c\uadf8",
                description=f"\ucc44\ub110: <#{after_full.channel.id}>",
                color=0xFEE75C,
            )
            icon_url = author.display_avatar.url if hasattr(author, "display_avatar") else None
            embed.set_author(
                name=_format_author(author),
                icon_url=icon_url,
            )
            embed.add_field(name="Before", value=_truncate(before_content), inline=False)
            embed.add_field(name="After", value=_truncate(after_content), inline=False)
            embed.add_field(
                name="\uba54\uc2dc\uc9c0 ID",
                value=str(after_full.id or "\uc54c \uc218 \uc5c6\uc74c"),
                inline=False,
            )
            embed.timestamp = discord.utils.utcnow()

            await send_management_log(bot, {"embeds": [embed]})
        except Exception:
            logging.exception("[messageUpdate] error")
