import logging
from typing import Iterable, List, Optional

import discord

from management_log import send_management_log

FIELD_LIMIT = 1024
ATTACHMENT_LIMIT = 5
NULL_TEXT = "(내용 없음)"


def _truncate(text: Optional[str], limit: int = FIELD_LIMIT) -> str:
    if not text:
        return NULL_TEXT
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3]}..."


def _format_author(author: Optional[discord.abc.User]) -> str:
    if not author:
        return "Unknown Author"
    if getattr(author, "bot", False):
        return f"{author} (bot)"
    discriminator = getattr(author, "discriminator", None)
    if discriminator and discriminator != "0":
        return f"{author.name}#{discriminator}"
    return getattr(author, "global_name", None) or getattr(author, "display_name", None) or author.name


def _format_attachments(attachments: Iterable[discord.Attachment]) -> str:
    att_list = list(attachments)
    items = []
    for idx, attachment in enumerate(att_list):
        if idx >= ATTACHMENT_LIMIT:
            items.append(f"...(+{len(att_list) - ATTACHMENT_LIMIT} more)")
            break
        name = attachment.filename
        url = attachment.url
        items.append(f"{name} ({url})")
    return "\n".join(items) if items else "없음"


def register(bot: discord.Client) -> None:
    @bot.listen("on_message_delete")
    async def handle_message_delete(message: discord.Message) -> None:
        try:
            if not getattr(message, "guild", None):
                return
            if getattr(message.author, "bot", False):
                return

            channel = getattr(message, "channel", None)
            content = _truncate(getattr(message, "content", "") or NULL_TEXT)
            attachments = _format_attachments(getattr(message, "attachments", []))
            embed = discord.Embed(
                title="메시지 삭제 로그",
                description=f"채널: <#{channel.id}>" if channel else "채널: 알 수 없음",
                color=0xED4245,
            )
            embed.add_field(name="작성자", value=_format_author(getattr(message, "author", None)), inline=False)
            embed.add_field(name="내용", value=content, inline=False)
            embed.add_field(name="첨부파일", value=attachments, inline=False)
            embed.add_field(name="메시지 ID", value=str(getattr(message, "id", "알 수 없음")), inline=False)
            embed.timestamp = discord.utils.utcnow()

            await send_management_log(bot, {"embeds": [embed]})
        except Exception:
            logging.exception("[messageDelete] error")

    @bot.listen("on_bulk_message_delete")
    async def handle_bulk_delete(messages: List[discord.Message]) -> None:
        try:
            if not messages:
                return
            if not getattr(messages[0], "guild", None):
                return

            channel = getattr(messages[0], "channel", None)
            sample = []
            for msg in messages[:3]:
                author = _format_author(getattr(msg, "author", None))
                content = _truncate(getattr(msg, "content", "") or NULL_TEXT, 200)
                sample.append(f"{author}: {content}")

            embed = discord.Embed(
                title="대량 메시지 삭제 로그",
                description=f"채널: <#{channel.id}>" if channel else "채널: 알 수 없음",
                color=0xED4245,
            )
            embed.add_field(name="삭제된 메시지 수", value=str(len(messages)), inline=False)
            embed.add_field(name="샘플 (최대 3개)", value="\n".join(sample) if sample else "없음", inline=False)
            embed.timestamp = discord.utils.utcnow()

            await send_management_log(bot, {"embeds": [embed]})
        except Exception:
            logging.exception("[bulkMessageDelete] error")
