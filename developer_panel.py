from pathlib import Path
from pyrogram import filters
import sqlite3
from datetime import datetime
import asyncio
import os
import sys

from pyrogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from subscriptions import get_channels, add_channel, toggle_channel, delete_channel
import requests
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().with_name(".env"))
BOT_TOKEN = os.getenv("DECOR_BOT_TOKEN", "")

DEVELOPER_ID = 8734901394



awaiting_channel_add = set()
awaiting_channel_delete = set()
awaiting_channel_toggle = set()

DB_FILE = str(Path(__file__).resolve().with_name("developer_users.db"))
BROADCAST_MODE = set()
MAINTENANCE_MODE = False

LOG_FILE = str(Path(__file__).resolve().with_name("developer_logs.txt"))

async def send_normal_colored_keyboard(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": text,
            "reply_markup": {
                "keyboard": [
                    [{"text": "• دمج الأسماء •", "style": "danger"}],
                    [
                        {"text": "• العربي •", "style": "danger"},
                        {"text": "• English •", "style": "danger"},
                        {"text": "• أرقام •", "style": "danger"}
                    ],
                    [{"text": "• عن البوت •", "style": "success"}]
                ],
                "resize_keyboard": True
            }
        },
        timeout=20
    )
    data = response.json()

    if not data.get("ok"):
        raise RuntimeError(f"Bot API error: {data}")


async def send_developer_colored_keyboard(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": text,
            "reply_markup": {
                "keyboard": [
                    [
                        {"text": "⟦ الإحصائيات ⟧", "style": "primary"},
                        {"text": "⟦ المستخدمون ⟧", "style": "primary"}
                    ],
                    [
                        {"text": "⟦ الإذاعة ⟧", "style": "primary"},
                        {"text": "⟦ إلغاء الإذاعة ⟧", "style": "primary"},
                        {"text": "⟦ إدارة البوت ⟧", "style": "primary"}
                    ],
                    [
                        {"text": "⟦ الاشتراك ⟧", "style": "primary"}
                    ],
                    [
                        {"text": "⟦ السجلات ⟧", "style": "primary"},
                        {"text": "⟦ تحديث ⟧", "style": "primary"}
                    ],
                    [
                        {"text": "𓏺 𝐦𝐲 𝐛𝐨𝐭 .", "style": "danger"}
                    ]
                ],
                "resize_keyboard": True
            }
        },
        timeout=20
    )
    data = response.json()

    if not data.get("ok"):
        raise RuntimeError(f"Bot API error: {data}")


async def send_subscription_colored_keyboard(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": text,
            "reply_markup": {
                "keyboard": [
                    [
                        {"text": "⟦ إضافة قناة ⟧", "style": "danger"},
                        {"text": "⟦ حذف قناة ⟧", "style": "danger"}
                    ],
                    [
                        {"text": "⟦ تشغيل / إيقاف ⟧", "style": "danger"}
                    ],
                    [
                        {"text": "⟦ رجوع ⟧", "style": "danger"}
                    ]
                ],
                "resize_keyboard": True
            }
        },
        timeout=20
    )
    data = response.json()

    if not data.get("ok"):
        raise RuntimeError(f"Bot API error: {data}")



async def send_bot_management_colored_keyboard(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": text,
            "reply_markup": {
                "keyboard": [
                    [
                        {"text": "⟦ تشغيل البوت ⟧", "style": "danger"},
                        {"text": "⟦ إيقاف البوت ⟧", "style": "danger"}
                    ],
                    [
                        {"text": "⟦ حالة البوت ⟧", "style": "danger"}
                    ],
                    [
                        {"text": "⟦ رجوع ⟧", "style": "danger"}
                    ]
                ],
                "resize_keyboard": True
            }
        },
        timeout=20
    )
    data = response.json()

    if not data.get("ok"):
        raise RuntimeError(f"Bot API error: {data}")



def add_log(event):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{now}] {event}\\n")
    except Exception:
        pass


