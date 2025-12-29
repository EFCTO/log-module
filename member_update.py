import logging
from typing import List, Optional

import discord

from management_log import send_management_log


def _role_names(roles: List[discord.Role]) -> List[str]:
    return [role.mention for role in roles if not getattr(role, "is_default", lambda: False)()]


def _avatar_key(member: discord.Member) -> Optional[str]:
    return str(getattr(member, "guild_avatar", None) or getattr(member, "avatar", None) or "")


def register(bot: discord.Client) -> None:
    @bot.listen("on_member_update")
    async def handle_member_update(before: discord.Member, after: discord.Member) -> None:
        try:
            if getattr(after, "bot", False):
                return

            changes = []

            if before.nick != after.nick:
                changes.append(
                    ("닉네임", before.nick or "없음", after.nick or "없음")
                )

            before_roles = set(_role_names(list(before.roles)))
            after_roles = set(_role_names(list(after.roles)))
            added = after_roles - before_roles
            removed = before_roles - after_roles
            if added:
                changes.append(("추가된 역할", "없음", ", ".join(sorted(added))))
            if removed:
                changes.append(("제거된 역할", ", ".join(sorted(removed)), "없음"))

            if _avatar_key(before) != _avatar_key(after):
                before_avatar = before.display_avatar.url if hasattr(before, "display_avatar") else "없음"
                after_avatar = after.display_avatar.url if hasattr(after, "display_avatar") else "없음"
                changes.append(("프로필 이미지", before_avatar, after_avatar))

            if not changes:
                return

            embed = discord.Embed(
                title="프로필 변경 로그",
                description=f"유저: {after.mention} (ID: {after.id})",
                color=0x5865F2,
            )

            for name, before_val, after_val in changes:
                embed.add_field(
                    name=name,
                    value=f"이전: {before_val}\n이후: {after_val}",
                    inline=False,
                )

            embed.timestamp = discord.utils.utcnow()
            await send_management_log(bot, {"embeds": [embed]})
        except Exception:
            logging.exception("[memberUpdate] error")
