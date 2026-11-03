from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from subscriptions import get_channels


async def check_subscription(client: Client, user_id: int) -> bool:
    channels = get_channels()

    enabled_channels = [
        row for row in channels if row[3] == 1
    ]

    if not enabled_channels:
        return True

    for channel_id, channel, link, enabled in enabled_channels:
        try:
            member = await client.get_chat_member(channel, user_id)

            if member.status not in {
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            }:
                return False

        except Exception:
            return False

    return True


def subscription_keyboard():
    channels = get_channels()

    buttons = []

    for channel_id, channel, link, enabled in channels:
        if enabled:
            buttons.append([
                InlineKeyboardButton(
                    f"⟡ الاشتراك في {channel} ⟡",
                    url=link
                )
            ])

    buttons.append([
        InlineKeyboardButton(
            "⟡ تحقق من الاشتراك ⟡",
            callback_data="check_subscription"
        )
    ])

    return InlineKeyboardMarkup(buttons)