bot_management_keyboard = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton("⟦ تشغيل البوت ⟧"),
            KeyboardButton("⟦ إيقاف البوت ⟧")
        ],
        [
            KeyboardButton("⟦ حالة البوت ⟧")
        ],
        [
            KeyboardButton("⟦ رجوع ⟧")
        ]
    ],
    resize_keyboard=True
)


# =========================
# لوحة المطور
# =========================

normal_keyboard = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton("• دمج الأسماء •")
        ],
        [
            KeyboardButton("• العربي •"),
            KeyboardButton("• English •"), KeyboardButton("• أرقام •")
        ],
        [
            KeyboardButton("• عن البوت •")
        ]
    ],
    resize_keyboard=True
)

subscription_keyboard = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton("⟦ إضافة قناة ⟧"),
            KeyboardButton("⟦ حذف قناة ⟧")
        ],
        [
            KeyboardButton("⟦ تشغيل / إيقاف ⟧")
        ],
        [
            KeyboardButton("⟦ رجوع ⟧")
        ]
    ],
    resize_keyboard=True
)

developer_keyboard = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton("⟦ الإحصائيات ⟧"),
            KeyboardButton("⟦ المستخدمون ⟧")
        ],
        [
            KeyboardButton("⟦ الإذاعة ⟧"),
            KeyboardButton("⟦ إلغاء الإذاعة ⟧"),
            KeyboardButton("⟦ إدارة البوت ⟧")
        ],
        [
            KeyboardButton("⟦ الاشتراك ⟧")
        ],
        [
            KeyboardButton("⟦ السجلات ⟧"),
            KeyboardButton("⟦ تحديث ⟧")
        ],
        [
            KeyboardButton("𓏺 𝐦𝐲 𝐛𝐨𝐭 .")
        ]
    ],
    resize_keyboard=True
)


def is_developer(user_id):
    return user_id == DEVELOPER_ID


# =========================
# قاعدة المستخدمين
# =========================

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            username TEXT,
            last_seen TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_user(user):
    if not user:
        return

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO users
        (user_id, first_name, username, last_seen)
        VALUES (?, ?, ?, ?)
    """, (
        user.id,
        user.first_name or "",
        user.username or "",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_users():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, first_name, username, last_seen
        FROM users
        ORDER BY last_seen DESC
    """)

    users = cur.fetchall()

    conn.close()

    return users


def get_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, first_name, username, last_seen
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    user = cur.fetchone()

    conn.close()

    return user


# =========================
# فتح بروفايل المستخدم
# =========================

def profile_keyboard(user_id):
    user = get_user(user_id)

    username = user[2] if user else ""

    profile_url = (
        f"https://t.me/{username}"
        if username
        else f"tg://user?id={user_id}"
    )

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "⟦ فتح البروفايل ⟧",
                    url=profile_url
                )
            ],
            [
                InlineKeyboardButton(
                    "⟦ رجوع ⟧",
                    callback_data="developer_users"
                )
            ]
        ]
    )


# =========================
# بيانات المستخدم كنص
# =========================

def user_details_text(user):
    if not user:
        return "المستخدم غير موجود."

    user_id, first_name, username, last_seen = user

    username_text = (
        f"@{username}"
        if username
        else "لا يوجد"
    )

    return (
        "╭━━━━━━━━━━━━━━━━━━╮\n"
        "       بيانات المستخدم\n"
        "╰━━━━━━━━━━━━━━━━━━╯\n\n"
        f"الاسم: {first_name or 'بدون اسم'}\n"
        f"Username: {username_text}\n"
        f"ID: `{user_id}`\n"
        f"آخر نشاط: {last_seen}"
    )


# =========================
# قائمة المستخدمين
# =========================

def users_keyboard(limit=50):
    users = get_users()

    buttons = []

    for user_id, first_name, username, last_seen in users[:limit]:

        name = first_name or "بدون اسم"

        if username:
            title = f"⟦ {name} @{username} ⟧"
        else:
            title = f"⟦ {name} ⟧"

        buttons.append(
            [
                InlineKeyboardButton(
                    title,
                    callback_data=f"developer_user:{user_id}"
                )
            ]
        )

    return users, InlineKeyboardMarkup(buttons) if buttons else None


