import logging
import os
import weakref
from typing import Optional

import discord

LOG_CHANNEL_ID = os.getenv("MANAGEMENT_LOG_CHANNEL_ID", "1422873243554943037")

_channel_cache: weakref.WeakKeyDictionary[
    discord.Client, discord.abc.Messageable
] = weakref.WeakKeyDictionary()


def _is_text_channel(channel: Optional[discord.abc.Messageable]) -> bool:
    return isinstance(channel, (discord.TextChannel, discord.Thread))


async def resolve_channel(bot: discord.Client) -> Optional[discord.abc.Messageable]:
    if not bot or not LOG_CHANNEL_ID:
        return None

    cached = _channel_cache.get(bot)
    if cached and _is_text_channel(cached):
        return cached

    try:
        channel_id = int(LOG_CHANNEL_ID)
    except (TypeError, ValueError):
        logging.warning("[ManagementLog] invalid channel id: %r", LOG_CHANNEL_ID)
        return None

    try:
        channel = bot.get_channel(channel_id)
        if not _is_text_channel(channel):
            channel = await bot.fetch_channel(channel_id)
        if _is_text_channel(channel):
            _channel_cache[bot] = channel
            return channel
    except Exception:
        logging.exception("[ManagementLog] failed to resolve log channel")
    return None


async def send_management_log(bot: discord.Client, payload: dict) -> bool:
    try:
        channel = await resolve_channel(bot)
        if not channel:
            return False

        final_payload = dict(payload or {})
        if "allowed_mentions" not in final_payload:
            final_payload["allowed_mentions"] = discord.AllowedMentions.none()
        if "silent" not in final_payload:
            final_payload["silent"] = True

        try:
            await channel.send(**final_payload)
            return True
        except TypeError:
            final_payload.pop("silent", None)
            await channel.send(**final_payload)
            return True
    except Exception:
        logging.exception("[ManagementLog] send failed")
    return False


__all__ = ["LOG_CHANNEL_ID", "send_management_log", "resolve_channel"]
