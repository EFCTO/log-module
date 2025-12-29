import logging

import discord

from management_log import send_management_log


def register(bot: discord.Client) -> None:
    @bot.listen("on_user_update")
    async def handle_user_update(before: discord.User, after: discord.User) -> None:
        try:
            if getattr(after, "bot", False):
                return

            changes = []

            if before.name != after.name:
                changes.append(("사용자명", before.name or "없음", after.name or "없음"))

            before_display = getattr(before, "global_name", None)
            after_display = getattr(after, "global_name", None)
            if before_display != after_display:
                changes.append(("표시 이름", before_display or "없음", after_display or "없음"))

            before_discriminator = getattr(before, "discriminator", None)
            after_discriminator = getattr(after, "discriminator", None)
            if before_discriminator != after_discriminator:
                changes.append(
                    ("태그(Discriminator)", before_discriminator or "없음", after_discriminator or "없음")
                )

            before_avatar = getattr(before, "avatar", None)
            after_avatar = getattr(after, "avatar", None)
            if before_avatar != after_avatar:
                before_avatar_url = before.display_avatar.url if hasattr(before, "display_avatar") else "없음"
                after_avatar_url = after.display_avatar.url if hasattr(after, "display_avatar") else "없음"
                changes.append(("프로필 이미지", before_avatar_url, after_avatar_url))

            if not changes:
                return

            embed = discord.Embed(
                title="사용자 프로필 변경 로그",
                description=f"{after} (ID: {after.id})",
                color=0x57F287,
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
            logging.exception("[userUpdate] error")