# =========================
# إحصائيات
# =========================

def statistics_text():
    users = get_users()

    return (
        "╭━━━━━━━━━━━━━━━━━━╮\n"
        "        الإحصائيات\n"
        "╰━━━━━━━━━━━━━━━━━━╯\n\n"
        f"عدد المستخدمين: {len(users)}\n"
        f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


# =========================
# تشغيل قاعدة البيانات
# =========================

init_db()

from pyrogram import filters


def _register_user_profile_callback(app):

    @app.on_callback_query(filters.regex(r"^developer_user:\d+$"))
    async def developer_user_profile(client, callback_query):
        if not callback_query.from_user:
            return

        if not is_developer(callback_query.from_user.id):
            await callback_query.answer()
            return

        user_id = int(callback_query.data.split(":")[1])
        user = get_user(user_id)

        await callback_query.answer()

        await callback_query.message.edit_text(
            user_details_text(user),
            reply_markup=profile_keyboard(user_id)
        )



def _register_users_handler(app):

    @app.on_message(filters.text & filters.private)
    async def developer_users_handler(client, message):
        global MAINTENANCE_MODE

        if not message.from_user:
            return

        if not is_developer(message.from_user.id):
            return

        user_id = message.from_user.id
        text = message.text

        if text == "⟦ إلغاء الإذاعة ⟧" and user_id in BROADCAST_MODE:
            BROADCAST_MODE.discard(user_id)

            await send_developer_colored_keyboard(
                message.chat.id,
                "╭━━━━━━━━━━━━━━━━━━╮\n"
                "       الإذاعة\n"
                "╰━━━━━━━━━━━━━━━━━━╯\n\n"
                "تم إلغاء وضع الإذاعة."
            )
            return

        if user_id in BROADCAST_MODE:
            BROADCAST_MODE.discard(user_id)

            users = get_users()
            success = 0
            failed = 0

            for user in users:
                try:
                    await app.send_message(user[0], text)
                    success += 1
                except Exception:
                    failed += 1

            await send_developer_colored_keyboard(
                message.chat.id,
                "╭━━━━━━━━━━━━━━━━━━╮\n"
                "       تقرير الإذاعة\n"
                "╰━━━━━━━━━━━━━━━━━━╯\n\n"
                f"إجمالي المستخدمين  : {len(users)}\n"
                f"تم الإرسال          : {success}\n"
                f"تعذر الإرسال        : {failed}\n\n"
                f"وقت التنفيذ         : "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            return

        subscription_buttons = {
            "⟦ إضافة قناة ⟧",
            "⟦ حذف قناة ⟧",
            "⟦ تشغيل / إيقاف ⟧",
            "⟦ رجوع ⟧"
        }

        if text in subscription_buttons:
            awaiting_channel_add.discard(user_id)

        if user_id in awaiting_channel_add:
            awaiting_channel_add.discard(user_id)

            parts = [x.strip() for x in text.split("|", 1)]

            if len(parts) != 2:
                awaiting_channel_add.add(user_id)

                await send_subscription_colored_keyboard(
                    message.chat.id,
                    "╭━━━━━━━━━━━━━━━━━━╮\n"
                    "       إضافة قناة\n"
                    "╰━━━━━━━━━━━━━━━━━━╯\n\n"
                    "أرسل بيانات القناة بهذا الشكل:\n\n"
                    "@اسم_القناة | رابط_القناة"
                )
                return

            channel, link = parts
            add_channel(channel, link)
            add_log(f"تمت إضافة قناة: {channel} بواسطة {user_id}")

            await send_subscription_colored_keyboard(
                message.chat.id,
                "╭━━━━━━━━━━━━━━━━━━╮\n"
                "       إضافة قناة\n"
                "╰━━━━━━━━━━━━━━━━━━╯\n\n"
                f"القناة : {channel}\n"
                f"الرابط : {link}\n\n"
                "تمت إضافة القناة بنجاح."
            )
            return

        if text == "𓏺 𝐦𝐲 𝐛𝐨𝐭 .":
#             add_log(f"العودة إلى الكيبورد العادي بواسطة {user_id}")

            await send_normal_colored_keyboard(
                message.chat.id,
                "╭━━━━━━━━━━━━━━━━━━╮\n"
                "        القائمة الرئيسية\n"
                "╰━━━━━━━━━━━━━━━━━━╯\n\n"
                "تم الرجوع إلى القائمة الرئيسية."
            )
            return

        if text == "⟦ الإحصائيات ⟧":
            await send_developer_colored_keyboard(
                message.chat.id,
                statistics_text()
            )
            return

        if text == "⟦ المستخدمون ⟧":
            users, markup = users_keyboard()

            if not users:
                await send_developer_colored_keyboard(
                    message.chat.id,
                    "╭━━━━━━━━━━━━━━━━━━╮\n"
                    "       المستخدمون\n"
                    "╰━━━━━━━━━━━━━━━━━━╯\n\n"
                    "لا يوجد مستخدمون مسجلون حتى الآن."
                )
                return

            await message.reply_text(
                "╭━━━━━━━━━━━━━━━━━━╮\n"
                "       المستخدمون\n"
                "╰━━━━━━━━━━━━━━━━━━╯\n\n"
                f"إجمالي المستخدمين : {len(users)}\n\n"
                "اختر مستخدمًا لعرض بياناته:",
                reply_markup=markup
            )
            return

        if text == "⟦ الإذاعة ⟧":
            BROADCAST_MODE.add(user_id)

            await send_developer_colored_keyboard(
                message.chat.id,
                "╭━━━━━━━━━━━━━━━━━━╮\n"
                "        الإذاعة\n"
                "╰━━━━━━━━━━━━━━━━━━╯\n\n"
                "تم تفعيل وضع الإذاعة.\n\n"
                "أرسل الآن الرسالة المطلوب إرسالها."
            )
            return

        if text == "⟦ إدارة البوت ⟧":
            status = "متوقف للصيانة" if MAINTENANCE_MODE else "يعمل"

            await send_bot_management_colored_keyboard(
                message.chat.id,
                "╭━━━━━━━━━━━━━━━━━━╮\n"
                "       إدارة البوت\n"
                "╰━━━━━━━━━━━━━━━━━━╯\n\n"
                f"الحالة الحالية : {status}"
            )
            return

        if text == "⟦ تشغيل البوت ⟧":
            MAINTENANCE_MODE = False

            await send_bot_management_colored_keyboard(
                message.chat.id,
                "╭━━━━━━━━━━━━━━━━━━╮\n"
                "       تشغيل البوت\n"
                "╰━━━━━━━━━━━━━━━━━━╯\n\n"
                "تم تشغيل البوت.\n"
                "البوت متاح للمستخدمين الآن."
            )
            return

        if text == "⟦ إيقاف البوت ⟧":
            MAINTENANCE_MODE = True

            await send_bot_management_colored_keyboard(
                message.chat.id,
                "╭━━━━━━━━━━━━━━━━━━╮\n"
                "       إيقاف البوت\n"
                "╰━━━━━━━━━━━━━━━━━━╯\n\n"
                "تم إيقاف البوت للمستخدمين.\n"
                "لوحة المطور ما زالت متاحة."
            )
            return

        if text == "⟦ حالة البوت ⟧":
            status = "متوقف للصيانة" if MAINTENANCE_MODE else "يعمل"

            await send_bot_management_colored_keyboard(
                message.chat.id,
                "╭━━━━━━━━━━━━━━━━━━╮\n"
                "        حالة البوت\n"
                "╰━━━━━━━━━━━━━━━━━━╯\n\n"
                f"الحالة : {status}\n"
                f"وقت الفحص : "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            return

        if text == "⟦ الاشتراك ⟧":
            channels = get_channels()

            lines = [
                "╭━━━━━━━━━━━━━━━━━━╮",
                "        الاشتراك",
                "╰━━━━━━━━━━━━━━━━━━╯",
                "",
                f"عدد القنوات : {len(channels)}",
                ""
            ]

            if channels:
                for channel_id, channel, link, enabled in channels:
                    state = "تشغيل" if enabled else "إيقاف"
                    lines.append(f"〔 {state} 〕  {channel}")
            else:
                lines.append("لا توجد قنوات اشتراك حاليًا.")

            await send_subscription_colored_keyboard(
                message.chat.id,
                "\n".join(lines)
            )
            return

        if text == "⟦ إضافة قناة ⟧":
            awaiting_channel_add.add(user_id)

            await send_subscription_colored_keyboard(
                message.chat.id,
                "╭━━━━━━━━━━━━━━━━━━╮\n"
                "       إضافة قناة\n"
                "╰━━━━━━━━━━━━━━━━━━╯\n\n"
                "أرسل بيانات القناة بهذا الشكل:\n\n"
                "@اسم_القناة | رابط_القناة"
            )
            return

        if text == "⟦ حذف قناة ⟧":
            channels = get_channels()

            if not channels:
                await send_subscription_colored_keyboard(
                    message.chat.id,
                    "╭━━━━━━━━━━━━━━━━━━╮\n"
                    "       حذف قناة\n"
                    "╰━━━━━━━━━━━━━━━━━━╯\n\n"
                    "لا توجد قنوات لحذفها."
                )
                return

            buttons = []

            for channel_id, channel, link, enabled in channels:
                buttons.append([
                    InlineKeyboardButton(
                        f"〔 حذف 〕 {channel}",
                        callback_data=f"sub_delete:{channel_id}"
                    )
                ])

            await message.reply_text(
                "╭━━━━━━━━━━━━━━━━━━╮\n"
                "       حذف قناة\n"
                "╰━━━━━━━━━━━━━━━━━━╯\n\n"
                "اختر القناة التي تريد حذفها:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return

        if text == "⟦ تشغيل / إيقاف ⟧":
            channels = get_channels()

            if not channels:
                await send_subscription_colored_keyboard(
                    message.chat.id,
                    "لا توجد قنوات."
                )
                return

            buttons = []

            for channel_id, channel, link, enabled in channels:
                state = "تشغيل" if enabled else "إيقاف"

                buttons.append([
                    InlineKeyboardButton(
                        f"〔 {state} 〕 {channel}",
                        callback_data=f"sub_toggle:{channel_id}"
                    )
                ])

            await message.reply_text(
                "╭━━━━━━━━━━━━━━━━━━╮\n"
                "      حالة القنوات\n"
                "╰━━━━━━━━━━━━━━━━━━╯\n\n"
                "اختر القناة لتغيير حالتها:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return

        if text == "⟦ السجلات ⟧":
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    logs = f.readlines()

                if logs:
                    logs = logs[-30:]
                    log_text = "".join(logs)
                    if len(log_text) > 3500:
                        log_text = log_text[-3500:]

                    await send_developer_colored_keyboard(
                        message.chat.id,
                        "╭━━━━━━━━━━━━━━━━━━╮\n"
                        "        السجلات\n"
                        "╰━━━━━━━━━━━━━━━━━━╯\n\n"
                        f"{log_text}"
                    )
                else:
                    await send_developer_colored_keyboard(
                        message.chat.id,
                        "╭━━━━━━━━━━━━━━━━━━╮\n"
                        "        السجلات\n"
                        "╰━━━━━━━━━━━━━━━━━━╯\n\n"
                        "لا توجد سجلات حتى الآن."
                    )
            else:
                await send_developer_colored_keyboard(
                    message.chat.id,
                    "╭━━━━━━━━━━━━━━━━━━╮\n"
                    "        السجلات\n"
                    "╰━━━━━━━━━━━━━━━━━━╯\n\n"
                    "لا توجد سجلات حتى الآن."
                )
            return

        if text == "⟦ تحديث ⟧":
            add_log(f"تم طلب تحديث البوت بواسطة {user_id}")

            await send_developer_colored_keyboard(
                message.chat.id,
                "╭━━━━━━━━━━━━━━━━━━╮\n"
                "         تحديث\n"
                "╰━━━━━━━━━━━━━━━━━━╯\n\n"
                "جاري تحديث البوت وإعادة تشغيله..."
            )

            await asyncio.sleep(1)

            os.execv(
                sys.executable,
                [sys.executable, os.path.join(os.getcwd(), "decor_bot.py")]
            )
            return

        if text == "⟦ رجوع ⟧":
            await send_developer_colored_keyboard(
                message.chat.id,
                "╭━━━━━━━━━━━━━━━━━━╮\n"
                "       لوحة المطور\n"
                "╰━━━━━━━━━━━━━━━━━━╯\n\n"
                "تم الرجوع إلى لوحة المطور."
            )
            return


def _register_subscription_callbacks(app):

    @app.on_callback_query(filters.regex(r"^sub_delete:\d+$"))
    async def subscription_delete_callback(client, callback_query):
        if not callback_query.from_user:
            await callback_query.answer()
            return

        if not is_developer(callback_query.from_user.id):
            await callback_query.answer()
            return

        channel_id = int(callback_query.data.split(":")[1])
        delete_channel(channel_id)

        await callback_query.answer("تم الحذف")

        channels = get_channels()

        buttons = []

        for cid, channel, link, enabled in channels:
            buttons.append([
                InlineKeyboardButton(
                    f"〔 حذف 〕 {channel}",
                    callback_data=f"sub_delete:{cid}"
                )
            ])

        await callback_query.message.edit_text(
            "╭━━━━━━━━━━━━━━━━━━╮\n"
            "       حذف قناة\n"
            "╰━━━━━━━━━━━━━━━━━━╯\n\n"
            "اختر قناة أخرى للحذف:"
            if channels else
            "╭━━━━━━━━━━━━━━━━━━╮\n"
            "       حذف قناة\n"
            "╰━━━━━━━━━━━━━━━━━━╯\n\n"
            "تم حذف القناة.\n"
            "لا توجد قنوات أخرى.",
            reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
        )


    @app.on_callback_query(filters.regex(r"^sub_toggle:\d+$"))
    async def subscription_toggle_callback(client, callback_query):
        if not callback_query.from_user:
            await callback_query.answer()
            return

        if not is_developer(callback_query.from_user.id):
            await callback_query.answer()
            return

        channel_id = int(callback_query.data.split(":")[1])
        toggle_channel(channel_id)

        await callback_query.answer("تم التغيير")

        channels = get_channels()
        buttons = []

        for cid, channel, link, enabled in channels:
            state = "تشغيل" if enabled else "إيقاف"

            buttons.append([
                InlineKeyboardButton(
                    f"〔 {state} 〕 {channel}",
                    callback_data=f"sub_toggle:{cid}"
                )
            ])

        await callback_query.message.edit_text(
            "╭━━━━━━━━━━━━━━━━━━╮\n"
            "      حالة القنوات\n"
            "╰━━━━━━━━━━━━━━━━━━╯\n\n"
            "تم تغيير حالة القناة.\n\n"
            "اختر قناة أخرى:"
            if buttons else
            "لا توجد قنوات.",
            reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
        )


def _register_users_back_callback(app):

    @app.on_callback_query(filters.regex(r"^developer_users$"))
    async def developer_users_back(client, callback_query):
        if not callback_query.from_user:
            return

        if not is_developer(callback_query.from_user.id):
            await callback_query.answer()
            return

        users, markup = users_keyboard()

        await callback_query.answer()

        await callback_query.message.edit_text(
            "╭━━━━━━━━━━━━━━━━━━╮\n"
            "       المستخدمون\n"
            "╰━━━━━━━━━━━━━━━━━━╯\n\n"
            f"إجمالي المستخدمين : {len(users)}\n\n"
            "اختر مستخدمًا لعرض بياناته:",
            reply_markup=markup
        )


def register_developer_panel(app):
    _register_users_handler(app)
    _register_user_profile_callback(app)
    _register_users_back_callback(app)
    _register_subscription_callbacks(app)
