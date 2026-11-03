from pathlib import Path
import os
import json
import random
import urllib.parse
import urllib.request
import unicodedata

import developer_panel
from developer_panel import (
    developer_keyboard,
    is_developer,
    DEVELOPER_ID,
    save_user,
    get_user,
    register_developer_panel
)
from dotenv import load_dotenv
from force_sub import check_subscription, subscription_keyboard
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
import requests

load_dotenv(Path(__file__).resolve().with_name(".env"))

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("DECOR_BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("DECOR_BOT_TOKEN is missing")

app = Client(
    "decor_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

DEVELOPER_ID = 8734901394


# =========================
# Colored Bot API Keyboard
# =========================

def colored_keyboard():
    return {
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


async def send_colored_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": text,
            "reply_markup": colored_keyboard()
        },
        timeout=20
    )
    data = response.json()

    if not data.get("ok"):
        raise RuntimeError(f"Bot API error: {data}")

    return data


# =========================
# Keyboard
# =========================

user_modes = {}
keyboard = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton("• دمج الأسماء •")
        ],
        [
            KeyboardButton("• العربي •"),
            KeyboardButton("• English •"),
            KeyboardButton("• أرقام •")
        ],
        [
            KeyboardButton("• عن البوت •")
        ]
    ],
    resize_keyboard=True
)


# =========================
# English Unicode fonts
# =========================

LOWER = "abcdefghijklmnopqrstuvwxyz"
UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

FONT_FAMILIES = {
    "Bold": (
        "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇",
        "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭"
    ),

    "Italic": (
        "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻",
        "𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡"
    ),

    "Bold Italic": (
        "𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯",
        "𝘼𝘽𝘾𝘿𝙀𝙁𝙂𝙃𝙄𝙅𝙆𝙇𝙈𝙉𝙊𝙋𝙌𝙍𝙎𝙏𝙐𝙑𝙒𝙓𝙔𝙕"
    ),

    "Monospace": (
        "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣",
        "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉"
    ),

    "Sans": (
        "𝖺𝖻𝖼𝖽𝖾𝖿𝗀𝗁𝗂𝗃𝗄𝗅𝗆𝗇𝗈𝗉𝗊𝗋𝗌𝗍𝗎𝗏𝗐𝗑𝗒𝗓",
        "𝖠𝖡𝖢𝖣𝖤𝖥𝖦𝖧𝖨𝖩𝖪𝖫𝖬𝖭𝖮𝖯𝖰𝖱𝖲𝖳𝖴𝖵𝖶𝖷𝖸𝖹"
    ),

    "Sans Bold": (
        "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇",
        "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭"
    ),

    "Sans Italic": (
        "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻",
        "𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡"
    ),

    "Fraktur": (
        "𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟",
        "𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅"
    ),

    "Double": (
        "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫",
        "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ"
    ),

    "Script": (
        "𝒶𝒷𝒸𝒹𝑒𝒻𝑔𝒽𝒾𝒿𝓀𝓁𝓂𝓃𝑜𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏",
        "𝒜𝐵𝒞𝒟𝐸𝐹𝒢𝐻𝐼𝒥𝒦𝐿𝑀𝒩𝒪𝒫𝒬𝑅𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵"
    ),

    "Bold Script": (
        "𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃",
        "𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩"
    ),

    "Small Caps": (
        "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ),

    "Fullwidth": (
        "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ",
        "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
    )
}


def apply_font(text, font):
    lower, upper = font

    table = str.maketrans(
        LOWER + UPPER,
        lower + upper
    )

    result = text.translate(table)

    digit_maps = {
        "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵": "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵",
        "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻": "0123456789",
        "𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯": "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵",
        "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣": "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿",
        "𝖺𝖻𝖼𝖽𝖾𝖿𝗀𝗁𝗂𝗃𝗄𝗅𝗆𝗇𝗈𝗉𝗊𝗋𝗌𝗍𝗎𝗏𝗐𝗑𝗒𝗓": "𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫",
        "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫": "𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡"
    }

    # الخطوط التي لها أرقام Unicode خاصة
    digit_style = "0123456789"

    if lower == "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇":
        digit_style = "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"
    elif lower == "𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙵𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯":
        digit_style = "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"
    elif lower == "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣":
        digit_style = "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿"
    elif lower == "𝖺𝖻𝖼𝖽𝖾𝖿𝗀𝗁𝗂𝗃𝗄𝗅𝗆𝗇𝗈𝗉𝗊𝗋𝗌𝗍𝗎𝗏𝗐𝗑𝗒𝗓":
        digit_style = "𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫"
    elif lower == "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫":
        digit_style = "𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡"

    result = result.translate(str.maketrans("0123456789", digit_style))

    return result


# =========================
# Extra English styles
# =========================

def english_bars(text):
    mapping = {
        "a": "𝐴", "b": "𝐵", "c": "𝐶", "d": "𝐷", "e": "𝐸", "f": "𝐹",
        "g": "𝐺", "h": "𝐻", "i": "𝐼", "j": "𝐽", "k": "𝐾", "l": "𝐿",
        "m": "𝑀", "n": "𝑁", "o": "𝑂", "p": "𝑃", "q": "𝑄", "r": "𝑅",
        "s": "𝑆", "t": "𝑇", "u": "𝑈", "v": "𝑉", "w": "𝑊", "x": "𝑋",
        "y": "𝑌", "z": "𝑍"
    }

    result = ""
    for char in text:
        base = mapping.get(char.lower(), char)
        result += base + "̮̑"

    return "║ " + result + " ║"


def english_extra(text):
    results = []
    seen = set()

    def add(name, value):
        value = value.strip()

        if not value:
            return

        if value == text:
            return

        if value in seen:
            return

        seen.add(value)
        results.append((name, value))

    # =========================
    # ستايل 𓏺 ♯ ᥉َِꫝُِꪖَِᥒُِꪖَِႦ .
    # =========================

    style1_map = {
        "a": "ꪖ", "b": "Ⴆ", "c": "ᥴ", "d": "ᦔ",
        "e": "ꫀ", "f": "ᠻ", "g": "ᧁ", "h": "ꫝ",
        "i": "ﺃ", "j": "᧒", "k": "ᛕ", "l": "ꪶ",
        "m": "ꪑ", "n": "ᥒ", "o": "ꪮ", "p": "ρ",
        "q": "ᑫ", "r": "᥅", "s": "᥉", "t": "ᡶ",
        "u": "ꪊ", "v": "ꪜ", "w": "᭙", "x": "᥊",
        "y": "ꪗ", "z": "ɀ"
    }

    styled1 = ""
    for i, char in enumerate(text):
        c = char.lower()
        if c in style1_map:
            styled1 += style1_map[c]
            styled1 += "َِ" if i % 2 == 0 else "ُِ"
        else:
            styled1 += char

    add(
        "Special Arabic Mix",
        "𓏺 ♯ " + styled1 + " ."
    )

    # =========================
    # ستايل - 𝑬 𝑳 𝑫 𝑶 𝑪 𝑻 𝑶 𝑹 • ༗
    # =========================

    italic_map = str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛"
    )

    spaced_italic = "- " + " ".join(
        char.translate(italic_map) for char in text
    ) + " • ༗"

    add(
        "Spaced Italic",
        spaced_italic
    )

    # =========================
    # ستايل °•~𝕂𝔸𝕊𝟟~•°
    # =========================

    kas7_map = str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
        "𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡"
    )

    add(
        "KAS7 Frame",
        "°•~" + text.translate(kas7_map) + "~•°"
    )

    # =========================
    # ستايل ᥆᥉ᥴᥲᖇ↷🕷
    # =========================

    oscar_map = {
        "a": "ᥲ", "b": "ᑲ", "c": "ᥴ", "d": "ძ",
        "e": "ᥱ", "f": "ᠻ", "g": "ᧁ", "h": "һ",
        "i": "і", "j": "ȷ", "k": "ƙ", "l": "ᥣ",
        "m": "m", "n": "ᥒ", "o": "᥆", "p": "ρ",
        "q": "զ", "r": "r", "s": "᥉", "t": "t",
        "u": "ᥙ", "v": "᥎", "w": "ᥕ", "x": "᥊",
        "y": "ᥡ", "z": "z"
    }

    oscar_text = "".join(
        oscar_map.get(char.lower(), char)
        for char in text
    )

    add(
        "Oscar Spider",
        oscar_text + "↷🕷"
    )

    # =========================
    # ستايل ᏦᎪᎡᏞᎾ
    # =========================

    carl_map = {
        "A":"Ꭺ","B":"Ᏼ","C":"Ꮯ","D":"Ꭰ","E":"Ꭼ","F":"Ꮀ",
        "G":"Ꮐ","H":"Ꮋ","I":"Ꮖ","J":"Ꭻ","K":"Ꮶ","L":"Ꮮ",
        "M":"Ꮇ","N":"Ꮑ","O":"Ꮎ","P":"Ꮲ","Q":"Ꭴ","R":"Ꭱ",
        "S":"Ꮥ","T":"Ꭲ","U":"Ꮼ","V":"Ꮩ","W":"Ꮤ","X":"Ꮖ",
        "Y":"Ꮍ","Z":"Ꮓ"
    }

    styled3 = "".join(
        carl_map.get(char.upper(), char)
        for char in text
    )

    add(
        "Cyrillic Style",
        styled3
    )

    # =========================
    # ستايل # 𝙻𝚞𝚌𝚊𝚜
    # =========================

    mono_map = {
        "a":"𝚊","b":"𝚋","c":"𝚌","d":"𝚍","e":"𝚎","f":"𝚏",
        "g":"𝚐","h":"𝚑","i":"𝚒","j":"𝚓","k":"𝚔","l":"𝚕",
        "m":"𝚖","n":"𝚗","o":"𝚘","p":"𝚙","q":"𝚚","r":"𝚛",
        "s":"𝚜","t":"𝚝","u":"𝚞","v":"𝚟","w":"𝚠","x":"𝚡",
        "y":"𝚢","z":"𝚣"
    }

    styled2 = "".join(
        mono_map.get(char.lower(), char)
        for char in text
    )

    add(
        "Monospace",
        "# " + styled2
    )

    # =========================
    # ستايل ⋆ . 𝙁 َ𝘼 َ𝙍 َ𝙀 ٍ𝙎 . ⤸
    # =========================

    sans_bold_italic_upper = {
        "A":"𝘼","B":"𝘽","C":"𝘾","D":"𝘿","E":"𝙀","F":"𝙁",
        "G":"𝙂","H":"𝙃","I":"𝙄","J":"𝙅","K":"𝙆","L":"𝙇",
        "M":"𝙈","N":"𝙉","O":"𝙊","P":"𝙋","Q":"𝙌","R":"𝙍",
        "S":"𝙎","T":"𝙏","U":"𝙐","V":"𝙑","W":"𝙒","X":"𝙓",
        "Y":"𝙔","Z":"𝙕"
    }

    styled_special = ""

    for i, char in enumerate(text):
        c = char.upper()

        if c in sans_bold_italic_upper:
            styled_special += sans_bold_italic_upper[c]

            if i == len(text.replace(" ", "")) - 1:
                styled_special += "ٍ"
            else:
                styled_special += "َ"

        else:
            styled_special += char

    add(
        "Special Aesthetic",
        "⋆ . " + styled_special + " . ⤸"
    )

    # =========================
    # Unicode mathematical fonts
    # =========================

    def math_style(value, upper, lower):
        out = ""

        for c in value:
            if "A" <= c <= "Z":
                out += chr(upper + ord(c) - 65)
            elif "a" <= c <= "z":
                out += chr(lower + ord(c) - 97)
            else:
                out += c

        return out

    add("Bold", math_style(text, 0x1D400, 0x1D41A))
    add("Italic", math_style(text, 0x1D434, 0x1D44E))
    add("Bold Italic", math_style(text, 0x1D468, 0x1D482))
    add("Double", math_style(text, 0x1D538, 0x1D552))
    add("Monospace", math_style(text, 0x1D670, 0x1D68A))
    add("Sans", math_style(text, 0x1D5A0, 0x1D5BA))
    add("Sans Bold", math_style(text, 0x1D5D4, 0x1D5EE))
    add("Sans Italic", math_style(text, 0x1D608, 0x1D622))
    add("Sans Bold Italic", math_style(text, 0x1D63C, 0x1D656))
    add("Sans Mono", math_style(text, 0x1D670, 0x1D68A))

    # =========================
    # Script
    # =========================

    script_upper = {
        "A":"𝒜","B":"ℬ","C":"𝒞","D":"𝒟","E":"ℰ","F":"ℱ",
        "G":"𝒢","H":"ℋ","I":"ℐ","J":"𝒥","K":"𝒦","L":"ℒ",
        "M":"ℳ","N":"𝒩","O":"𝒪","P":"𝒫","Q":"𝒬","R":"ℛ",
        "S":"𝒮","T":"𝒯","U":"𝒰","V":"𝒱","W":"𝒲","X":"𝒳",
        "Y":"𝒴","Z":"𝒵"
    }

    script_lower = {
        "a":"𝒶","b":"𝒷","c":"𝒸","d":"𝒹","e":"ℯ","f":"𝒻",
        "g":"ℊ","h":"𝒽","i":"𝒾","j":"𝒿","k":"𝓀","l":"𝓁",
        "m":"𝓂","n":"𝓃","o":"ℴ","p":"𝓅","q":"𝓆","r":"𝓇",
        "s":"𝓈","t":"𝓉","u":"𝓊","v":"𝓋","w":"𝓌","x":"𝓍",
        "y":"𝓎","z":"𝓏"
    }

    add(
        "Script",
        "".join(
            script_upper.get(
                c,
                script_lower.get(c, c)
            )
            for c in text
        )
    )

    # =========================
    # Fraktur
    # =========================

    fraktur_upper = {
        "A":"𝔄","B":"𝔅","C":"ℭ","D":"𝔇","E":"𝔈","F":"𝔉",
        "G":"𝔊","H":"ℌ","I":"ℑ","J":"𝔍","K":"𝔎","L":"𝔏",
        "M":"𝔐","N":"𝔑","O":"𝔒","P":"𝔓","Q":"𝔔","R":"ℜ",
        "S":"𝔖","T":"𝔗","U":"𝔘","V":"𝔙","W":"𝔚","X":"𝔛",
        "Y":"𝔜","Z":"ℨ"
    }

    fraktur_lower = {
        "a":"𝔞","b":"𝔟","c":"𝔠","d":"𝔡","e":"𝔢","f":"𝔣",
        "g":"𝔤","h":"𝔥","i":"𝔦","j":"𝔧","k":"𝔨","l":"𝔩",
        "m":"𝔪","n":"𝔫","o":"𝔬","p":"𝔭","q":"𝔮","r":"𝔯",
        "s":"𝔰","t":"𝔱","u":"𝔲","v":"𝔳","w":"𝔴","x":"𝔵",
        "y":"𝔶","z":"𝔷"
    }

    add(
        "Fraktur",
        "".join(
            fraktur_upper.get(
                c,
                fraktur_lower.get(c, c)
            )
            for c in text
        )
    )

    # =========================
    # Small Caps
    # =========================

    small_caps = {
        "a":"ᴀ","b":"ʙ","c":"ᴄ","d":"ᴅ","e":"ᴇ",
        "f":"ꜰ","g":"ɢ","h":"ʜ","i":"ɪ","j":"ᴊ",
        "k":"ᴋ","l":"ʟ","m":"ᴍ","n":"ɴ","o":"ᴏ",
        "p":"ᴘ","q":"ǫ","r":"ʀ","s":"s","t":"ᴛ",
        "u":"ᴜ","v":"ᴠ","w":"ᴡ","x":"x","y":"ʏ","z":"ᴢ"
    }

    add(
        "Small Caps",
        "".join(
            small_caps.get(c.lower(), c)
            for c in text
        )
    )

    # =========================
    # Superscript
    # =========================

    super_map = {
        "a":"ᵃ","b":"ᵇ","c":"ᶜ","d":"ᵈ","e":"ᵉ","f":"ᶠ",
        "g":"ᵍ","h":"ʰ","i":"ⁱ","j":"ʲ","k":"ᵏ","l":"ˡ",
        "m":"ᵐ","n":"ⁿ","o":"ᵒ","p":"ᵖ","q":"ᑫ","r":"ʳ",
        "s":"ˢ","t":"ᵗ","u":"ᵘ","v":"ᵛ","w":"ʷ","x":"ˣ",
        "y":"ʸ","z":"ᶻ"
    }

    add(
        "Superscript",
        "".join(
            super_map.get(c.lower(), c)
            for c in text
        )
    )

    # =========================
    # Custom fonts from your list
    # =========================

    custom_maps = {
        "ƒᥲძᥡ": {
            "f":"ƒ","a":"ᥲ","d":"ძ","y":"ᥡ",
            "F":"Ƒ","A":"ᥲ","D":"ᗫ","Y":"Ƴ"
        },

        "ƒꪖᦔꪗ": {
            "f":"ƒ","a":"ꪖ","d":"ᦔ","y":"ꪗ",
            "F":"Ƒ","A":"ꪖ","D":"ᗪ","Y":"Ƴ"
        },

        "Angular": {
            "f":"ᖴ","a":"ᗩ","d":"ᗪ","y":"Y",
            "F":"ᖴ","A":"ᗩ","D":"ᗪ","Y":"Y"
        },

        "Greek Mix": {
            "f":"𝖿","a":"α","d":"ძ","y":"𝗒",
            "F":"𝖥","A":"Α","D":"ᗪ","Y":"𝖸"
        },

        "Greek Dark": {
            "f":"𝖋","a":"α","d":"ძ","y":"𝗒",
            "F":"𝕱","A":"Α","D":"𝔇","Y":"𝖄"
        },

        "Double Caps": {
            "F":"𝔽","A":"𝔸","D":"𝔻","Y":"𝕐",
            "f":"𝕗","a":"𝕒","d":"𝕕","y":"𝕪"
        },

        "Double Accent": {
            "Y":"Ý",
            "y":"ý"
        }
    }

    for name, mapping in custom_maps.items():
        add(
            name,
            "".join(
                mapping.get(c, c)
                for c in text
            )
        )

    # =========================
    # Fullwidth
    # =========================

    add(
        "Fullwidth",
        "".join(
            chr(ord(c) + 0xFEE0)
            if "!" <= c <= "~"
            else "　"
            if c == " "
            else c
            for c in text
        )
    )

    # =========================
    # Circled
    # =========================

    circled = {}

    for i in range(26):
        circled[chr(65 + i)] = chr(0x24B6 + i)
        circled[chr(97 + i)] = chr(0x24D0 + i)

    add(
        "Circled",
        "".join(
            circled.get(c, c)
            for c in text
        )
    )

    # =========================
    # Spacing
    # =========================

    add("Spaced", " ".join(text))
    add("Wide Spaced", "  ".join(text))
    add("Dotted", "·".join(text))
    add("Vertical", "│".join(text))
    add("Dash", "-".join(text))
    add("Underscore", "_".join(text))
    add("Colon", ":".join(text))
    add("Wave", "~".join(text))
    add("Pipe", "|".join(text))
    add("Slash", "/".join(text))
    add("Dot Space", ". ".join(text))

    # =========================
    # Combining marks
    # =========================

    combining_marks = [
        ("Underline", "\u0332"),
        ("Double Underline", "\u0333"),
        ("Strike", "\u0336"),
        ("Slash", "\u0337"),
        ("Crossed", "\u0338"),
        ("Overline", "\u0305"),
        ("Dot Above", "\u0307"),
        ("Diaeresis", "\u0308"),
        ("Ring", "\u030A"),
        ("Tilde", "\u0303"),
        ("Macron", "\u0304"),
        ("Acute", "\u0301"),
        ("Grave", "\u0300"),
        ("Circumflex", "\u0302"),
        ("Hook", "\u0309"),
        ("Dot Below", "\u0323"),
        ("Tilde Below", "\u0330")
    ]

    for name, mark in combining_marks:
        add(
            name,
            "".join(
                c + mark
                if c != " "
                else c
                for c in text
            )
        )

    # =========================
    # Mixed combining
    # =========================

    combos = [
        "\u0650\u064e",
        "\u064e\u0650",
        "\u064f\u0650",
        "\u0650\u064f",
        "\u064e\u064f",
        "\u064f\u064e"
    ]

    for i, combo in enumerate(combos, 1):
        add(
            f"Mixed Combining {i}",
            "".join(
                c + combo
                if c != " "
                else c
                for c in text
            )
        )

    # =========================
    # Tumblr styles
    # =========================

    tumblr_italic = math_style(
        text,
        0x1D434,
        0x1D44E
    )

    tumblr_bold_italic = math_style(
        text,
        0x1D468,
        0x1D482
    )

    tumblr_bold = math_style(
        text,
        0x1D400,
        0x1D41A
    )

    tumblr_sans = math_style(
        text,
        0x1D5A0,
        0x1D5BA
    )

    add(
        "Tumblr 1",
        "𓏺 " +
        "".join(
            c + "\u0650\u064e"
            if c != " "
            else c
            for c in tumblr_italic
        ) +
        " ."
    )

    add(
        "Tumblr 2",
        "𓏺 " +
        "".join(
            c + "\u0650\u064e"
            if c != " "
            else c
            for c in tumblr_bold_italic
        ) +
        " ."
    )

    add(
        "Tumblr 3",
        "𓏺 " +
        "".join(
            c + "\u0650\u064e"
            if c != " "
            else c
            for c in tumblr_bold
        ) +
        " ."
    )

    add(
        "Tumblr 4",
        "𓏺 " +
        "".join(
            c + "\u0650\u064e"
            if c != " "
            else c
            for c in tumblr_sans
        ) +
        " ."
    )

    add(
        "Tumblr 5",
        "𓏺 " + tumblr_italic + " ."
    )

    if len(text) > 1:
        add(
            "Tumblr 6",
            "𓏺 " +
            text[0] +
            math_style(
                text[1:],
                0x1D434,
                0x1D44E
            ) +
            " ."
        )

    add(
        "Tumblr 7",
        "𓏺 " + tumblr_bold + " ."
    )

    # =========================
    # Upside Down
    # =========================

    upside = str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "ɐqɔpǝɟƃɥᴉɾʞןɯuodbɹsʇnʌʍxʎzɐqɔpǝɟƃɥᴉɾʞןɯuodbɹsʇnʌʍxʎz"
    )

    add(
        "Upside Down",
        text.translate(upside)[::-1]
    )

    # =========================
    # Decorations
    # No repeated side frame
    # =========================

    decorations = [
        ("Star Prefix", "★ ", ""),
        ("Star Suffix", "", " ★"),
        ("Sparkle Prefix", "✦ ", ""),
        ("Sparkle Suffix", "", " ✦"),
        ("Heart Prefix", "♡ ", ""),
        ("Heart Suffix", "", " ♡"),
        ("Diamond Prefix", "◆ ", ""),
        ("Diamond Suffix", "", " ◆"),
        ("Flower Prefix", "❀ ", ""),
        ("Flower Suffix", "", " ❀"),
        ("Music Prefix", "♫ ", ""),
        ("Music Suffix", "", " ♫"),
        ("Moon Prefix", "☾ ", ""),
        ("Moon Suffix", "", " ☽"),
        ("Sun Prefix", "☀ ", ""),
        ("Sun Suffix", "", " ☀"),
        ("Crown Prefix", "♛ ", ""),
        ("Crown Suffix", "", " ♛"),
        ("Special Prefix", "𖤐 ", ""),
        ("Special Suffix", "", " 𖤐"),
        ("Decor Prefix", "𖦹 ", ""),
        ("Decor Suffix", "", " 𖦹"),
        ("Wave Prefix", "⌁ ", ""),
        ("Wave Suffix", "", " ⌁"),
        ("Arrow Prefix", "➤ ", ""),
        ("Arrow Suffix", "", " ➤"),
        ("Soft Star", "⋆ ", ""),
        ("Soft Star End", "", " ⋆"),
        ("Tiny Spark", "˖ ", ""),
        ("Tiny Spark End", "", " ˖"),
        ("Cross Prefix", "† ", ""),
        ("Cross End", "", " †"),
        ("Dot Prefix", "• ", ""),
        ("Dot End", "", " •"),
        ("Plus Prefix", "⁺ ", ""),
        ("Plus End", "", " ⁺"),
        ("Moon Star", "☾⋆ ", ""),
        ("Star Moon", "", " ⋆☽"),
        ("Flower Star", "❀⋆ ", ""),
        ("Star Flower", "", " ⋆❀"),
        ("Spark Line", "✦· ", ""),
        ("Line Spark", "", " ·✦"),
    ]

    for name, left, right in decorations:
        add(
            name,
            left + text + right
        )

    # =========================
    # Tumblr / Aesthetic English
    # =========================

    def with_mark(value, mark="َِ"):
        return "".join(
            c if c == " " else c + mark
            for c in value
        )

    def with_hidden(value):
        return "".join(
            c if c == " " else c + "\u200c"
            for c in value
        )

    def map_chars(value, mapping):
        return "".join(mapping.get(c, c) for c in value)

    font_a = lambda x: math_style(x, 0x1D434, 0x1D44E)
    font_b = lambda x: math_style(x, 0x1D400, 0x1D41A)
    font_c = lambda x: math_style(x, 0x1D468, 0x1D482)
    font_d = lambda x: math_style(x, 0x1D4D0, 0x1D4EA)
    font_e = lambda x: math_style(x, 0x1D670, 0x1D68A)
    font_f = lambda x: math_style(x, 0x1D5A0, 0x1D5BA)
    font_g = lambda x: math_style(x, 0x1D5D4, 0x1D5EE)
    font_h = lambda x: math_style(x, 0x1D608, 0x1D622)
    font_i = lambda x: math_style(x, 0x1D63C, 0x1D656)

    aesthetic_fonts = [
        font_a,
        font_b,
        font_c,
        font_d,
        font_e,
        font_f,
        font_g,
        font_h,
        font_i,
    ]

    aesthetic_symbols = [
        (". ", " . ˙"),
        ("꒰ . ", " . ꒱"),
        ("⋆ . ", " . ⋆"),
        ("⋆ . ", " . ⤸"),
        ("⌯ . ", " . ⤸"),
        ("⋆ ", " ⇗"),
        ("↝ ", " ✦"),
        ("˚ ", " ⤸"),
        ("✧ ", " ↠"),
        ("⇗ ", " ⋆"),
        ("⋆ ", " ↝"),
        ("˖ ", " ↟"),
        ("⟡ ", " ⇗"),
        ("↝ ", " ✦"),
        ("✦ ", " ↠"),
        ("⋆ ", " ⤸"),
        ("⇗ ", " ˚"),
    ]

    for font in aesthetic_fonts:
        styled = font(text)

        for mark in ["َِ", "َ", "ِ"]:
            marked = with_mark(styled, mark)

            for left, right in random.sample(
                aesthetic_symbols,
                min(3, len(aesthetic_symbols))
            ):
                add(
                    "Aesthetic",
                    left + marked + right
                )

        hidden = with_hidden(styled)

        for left, right in random.sample(
            aesthetic_symbols,
            min(3, len(aesthetic_symbols))
        ):
            add(
                "Aesthetic Hidden",
                left + hidden + right
            )

    # Mixed-font patterns
    mixed_maps = [
        [font_b, font_a, font_c, font_b, font_a],
        [font_a, font_b, font_a, font_c, font_b],
        [font_c, font_b, font_a, font_b, font_c],
    ]

    for fonts in mixed_maps:
        chars = []
        for index, char in enumerate(text):
            if char == " ":
                chars.append(char)
            else:
                chars.append(fonts[index % len(fonts)](char))

        mixed_text = "".join(chars)

        add(
            "Aesthetic Mixed",
            "⋆ " + with_mark(mixed_text) + " ⇗"
        )

        add(
            "Aesthetic Mixed",
            "↝ " + with_hidden(mixed_text) + " ✦"
        )

    # Underline / combining style
    underline = "\u035f"

    underlined = "".join(
        c if c == " " else c + underline
        for c in font_b(text)
    )

    add(
        "Aesthetic Underline",
        "⌯ . " + underlined + " . ⤸"
    )

    # Hidden separator + mixed fonts
    hidden_mixed = "".join(
        c if c == " " else c + "\u200c"
        for c in font_a(text)
    )

    add(
        "Aesthetic Hidden",
        "⋆ " + hidden_mixed + " ⇗"
    )

    add(
        "Aesthetic Hidden",
        "↝ " + hidden_mixed + " ✦"
    )

    # Greek-looking mixed alphabet
    greek_mix = {
        "A": "Α", "B": "Β", "E": "Ε", "H": "Η",
        "I": "Ι", "K": "Κ", "M": "Μ", "N": "Ν",
        "O": "Ο", "P": "Ρ", "T": "Τ", "X": "Χ",
        "Y": "Υ", "Z": "Ζ"
    }

    gm = map_chars(text.upper(), greek_mix)

    add("Aesthetic Greek", "⋆ . " + with_mark(gm) + " . ⋆")
    add("Aesthetic Greek", "↝ . " + gm + " . ✦")

    # =========================
    # Additional Unicode styles
    # =========================

    style_maps = [
        (
            "Small Mix 1",
            {
                "a":"ᥲ","b":"Ⴆ","c":"ᥴ","d":"ძ","e":"ꫀ","f":"ƒ",
                "g":"ᧁ","h":"ꫝ","i":"ι","j":"נ","k":"ƙ","l":"ℓ",
                "m":"ɱ","n":"η","o":"σ","p":"ρ","q":"զ","r":"ɾ",
                "s":"ѕ","t":"τ","u":"υ","v":"ν","w":"ω","x":"х",
                "y":"ყ","z":"z"
            }
        ),
        (
            "Bold Fraktur Mix",
            {
                "a":"𝖆","b":"𝖇","c":"𝖈","d":"𝖉","e":"𝖊","f":"𝖋",
                "g":"𝖌","h":"𝖍","i":"𝖎","j":"𝖏","k":"𝖐","l":"𝖑",
                "m":"𝖒","n":"𝖓","o":"𝖔","p":"𝖕","q":"𝖖","r":"𝖗",
                "s":"𝖘","t":"𝖙","u":"𝖚","v":"𝖛","w":"𝖜","x":"𝖝",
                "y":"𝖞","z":"𝖟"
            }
        ),
        (
            "Hook Mix",
            {
                "a":"α","b":"Ⴆ","c":"ƈ","d":"ժ","e":"ҽ","f":"ƒ",
                "g":"ɠ","h":"ɧ","i":"ι","j":"ʝ","k":"ƙ","l":"ℓ",
                "m":"ɱ","n":"ɳ","o":"σ","p":"ρ","q":"զ","r":"ɾ",
                "s":"ʂ","t":"ƭ","u":"ʋ","v":"ѵ","w":"ω","x":"ҳ",
                "y":"ყ","z":"ʐ"
            }
        ),
        (
            "Ethiopic Mix",
            {
                "a":"ክ","b":"ጌ","c":"ር","d":"ժ","e":"є","f":"ƒ",
                "g":"ց","h":"հ","i":"𝑖","j":"נ","k":"ƙ","l":"ℓ",
                "m":"ɱ","n":"η","o":"σ","p":"ρ","q":"զ","r":"ɾ",
                "s":"ѕ","t":"τ","u":"υ","v":"ν","w":"ω","x":"х",
                "y":"ყ","z":"z"
            }
        ),
    ]

    for name, mapping in style_maps:
        styled = "".join(
            mapping.get(char.lower(), char)
            for char in text
        )

        add(name, styled)

    # نفس النمط مع أول حرف كبير عند الحاجة
    style_upper = {
        "A":"ꁹ","B":"Ⴆ","C":"Ƈ","D":"ժ","E":"Ɛ","F":"Ƒ",
        "G":"Ǥ","H":"Ȟ","I":"𝘐","J":"Ј","K":"Ҡ","L":"Ł",
        "M":"Μ","N":"Ň","O":"Θ","P":"Ƥ","Q":"Ꝗ","R":"Ř",
        "S":"Ƨ","T":"Ŧ","U":"Ս","V":"Ѵ","W":"Ш","X":"Ж",
        "Y":"Ү","Z":"Ƶ"
    }

    add(
        "Special Greek Mix",
        "".join(style_upper.get(c.upper(), c) for c in text)
    )

    # =========================
    # Exact User Templates
    # =========================

    def exact_font(text, font):
        return font(text)

    def exact_mix(text, fonts):
        out = ""
        index = 0

        for char in text:
            if char == " ":
                out += char
                continue

            font = fonts[index % len(fonts)]
            out += font(char)
            index += 1

        return out

    exact_templates = [
        lambda x: ". " + with_mark(font_c(x)) + " . ˙",
        lambda x: "꒰ . " + with_mark(font_e(x)) + " . ꒱",
        lambda x: "⋆ . " + with_mark(font_h(x)) + " . ⋆",
        lambda x: "⋆ . " + with_mark(font_g(x)) + " . ⤸",
        lambda x: "⌯ . " + "".join(
            c if c == " " else c + "\u035f"
            for c in font_b(x)
        ) + " . ⤸",

        lambda x: "⋆ " + with_hidden(font_a(x)) + " ⇗",
        lambda x: "↝ " + with_hidden(font_b(x)) + " ✦",
        lambda x: "˚ " + with_hidden(font_c(x)) + " ⤸",
        lambda x: "✧ " + with_hidden(font_e(x)) + " ↠",
        lambda x: "⇗ " + with_hidden(font_g(x)) + " ⋆",
        lambda x: "⋆ " + with_hidden(font_b(x)) + " ↝",
        lambda x: "˖ " + with_hidden(font_a(x)) + " ↟",
        lambda x: "⟡ " + with_hidden(font_e(x)) + " ⇗",
        lambda x: "↝ " + with_hidden(font_f(x)) + " ✦",
        lambda x: "✦ " + with_hidden(x) + " ↠",
        lambda x: "⋆ " + with_hidden(font_a(x)) + " ⤸",
        lambda x: "⇗ " + with_hidden(font_h(x)) + " ˚",

        lambda x: "↝ " + with_mark(font_f(x)) + " ✦",
        lambda x: "✧ " + with_mark(font_b(x)) + " ↟",
        lambda x: "⋆ " + with_mark(font_d(x)) + " ↠",
        lambda x: "˚ . " + with_mark(font_b(x)) + " . ⋆",
        lambda x: "⟡ . " + with_mark(font_f(x)) + " . ↝",
    ]

    for template in exact_templates:
        add("Exact Aesthetic", template(text))

    # Exact mixed-font patterns
    exact_mixes = [
        [font_c, font_c, font_a, font_a, font_c],
        [font_a, font_c, font_b, font_a, font_c],
        [font_b, font_a, font_b, font_c, font_a],
        [font_c, font_a, font_c, font_b, font_a],
        [font_g, font_h, font_g, font_h, font_g],
    ]

    for fonts in exact_mixes:
        mixed = exact_mix(text, fonts)

        add(
            "Exact Mixed",
            "⋆ . " + with_mark(mixed) + " . ⋆"
        )

        add(
            "Exact Mixed",
            "↝ " + with_hidden(mixed) + " ✦"
        )

    # =========================
    # Final cleanup
    # =========================


    # =========================
    # زخارف عربية جديدة
    # =========================

    # 1) مـ,ـعـ,ـآيـ,ـنـ,ـةّ آلـ,ـنـ,ـصـ,ـ
    parts = text.split(" ")
    style_comma = []

    for word in parts:
        chars = list(word)
        styled = "ـ,ـ".join(chars)
        style_comma.append(styled)

    results.append(
        ("Arabic Comma", "ـ,ـ".join(style_comma) + "ـ")
    )

    # 2) مِـعَ ـًآيّّنٌة آلَنٌصِـ
    marks = ["ِ", "َ", "ً", "ّ", "ٌ", "ِ"]
    styled = ""

    index = 0
    for char in text:
        if char == " ":
            styled += " "
            continue

        styled += marks[index % len(marks)] + "ـ" + char
        index += 1

    results.append(
        ("Arabic Mixed Marks", styled)
    )

    # 3) مـ۶إآيَنة إآلُنص
    arabic_mix = {
        "ا": "إآ",
        "أ": "إآ",
        "إ": "إآ",
        "آ": "إآ",
        "ع": "۶",
    }

    styled = "".join(
        arabic_mix.get(char, char)
        for char in text
    )

    results.append(
        ("Arabic Mix", styled)
    )

    # 4) مِــــــــعــــــــآيـــــــّــنـــــــٌة آلَنـــــــٌصـــ
    styled_words = []

    for word in text.split(" "):
        out = ""

        for i, char in enumerate(word):
            out += char

            if i < len(word) - 1:
                out += "ــــــــ"

            if i % 3 == 0:
                out += "ّ"
            elif i % 3 == 1:
                out += "ٌ"

        styled_words.append(out)

    results.append(
        ("Arabic Long", " ".join(styled_words))
    )

    return results

# =========================
# Arabic transformations
# =========================

ARABIC_VARIANTS = [
    {
        "ا": "ٱ", "أ": "ٲ", "إ": "ٳ", "آ": "ٵ",
        "ر": "ࢪ", "و": "ﯙ", "ك": "ڪ",
        "ع": "؏", "ه": "ۿ", "ي": "Ⴢ"
    },
    {
        "ا": "ﭑ", "أ": "ٲ", "إ": "ٳ",
        "ر": "ࢪ", "ك": "ڪ", "ع": "؏",
        "ه": "ھ", "ي": "ﯼ"
    },
    {
        "ا": "ٱ", "ر": "ࢪ", "ك": "ڪ",
        "ع": "؏", "ل": "ڵ", "ي": "ﻱ"
    },
    {
        "ا": "ﭑ", "ر": "ࢪ", "ك": "ڪ",
        "ع": "؏", "ه": "ﮪ", "ي": "ﯼ"
    }
]


ARABIC_SPECIAL = {
    "ا": ["ٱ", "ﭑ", "ﺎ"],
    "أ": ["ٲ", "ٵ"],
    "إ": ["ٳ"],
    "آ": ["ٵ"],
    "ر": ["ࢪ", "ڕ"],
    "و": ["ﯙ", "ۅ"],
    "ك": ["ڪ", "ﮏ"],
    "ع": ["؏"],
    "ه": ["ۿ", "ھ", "ﮪ"],
    "ة": ["ۃ", "هۃ"],
    "ي": ["Ⴢ", "ﯼ", "ﻱ"],
    "ى": ["ﯨ"],
    "ل": ["ڵ"],
    "ج": ["چ"],
    "ح": ["ﺣ"],
    "د": ["ډ"],
    "ز": ["ژ"],
    "ش": ["ﺷ"],
    "ص": ["ﺻ"],
    "ض": ["ﺿ"],
    "ط": ["ﻁ"],
    "ظ": ["ﻅ"],
    "ف": ["ﻑ"],
    "ق": ["ﻕ"],
    "م": ["ﻡ"],
    "ن": ["ﻥ"],
    "ب": ["ﺑ"],
    "ت": ["ﺗ"],
    "ث": ["ﺛ"],
    "خ": ["ﺧ"],
    "ذ": ["ﺫ"],
    "س": ["ﺳ"],
}


ARABIC_MARKS = [
    "َ",
    "ِ",
    "ُ",
    "ْ",
    "ّ",
    "ٰ",
    "ۛ",
    "ۧ",
    "ۂ",
]


def arabic_transform(text, mapping):
    return "".join(mapping.get(char, char) for char in text)


def arabic_special_transform(text, variant):
    result = ""

    for char in text:
        if char in variant:
            result += random.choice(variant[char])
        else:
            result += char

    return result


def add_mark(text, mark):
    result = ""

    for char in text:
        if char == " ":
            result += char
        else:
            result += char + mark

    return result


def arabic_kashida(text):
    return text.replace(" ", "ــ ")


def arabic_kashida_letters(text):
    result = []

    for char in text:
        if char == " ":
            result.append(" ")
        else:
            result.append(char)
            result.append("ــ")

    return "".join(result).rstrip("ــ")


def arabic_selective_stretch(text):
    chars = list(text)

    for i in range(len(chars) - 1):
        if chars[i] != " " and chars[i + 1] != " ":
            chars[i] += "ـ"

    return "".join(chars)


def arabic_double_stretch(text):
    return (
        text
        .replace("ا", "اا")
        .replace("ي", "يي")
        .replace("و", "وو")
    )


def arabic_custom_style(text):
    return "اެ" + "ݪ" + "اެ" + text + "يَــقِـــۅٛنِهِ"


def arabic_styles(text):
    results = []

    # =========================

    def flip_add(name, value):
        value = value.strip()
        if value and value != text and all(value != x[1] for x in results):
            results.append((name, value))

    NO_JOIN_AFTER = set("اأإآدذرزوؤةىء")

    def can_stretch(current, next_char):
        if not current or not next_char:
            return False

        if current.isspace() or next_char.isspace():
            return False

        if current in ".,،؛:!?؟-":
            return False

        return current not in NO_JOIN_AFTER and "\u0600" <= current <= "\u06ff"

    alt1 = {
        "ا":"ﺍ","أ":"ﺃ","إ":"ﺇ","آ":"ﺂ","ب":"ﺑ","ت":"ﺗ","ث":"ﺛ",
        "ج":"ﺟ","ح":"ﺣ","خ":"ﺧ","د":"ﺩ","ذ":"ﺫ","ر":"ﺭ","ز":"ﺯ",
        "س":"ﺳ","ش":"ﺷ","ص":"ﺻ","ض":"ﺿ","ط":"ﻁ","ظ":"ﻅ",
        "ع":"ﻋ","غ":"ﻏ","ف":"ﻓ","ق":"ﻗ","ك":"ﻛ","ل":"ﻟ",
        "م":"ﻣ","ن":"ﻧ","ه":"ﮬ","و":"ﻭ","ي":"ﻳ","ى":"ﻰ"
    }

    alt2 = {
        "ا":"آ","أ":"ﺃ","إ":"ﺇ","آ":"ﺂ","س":"ﺳ","ش":"ﺷ",
        "ص":"ﺻ","ض":"ﺿ","ط":"ﻁ","ظ":"ﻇ","ل":"ﻟ","ن":"ﻧ",
        "ه":"ہ","ع":"؏","ك":"ڪ","ر":"ࢪ","ي":"ی","ى":"ى"
    }

    def build_flip(mapping, mark_before="", mark_after=""):
        chars = list(text)
        out = ""

        for i, original in enumerate(chars):
            if original.isspace():
                out += original
                continue

            out += mapping.get(original, original) + mark_before

            if i + 1 < len(chars):
                next_char = chars[i + 1]

                if can_stretch(original, next_char):
                    out += "ـ" + mark_after
                else:
                    out += mark_after

        return out

    flip_add("Arabic Flip Style 1", build_flip(alt1))
    flip_add("Arabic Flip Style 2", build_flip(alt2, "َٰ", "ُـٰٓ"))
    flip_add("Arabic Flip Style 3", build_flip(alt2, "َٰ", "ُـٰٓ"))
    flip_add("Arabic Flip Style 4", build_flip(alt2, "ہٰ", "ٰٖ"))
    flip_add("Arabic Flip Style 5", build_flip(alt2, "ُِ", "َِ"))
    flip_add("Arabic Flip Style 6", build_flip(alt2, "ِٰ", "ِۢ"))
    flip_add("Arabic Flip Style 7", build_flip(alt2, "ُِ", ""))
    flip_add("Arabic Flip Style 8", build_flip(alt2, "ہٰ", "ٰٖ"))
    flip_add("Arabic Flip Style 9", build_flip(alt1, "ْ", "ھَہّ"))
    flip_add("Arabic Flip Style 10", build_flip(alt2, "َٰ", "ُِ"))

    # =========================

    def flip_add(name, value):
        value=value.strip()
        if value and value != text and all(value != x[1] for x in results):
            results.append((name,value))

    alt1={
        "ا":"ﺍ","أ":"ﺃ","إ":"ﺇ","آ":"ﺂ","ب":"ﺑ","ت":"ﺗ","ث":"ﺛ",
        "ج":"ﺟ","ح":"ﺣ","خ":"ﺧ","د":"ﺩ","ذ":"ﺫ","ر":"ﺭ","ز":"ﺯ",
        "س":"ﺳ","ش":"ﺷ","ص":"ﺻ","ض":"ﺿ","ط":"ﻁ","ظ":"ﻅ",
        "ع":"ﻋ","غ":"ﻏ","ف":"ﻓ","ق":"ﻗ","ك":"ﻛ","ل":"ﻟ",
        "م":"ﻣ","ن":"ﻧ","ه":"ﮬ","و":"ﻭ","ي":"ﻳ","ى":"ﻰ"
    }

    alt2={
        "ا":"آ","أ":"ﺃ","إ":"ﺇ","آ":"ﺂ","س":"ﺳ","ش":"ﺷ",
        "ص":"ﺻ","ض":"ﺿ","ط":"ﻁ","ظ":"ﻇ","ل":"ﻟ","ن":"ﻧ",
        "ه":"ہ","ع":"؏","ك":"ڪ","ر":"ࢪ","ي":"ی","ى":"ى"
    }

    # حروف لا تتصل بما بعدها
    no_next_join=set("اأإآدذرزوؤةى")
    
    def joinable_left(c):
        return c not in no_next_join and ("\u0600" <= c <= "\u06ff" or c in "ﺑﺗﺛﺟﺣﺧﺷﺻﺿﻃﻇﻋﻏﻓﻗﻛﻟﻣﻧﮬہڪࢪی")

    def can_stretch(a,b):
        if not a or not b:
            return False

        if a.isspace() or b.isspace():
            return False

        if a in ".,،؛:!?؟-ـ" or b in ".,،؛:!?؟-ـ":
            return False

        # الحرف السابق لازم يكون قادرًا على الاتصال بما بعده.
        # الحرف التالي يكفي أن يكون قادرًا على استقبال الاتصال.
        #
        # مثال:
        # آ + ل  = لا تطويل
        # ل + ح  = تطويل
        # ح + آ  = تطويل
        # آ + ك  = لا تطويل
        # ك + م  = تطويل

        if a in no_next_join:
            return False

        return joinable_left(a)

    def build_flip(mapping, marks, stretch=True, heavy=False, ending=""):
        chars=list(text)
        out=""
        for i,c in enumerate(chars):
            if c.isspace():
                out+=c
                continue

            x=mapping.get(c,c)

            # العلامة
            if marks:
                x+=marks[i % len(marks)]

            out+=x

            # التطويل فقط بين حرفين متصلين فعليًا
            if stretch and i+1 < len(chars):
                if can_stretch(chars[i],chars[i+1]):
                    out+="ـ" if not heavy or i%3 else "ــ"

        if ending:
            out+=ending

        return out

    # 1
    flip_add(
        "Arabic Flip Style 1",
        build_flip(alt1,[""],True,False)
    )

    # 2
    flip_add(
        "Arabic Flip Style 2",
        build_flip(alt2,["ٰ","َ","ُ","ٓ","ہ"],True,False)
    )

    # 3
    def build_flip_style3():
        chars = list(text)
        out = ""

        for i, c in enumerate(chars):
            if c.isspace():
                out += c
                continue

            out += alt2.get(c, c) + "َٰ"

            if i + 1 < len(chars) and can_stretch(chars[i], chars[i + 1]):
                out += "ـُـٰٓ"

        return out

    flip_add(
        "Arabic Flip Style 3",
        build_flip_style3()
    )

    # 4
    flip_add(
        "Arabic Flip Style 4",
        build_flip(alt2,["ہٰ","ٰٖ"],True,False)
    )

    # 5
    flip_add(
        "Arabic Flip Style 5",
        build_flip(alt2,["ُِ","َِ","ٰٖ","ّ"],True,False,"ﮭ")
    )

    # 6
    flip_add(
        "Arabic Flip Style 6",
        build_flip(alt2,["ِٰۢ","ۿۿہ"],True,False)
    )

    # 7
    flip_add(
        "Arabic Flip Style 7",
        build_flip(alt2,["ُِ"],True,False,"هـ")
    )

    # 8
    flip_add(
        "Arabic Flip Style 8",
        build_flip(alt2,["ہٰ","ٰٖ","ٰ"],True,False)
    )

    # 9
    flip_add(
        "Arabic Flip Style 9",
        build_flip(alt1,["ْھَہّ"],True,False)
    )

    # 10
    flip_add(
        "Arabic Flip Style 10",
        build_flip(
            alt2,
            ["ٰ","َِ","ۨہٰٰ","ٰٖ","ُِ"],
            True,
            True
        )
    )

    # =========================

    def flip_add(name, value):
        value = value.strip()
        if value and value != text and all(value != x[1] for x in results):
            results.append((name, value))

    arabic_alt = {
        "ا":"ﺍ","أ":"ﺃ","إ":"ﺇ","آ":"ﺂ",
        "ب":"ﺑ","ت":"ﺗ","ث":"ﺛ","ج":"ﺟ","ح":"ﺣ","خ":"ﺧ",
        "د":"ﺩ","ذ":"ﺫ","ر":"ﺭ","ز":"ﺯ","س":"ﺳ","ش":"ﺷ",
        "ص":"ﺻ","ض":"ﺿ","ط":"ﻁ","ظ":"ﻅ","ع":"ﻋ","غ":"ﻏ",
        "ف":"ﻓ","ق":"ﻗ","ك":"ﻛ","ل":"ﻟ","م":"ﻣ","ن":"ﻧ",
        "ه":"ﮬ","و":"ﻭ","ي":"ﻳ","ى":"ﻰ"
    }

    # =========================
    # قوالب عربية عامة جديدة
    # =========================

    def template_1(text):
        mapping = {
            "ع": "؏",
            "ك": "ڪ",
            "ي": "ی",
            "ه": "ہ",
        }
        out = ""
        for i, c in enumerate(text):
            out += mapping.get(c, c)
            if c not in "اأإآدذرزوؤةى " and i + 1 < len(text):
                out += "ـ"
        return out

    def template_2(text):
        mapping = {
            "ا": "ﺂ",
            "ع": "؏",
            "ك": "ڪ",
            "ه": "ہ",
            "ي": "ی",
        }
        out = ""
        for i, c in enumerate(text):
            x = mapping.get(c, c)
            if c not in " ":
                x += "َ"
            out += x
            if c not in "اأإآدذرزوؤةى " and i + 1 < len(text):
                out += "ـ"
        return out

    def template_3(text):
        mapping = {
            "ك": "ڪ",
            "ي": "ی",
            "ه": "ہ",
            "ت": "ت",
        }
        out = ""
        for c in text:
            if c == " ":
                out += " "
                continue
            out += mapping.get(c, c) + "ۿ"
        return out

    def template_4(text):
        mapping = {
            "ر": "ﯠ",
            "و": "ﯠ",
            "ح": "ح",
            "ك": "ڪ",
            "ي": "ی",
        }
        out = ""
        for c in text:
            if c == " ":
                out += " "
                continue
            out += mapping.get(c, c)
        return out + "كَ"

    def template_5(text):
        mapping = {
            "د": "د",
            "ق": "ق",
            "ي": "ی",
            "ه": "ہ",
        }
        out = ""
        for i, c in enumerate(text):
            if c == " ":
                out += " "
                continue
            out += mapping.get(c, c) + "ـِـِۧ"
        return out

    flip_add("قالب عربي 11", template_1(text))
    flip_add("قالب عربي 12", template_2(text))
    flip_add("قالب عربي 13", template_3(text))
    flip_add("قالب عربي 14", template_4(text))
    flip_add("قالب عربي 15", template_5(text))

    arabic_alt2 = {
        "ا":"آ","أ":"ﺄ","إ":"ﺈ","آ":"ﺂ",
        "س":"ﺳ","ش":"ﺷ","ص":"ﺻ","ض":"ﺿ",
        "ط":"ﻁ","ظ":"ﻇ","ل":"ﻟ","ن":"ﻧ",
        "ه":"ہ","ع":"؏","ك":"ڪ","ر":"ࢪ",
        "ي":"ی","ى":"ى"
    }

    # 1 — ﺳ‌ــــﻟﻁ‌ـــﻧ‌ﮬ‌
    out=""
    for i,c in enumerate(text):
        if c==" ":
            out+=" "
            continue
        x=arabic_alt.get(c,c)
        if i==0:
            x += "‌"
        if i%2==0:
            x += "ـ"
        if i%3==0:
            x += "ــ"
        out+=x
    flip_add("Arabic Flip Style 1",out)

    # 2 — ـ‌ٰـہ + تطويل + ٰٓ
    out=""
    for i,c in enumerate(text):
        if c==" ":
            out+=" "
            continue
        x=arabic_alt2.get(c,c)
        out += x + "‌ٰـہ"
        if i%2==0:
            out += "ٰٓ"
    flip_add("Arabic Flip Style 2",out)

    # 3 — َٰـُـٰٓ
    out=""
    for i,c in enumerate(text):
        if c==" ":
            out+=" "
            continue
        x=arabic_alt2.get(c,c)
        out += x + "َُٰٰٓ"
    flip_add("Arabic Flip Style 3",out)

    # 4 — ہ + ٰہٰٖ
    out=""
    for i,c in enumerate(text):
        if c==" ":
            out+=" "
            continue
        x=arabic_alt2.get(c,c)
        out += x + "ہ"
        if i%2==0:
            out += "ـ"
        out += "ٰہٰٖ"
    flip_add("Arabic Flip Style 4",out)

    # 5 — تشكيل متنوع + ﮭ
    marks=["ُِ","َِ","ٰٖ","ّ"]
    out=""
    j=0
    for c in text:
        if c==" ":
            out+=" "
            continue
        x=arabic_alt2.get(c,c)
        out += x + marks[j%len(marks)]
        if j%2==0:
            out+="ـ"
        j+=1
    out += "ﮭ"
    flip_add("Arabic Flip Style 5",out)

    # 6 — ۢ + ۿۿہ
    out=""
    for i,c in enumerate(text):
        if c==" ":
            out+=" "
            continue
        x=arabic_alt2.get(c,c)
        out += x + "ِٰۢ"
        if i%3==0:
            out += "ۿۿہ"
    flip_add("Arabic Flip Style 6",out)

    # 7 — ُِ + هـ
    out=""
    for i,c in enumerate(text):
        if c==" ":
            out+=" "
            continue
        x=arabic_alt2.get(c,c)
        out += x + "ُِ"
        if i%3==0:
            out += "ـ"
    out += "هـ"
    flip_add("Arabic Flip Style 7",out)

    # 8 — ہٰ + تطويلات + ٰٖ
    out=""
    for i,c in enumerate(text):
        if c==" ":
            out+=" "
            continue
        x=arabic_alt2.get(c,c)
        out += x + "ہٰ"
        if i%2==0:
            out += "ـ"
        if i%3==0:
            out += "ٰٖ"
    flip_add("Arabic Flip Style 8",out)

    # 9 — ْھَہّ + تطويلات مختلفة
    out=""
    for i,c in enumerate(text):
        if c==" ":
            out+=" "
            continue
        x=arabic_alt.get(c,c)
        out += x
        if i%2==0:
            out += "ـ"
        if i%3==0:
            out += "ــ"
        if i%4==0:
            out += "ْھَہّ"
    flip_add("Arabic Flip Style 9",out)

    # 10 — الشقلبة الثقيلة: بدائل + علامات + تطويل + هاء زخرفية
    marks=["ٰ","َِ","ۨہٰٰ","ٰٖ","ُِ"]
    out=""
    j=0
    for c in text:
        if c==" ":
            out+=" "
            continue
        x=arabic_alt2.get(c,c)
        out += x + "‌"
        if j%2==0:
            out += "ـ"
        out += marks[j%len(marks)]
        if j%3==0:
            out += "ہ"
        j+=1
    flip_add("Arabic Flip Style 10",out)


    # =========================

    def clean_arabic_tatweel(value, source_text):
        non_joining = set("اأإآدذرزوؤةى")
        src = [c for c in source_text if c != " "]
        if not src:
            return value

        out = []
        char_index = 0
        last_original = None

        for c in value:
            if c == "ـ":
                if last_original in non_joining:
                    continue
                out.append(c)
                continue

            out.append(c)

            if char_index < len(src):
                last_original = src[char_index]
                char_index += 1

        return "".join(out)
    maps = [
        {
            "ا":"ﺈ","أ":"ﺈ","إ":"ﺈ","آ":"ﺂ",
            "ل":"ﻟ","س":"ﺳ","ط":"ﻁ","ن":"ﻧ","ه":"ﮬ",
            "ع":"؏","ك":"ڪ","ر":"ࢪ","ي":"ﻳ","ى":"ﻰ"
        },
        {
            "ا":"آ","أ":"آ","إ":"آ","آ":"آ",
            "ل":"ل","س":"س","ط":"ط","ن":"ن","ه":"ہ",
            "ع":"؏","ك":"ڪ","ر":"ࢪ","ي":"ی","ى":"ى"
        },
        {
            "ا":"آ","أ":"أ","إ":"إ","آ":"آ",
            "ل":"ل","س":"س","ط":"ط","ن":"ن","ه":"ه",
            "ع":"ع","ك":"ك","ر":"ر","ي":"ي","ى":"ى"
        },
        {
            "ا":"ا","أ":"أ","إ":"إ","آ":"آ",
            "ل":"ﻟ","س":"ﺳ","ط":"ﻁ","ن":"ﻧ","ه":"ہ",
            "ع":"ع","ك":"ڪ","ر":"ࢪ","ي":"ی","ى":"ى"
        }
    ]

    mark_sets = [
        ["ٰ","ـ","ۨ","ہٰٖ"],
        ["َ","ُ","ٰ","ٓ","ۨ"],
        ["ِ","ۢ","ٰ","ۿۿہ"],
        ["ُِ","َِ","ٰٖ","ّ"],
        ["ٰ","ہٰٖ","ۨہٰٰ","َِہ"],
    ]

    def mapped_chars(src, mp):
        return "".join(mp.get(c,c) for c in src)

    # 1 — شكل ﺈ‌ﺈ‌‌ﻟﺳ‌ــــﺈ‌‌ﻟــﻁ‌ـــﻧ‌ﮬ‌‌
    v = mapped_chars(text, maps[0])
    v = v.replace("ﺈ", "ﺈ‌ﺈ‌‌", 1)
    v = v.replace("ﻟ", "ﻟ", 1)
    v = v.replace("ﺳ", "ﺳ‌ــــ")
    v = v.replace("ﻁ", "ﻁ‌ـــ")
    v = v.replace("ﻧ", "ﻧ‌")
    flip_add("Arabic Flip 01", clean_arabic_tatweel(v + "‌", text))

    # 2 — آلـ‌ٰـہسٰٓــــلـ‌ٰـہــطۨہٰٰـــنَِہهٰہٰٖ
    v = mapped_chars(text, maps[1])
    out=""
    for i,c in enumerate(v):
        if c==" ":
            out+=" "
            continue
        out += c + "‌ٰـہ"
        if i % 2 == 0:
            out += "ٰٓ"
    v=out
    flip_add("Arabic Flip 02", v)

    # 3 — علامات مركبة مع تطويلات
    out=""
    for i,c in enumerate(mapped_chars(text,maps[1])):
        if c==" ":
            out+=" "
            continue
        out += c + "َُٰٰٓ"
        if i % 3 == 1:
            out += "ـ"
    flip_add("Arabic Flip 03", clean_arabic_tatweel(out, text))

    # 4 — الہسہــــلہــطہـــنٰہٰٖهٰہٰٖ
    out=""
    for i,c in enumerate(mapped_chars(text,maps[2])):
        if c==" ":
            out+=" "
            continue
        out += c + "ہ"
        if i % 2 == 0:
            out += "ـ"
        if i % 3 == 0:
            out += "ٰہٰٖ"
    flip_add("Arabic Flip 04", clean_arabic_tatweel(out, text))

    # 5 — أُلَسًــــلَــطٌـــنًﮭ
    marks=mark_sets[3]
    out=""
    for i,c in enumerate(mapped_chars(text,maps[2])):
        if c==" ":
            out+=" "
            continue
        out += c + marks[i % len(marks)]
        if i % 2 == 0:
            out += "ـ"
        if i == len(text.replace(" ",""))-1:
            out += "ﮭ"
    flip_add("Arabic Flip 05", clean_arabic_tatweel(out, text))

    # 6 — آلِٰـِۢسِٰـِۢــــلِٰـِۢــطِٰـِۢـــنِٰـِۢۿۿہ
    out=""
    for i,c in enumerate(mapped_chars(text,maps[1])):
        if c==" ":
            out+=" "
            continue
        out += c + "ِٰۢ"
        if i % 2 == 0:
            out += "ـ"
        if i % 3 == 0:
            out += "ۿۿہ"
    flip_add("Arabic Flip 06", clean_arabic_tatweel(out, text))

    # 7 — آلُِســــلُِــطُـــنهـ
    out=""
    for i,c in enumerate(mapped_chars(text,maps[1])):
        if c==" ":
            out+=" "
            continue
        out += c + "ُِ"
        if i == 0 or i % 3 == 0:
            out += "ـ"
        if i == len(text.replace(" ",""))-1:
            out += "هـ"
    flip_add("Arabic Flip 07", clean_arabic_tatweel(out, text))

    # 8 — آلہٰسہٰــــلہٰــطہٰـــنہٰهٰہٰٖ
    out=""
    for i,c in enumerate(mapped_chars(text,maps[1])):
        if c==" ":
            out+=" "
            continue
        out += c + "ہٰ"
        if i % 2 == 0:
            out += "ـ"
        if i % 3 == 0:
            out += "ٰ"
    out += "هٰہٰٖ"
    flip_add("Arabic Flip 08", clean_arabic_tatweel(out, text))

    # 9 — ﺂﻟﺳــــﻟــﻁْـــﻧھَہّ
    v=mapped_chars(text,maps[0])
    out=""
    for i,c in enumerate(v):
        if c==" ":
            out+=" "
            continue
        out += c
        if i % 3 == 0:
            out += "ـ"
        if i % 3 == 1:
            out += "ــ"
        if i % 4 == 0:
            out += "ْ"
        if i % 5 == 0:
            out += "ھَہّ"
    flip_add("Arabic Flip 09", clean_arabic_tatweel(out, text))

    # 10 — شقلبة ثقيلة تجمع الحروف البديلة + التطويل + العلامات
    out=""
    for i,c in enumerate(mapped_chars(text,maps[i % len(maps)])):
        if c==" ":
            out+=" "
            continue
        out += c
        out += mark_sets[i % len(mark_sets)][i % len(mark_sets[i % len(mark_sets)])]
        if i % 2 == 0:
            out += "ـ"
        if i % 3 == 0:
            out += "ٰ"
        if i % 4 == 0:
            out += "ہ"
    flip_add("Arabic Flip 10", out)

    # =========================

    arabic_flip_maps = [
        {
            "ا":"ﺎ","أ":"ﺄ","إ":"ﺈ","آ":"ﺂ","ب":"ﺑ","ت":"ﺗ","ث":"ﺛ",
            "ج":"ﺟ","ح":"ﺣ","خ":"ﺧ","د":"ﺩ","ذ":"ﺫ","ر":"ﺭ","ز":"ﺯ",
            "س":"ﺳ","ش":"ﺷ","ص":"ﺻ","ض":"ﺿ","ط":"ﻃ","ظ":"ﻇ",
            "ع":"ﻋ","غ":"ﻏ","ف":"ﻓ","ق":"ﻗ","ك":"ﻛ","ل":"ﻟ",
            "م":"ﻣ","ن":"ﻧ","ه":"ﻫ","و":"ﻭ","ي":"ﻳ","ى":"ﻰ",
        },
        {
            "ا":"ﭑ","أ":"ﺃ","إ":"ﺇ","آ":"ﺁ","س":"ﺳ","ش":"ﺷ","ص":"ﺻ",
            "ض":"ﺿ","ط":"ﻁ","ظ":"ﻅ","ل":"ﻟ","م":"ﻣ","ن":"ﻧ",
            "ه":"ﮬ","ع":"؏","ك":"ڪ","ر":"ࢪ","ي":"ﯾ","ى":"ﯩ",
        },
        {
            "ا":"ﺍ","أ":"ﺃ","إ":"ﺇ","آ":"ﺁ","س":"ﺲ","ش":"ﺶ","ص":"ﺺ",
            "ض":"ﺾ","ط":"ﻂ","ظ":"ﻆ","ل":"ﻞ","م":"ﻢ","ن":"ﻦ",
            "ه":"ﻪ","ع":"ﻊ","ك":"ﻚ","ر":"ﺮ","ي":"ﻲ","ى":"ﻰ",
        },
    ]

    arabic_marks = [
        ["ٰ", "ِ"],
        ["َ", "ّ", "ٰ"],
        ["ُ", "ِ", "ٖ"],
        ["ۡ", "َ", "ّ", "ٰ"],
    ]

    def add_arabic_flip(name, value):
        value = value.strip()
        if value and value != text and all(value != old for _, old in results):
            results.append((name, value))

    # 1 — شقلبة خفيفة بحروف Unicode بديلة
    add_arabic_flip(
        "Arabic Flip 1",
        "".join(arabic_flip_maps[0].get(c, c) for c in text)
    )

    # 2 — شقلبة ثقيلة
    add_arabic_flip(
        "Arabic Flip 2",
        "".join(arabic_flip_maps[1].get(c, c) for c in text)
    )

    # 3 — شقلبة نهايات الحروف
    add_arabic_flip(
        "Arabic Flip 3",
        "".join(arabic_flip_maps[2].get(c, c) for c in text)
    )

    # 4 — حروف بديلة + تطويل
    v = "".join(arabic_flip_maps[1].get(c, c) + ("ـ" if c != " " else "")
                for c in text)
    add_arabic_flip("Arabic Flip 4", v)

    # 5 — تطويل متدرج
    v = ""
    for i, c in enumerate(text):
        v += c
        if c != " " and i % 3 != 0:
            v += "ـ"
    add_arabic_flip("Arabic Flip 5", v)

    # 6 — علامات عربية مركبة
    v = ""
    mi = 0
    marks = arabic_marks[0]
    for c in text:
        if c == " ":
            v += " "
        else:
            v += c + marks[mi % len(marks)]
            mi += 1
    add_arabic_flip("Arabic Flip 6", v)

    # 7 — حروف بديلة + علامات
    v = ""
    mi = 0
    marks = arabic_marks[1]
    for c in text:
        if c == " ":
            v += " "
        else:
            v += arabic_flip_maps[1].get(c, c)
            v += marks[mi % len(marks)]
            mi += 1
    add_arabic_flip("Arabic Flip 7", v)

    # 8 — شقلبة مع تطويلات داخلية
    v = ""
    mi = 0
    marks = arabic_marks[2]
    for c in text:
        if c == " ":
            v += " "
            continue
        v += arabic_flip_maps[0].get(c, c)
        if mi % 2 == 0:
            v += "ـ"
        v += marks[mi % len(marks)]
        mi += 1
    add_arabic_flip("Arabic Flip 8", v)

    # 9 — تكرار بصري لبعض الحروف + علامات
    duplicate_chars = set("الهسطنم")
    v = ""
    mi = 0
    for c in text:
        if c == " ":
            v += " "
            continue
        x = arabic_flip_maps[1].get(c, c)
        if c in duplicate_chars:
            x += x
        x += arabic_marks[3][mi % len(arabic_marks[3])]
        v += x
        mi += 1
    add_arabic_flip("Arabic Flip 9", v)

    # 10 — الشقلبة الثقيلة النهائية
    v = ""
    mi = 0
    for c in text:
        if c == " ":
            v += " "
            continue
        x = arabic_flip_maps[2].get(c, c)
        v += "ـ" + x + arabic_marks[3][mi % len(arabic_marks[3])]
        mi += 1
    add_arabic_flip("Arabic Flip 10", v)


    # =========================
    # زخارف عربية إضافية
    # =========================

    # 1
    style1 = "ـ,ـ".join(list(text))
    results.append(("Arabic Comma", style1))
    results.append(("Arabic Frame", "⤸:↜" + text + "↝:⤹"))


    # 2
    marks = ["ِ", "َ", "ً", "ّ", "ٌ", "ِ"]
    style2 = ""
    i = 0

    for char in text:
        if char == " ":
            style2 += " "
            continue

        style2 += char + marks[i % len(marks)]
        i += 1

    results.append(("Arabic Mixed Marks", style2))

    # 3
    style3 = text.translate(str.maketrans({
        "ع": "۶",
        "ا": "إ",
        "أ": "إ",
        "إ": "إ",
        "آ": "آ",
    }))

    results.append(("Arabic Mix", style3))

    # 4
    style4 = ""

    for word in text.split(" "):
        if not word:
            continue

        for i, char in enumerate(word):
            style4 += char

            if i < len(word) - 1:
                style4 += "ــــــــ"

        style4 += " "

    results.append(("Arabic Long", style4.strip()))


    # 1 — أشكال الحروف الأساسية
    for mapping in ARABIC_VARIANTS:
        results.append(
            ("Arabic", arabic_transform(text, mapping))
        )

    # 2 — تبديلات عربية خاصة
    for _ in range(4):
        results.append(
            ("Arabic Mixed", arabic_special_transform(text, ARABIC_SPECIAL))
        )

    # 3 — تبديل ثقيل
    heavy = text

    for old, new in [
        ("ر", "ࢪ"),
        ("ك", "ڪ"),
        ("ع", "؏"),
        ("ا", "ﭑ"),
        ("ي", "Ⴢ"),
        ("ه", "ۿ"),
        ("ة", "ۃ"),
        ("ل", "ڵ"),
    ]:
        heavy = heavy.replace(old, new)

    results.append(("Arabic Heavy", heavy))

    # 4 — كَشيدة
    results.append(
        ("Kashida", arabic_kashida(text))
    )

    # 5 — كَشيدة بين الحروف
    if len(text.replace(" ", "")) > 1:
        results.append(
            ("Kashida", arabic_kashida_letters(text))
        )

    # 6 — تمديد تدريجي
    results.append(
        ("Arabic Stretch", arabic_selective_stretch(text))
    )

    # 7 — تمديد مضاعف
    results.append(
        ("Arabic Stretch", arabic_double_stretch(text))
    )

    # 8 — تشكيل
    for mark in ARABIC_MARKS:
        results.append(
            ("Arabic Marks", add_mark(text, mark))
        )

    # 9 — تشكيل مع تبديل الحروف
    mixed = arabic_special_transform(text, ARABIC_SPECIAL)

    for mark in ["َ", "ِ", "ُ", "ّ", "ۛ"]:
        results.append(
            ("Arabic Decorated", add_mark(mixed, mark))
        )

    # 10 — تبديل + كَشيدة
    mixed_kashida = arabic_special_transform(
        text,
        ARABIC_SPECIAL
    )

    mixed_kashida = arabic_kashida(mixed_kashida)

    results.append(
        ("Arabic Kashida Mixed", mixed_kashida)
    )

    # 11 — تبديل + تمديد
    mixed_stretch = arabic_special_transform(
        text,
        ARABIC_SPECIAL
    )

    mixed_stretch = arabic_selective_stretch(
        mixed_stretch
    )

    results.append(
        ("Arabic Stretch Mixed", mixed_stretch)
    )

    # 12 — زخارف عربية إضافية
    extra1 = "".join(
        char + "ِٰۢ" if char != " " else " "
        for char in text
    )

    extra2 = "".join(
        char + "َُٰٰٓ" if char != " " else " "
        for char in text
    )

    # القالب الثالث — مطابق للنمط الأصلي
    chars = [char for char in text if char != " "]

    if chars:
        extra3 = ""

        for i, char in enumerate(text):
            if char == " ":
                extra3 += " "
            elif i == len(text.replace(" ", "")) - 1:
                extra3 += char + "ٰ"
            elif len(chars) > 1 and i == 1:
                extra3 += char + "ـ‌ٰـہہٰٰ"
            else:
                extra3 += char + "ـ‌ٰـہٰ‌ہ"
    else:
        extra3 = text

    results.append(("Arabic Extra", extra1))
    results.append(("Arabic Extra", extra2))
    results.append(("Arabic Extra", extra3))

    # ستايل ↻¹⁷l — إطالة صغيرة داخل الاسم
    chars = [i for i, char in enumerate(text) if "\u0600" <= char <= "\u06ff"]

    if len(chars) >= 2:
        pos = chars[len(chars) // 2 - 1]
        styled = text[:pos + 1] + "ـ" + text[pos + 1:]
    else:
        styled = text + "ـ"

    results.append(("Arabic Special", "↻¹⁷l" + styled))

    # 12 — لمسات Unicode مستوحاة من الأنماط المرسلة
    symbol_styles = [
        "ۿ",
        "ہ",
        "ۂ",
        "ۛ",
        "ۧ",
        "ٰ",
    ]

    for symbol in symbol_styles:
        results.append(
            ("Arabic Symbol", text + symbol)
        )

    unique_results = []
    seen = set()

    for category, value in results:
        if value and value not in seen:
            seen.add(value)
            unique_results.append((category, value))

    return unique_results

# =========================
# Combining / Tumblr
# =========================

COMBINING_MARKS = [
    "\u0300",
    "\u0301",
    "\u0302",
    "\u0303",
    "\u0304",
    "\u0307",
    "\u0308",
    "\u030a",
    "\u030c",
    "\u0332",
    "\u0333"
]


def combining_style(text, mark):
    result = ""

    for char in text:
        if char == " ":
            result += " "
        else:
            result += char + mark

    return result


def tumblr_styles(text):
    results = []

    for mark in COMBINING_MARKS:
        results.append(
            ("Tumblr", combining_style(text, mark))
        )

    # Mixed fonts
    if any(c.lower() in LOWER for c in text):
        for name in ["Bold", "Italic", "Monospace", "Fraktur", "Double"]:
            styled = apply_font(text, FONT_FAMILIES[name])
            results.append(
                ("Tumblr Mix", combining_style(styled, "\u0301"))
            )

    return results


# =========================
# Heavy styles
# =========================

def heavy_styles(text):
    results = []

    results.append(
        ("Heavy", f"𓏺 {text}")
    )

    results.append(
        ("Heavy", f"{text} 𖦹")
    )

    results.append(
        ("Heavy", f"🕷𖡻⃝֘ {text} 𖦹‌ֹ 𝆺𝅥𝆹̸𝅥")
    )

    results.append(
        ("Heavy", f"𖦹‌ֹ {text} 𝆺𝅥𝆹̸𝅥")
    )

    results.append(
        ("Heavy", f"𖡻⃝ {text}")
    )

    return results


# =========================
# Generator
# =========================

def generate_styles(text):
    results = []

    is_arabic = any(
        "\u0600" <= c <= "\u06ff"
        for c in text
    )

    is_english = any(
        c.lower() in LOWER
        for c in text
    )

    if is_english:
        for name, font in FONT_FAMILIES.items():
            results.append(
                (name, apply_font(text, font))
            )

        results.extend(english_extra(text))

    if is_arabic:
        results.extend(arabic_styles(text))

    if is_english or is_arabic:
        results.extend(tumblr_styles(text))
        results.extend(heavy_styles(text))

    # Remove duplicates
    unique = []
    seen = set()

    for category, value in results:
        value = unicodedata.normalize("NFC", value)

        if value.strip() and value not in seen:
            seen.add(value)
            unique.append((category, value))

    return unique


# =========================
# Telegram copy button
# =========================

async def send_copy_message(client, chat_id, results):
    import urllib.error

    def duplicate_key(text):
        import unicodedata

        text = unicodedata.normalize("NFC", text.strip())
        result = []

        for char in text:
            if unicodedata.combining(char):
                if result:
                    result[-1] += char
            else:
                result.append(char)

        for i, item in enumerate(result):
            if len(item) > 1:
                base = item[0]
                marks = sorted(item[1:])
                result[i] = base + "".join(marks)

        return "".join(result)


    # إزالة التكرار من كل النتائج
    unique_results = []
    seen = set()

    for category, text in results:
        if not text or not text.strip():
            continue

        key = duplicate_key(text)

        if key in seen:
            continue

        seen.add(key)
        unique_results.append((category, text))

    results = unique_results

    # تقسيم النتائج على عدة رسائل تلقائيًا
    chunk_size = 15

    for start in range(0, len(results), chunk_size):
        chunk = results[start:start + chunk_size]
        buttons = []

        for category, text in chunk:
            display_text = text

            if len(display_text) > 64:
                display_text = display_text[:61] + "..."

            buttons.append([
                {
                    "text": display_text,
                    "copy_text": {
                        "text": text
                    }
                }
            ])

        if not buttons:
            continue

        data = {
            "chat_id": chat_id,
            "text": "⟡ اختر الزخرفة للنسخ ⟡",
            "reply_markup": json.dumps(
                {"inline_keyboard": buttons},
                ensure_ascii=False
            )
        }

        url = (
            "https://api.telegram.org/bot"
            + BOT_TOKEN
            + "/sendMessage?"
            + urllib.parse.urlencode(data)
        )

        try:
            urllib.request.urlopen(url, timeout=10)

        except urllib.error.HTTPError as e:
            print(
                "SEND COPY ERROR:",
                e.read().decode("utf-8", errors="replace")
            )

        except Exception as e:
            print("SEND COPY ERROR:", repr(e))

@app.on_message(filters.command("start"))
async def start(client, message):
    if not await check_subscription(client, message.from_user.id):
        await message.reply_text(
            "⟡ يجب الاشتراك في القناة أولًا ⟡\n\n"
            "بعد الاشتراك اضغط على زر التحقق.",
            reply_markup=subscription_keyboard()
        )

        return

    is_new_user = get_user(message.from_user.id) is None

    save_user(message.from_user)

    if is_new_user:
        username = (
            f"@{message.from_user.username}"
            if message.from_user.username
            else "لا يوجد"
        )

        await client.send_message(
            DEVELOPER_ID,
            "╭━━━━━━━━━━━━━━━━━━╮\n"
            "        مستخدم جديد\n"
            "╰━━━━━━━━━━━━━━━━━━╯\n\n"
            f"الاسم: {message.from_user.first_name or 'بدون اسم'}\n"
            f"Username: {username}\n"
            f"ID: `{message.from_user.id}`\n\n"
            "تم تسجيله في قاعدة البيانات."
        )

    welcome_text = (
        "╭━━━ 𝐃𝐄𝐂𝐎𝐑 𝐁𝐎𝐓 ━━━╮\n\n"
        "𖦹 أهلاً بك في عالم الزخارف.\n"
        "𖦹 حوّل كلماتك إلى أشكال مختلفة.\n"
        "𖦦 اختر النمط الذي يعجبك وانسخه بسهولة."
    )

    if message.from_user.id == DEVELOPER_ID:
        await developer_panel.send_developer_colored_keyboard(
            message.chat.id,
            welcome_text
        )
    else:
        await send_colored_message(
            message.chat.id,
            welcome_text
        )


@app.on_message(filters.command("myid"))
async def myid(client, message):
    await message.reply_text(f"🆔 ID الخاص بك:\n`{message.from_user.id}`")

@app.on_callback_query(filters.regex("^check_subscription$"))
async def verify_subscription(client, callback_query):
    if await check_subscription(client, callback_query.from_user.id):
        await callback_query.answer("تم التحقق من الاشتراك ✓")
        await callback_query.message.delete()

        await send_colored_message(
            callback_query.message.chat.id,
            "╭━━━ 𝐃𝐄𝐂𝐎𝐑 𝐁𝐎𝐓 ━━━╮\n\n"
            "𖦹 أهلاً بك في عالم الزخارف.\n"
            "𖦹 حوّل كلماتك إلى أشكال مختلفة.\n"
            "𖦦 اختر النمط الذي يعجبك وانسخه بسهولة."
        )
    else:
        await callback_query.answer(
            "اشترك في القناة أولًا ثم اضغط تحقق.",
            show_alert=True
        )

# =========================
# Keyboard actions
# =========================

@app.on_message(filters.regex(r"^• زخرفة النص •$"))
async def decorate_mode(client, message):
    await message.reply_text(
        "أرسل الكلمة أو الجملة الآن."
    )


async def random_mode(client, message):
    await message.reply_text(
        "أرسل النص وسأختار لك مجموعة عشوائية من الزخارف."
    )


@app.on_message(filters.regex(r"^• العربي •$"))
async def arabic_mode(client, message):
    if not await check_subscription(client, message.from_user.id):
        await message.reply_text(
            "⟡ يجب الاشتراك في القناة أولًا ⟡\n\n"
            "بعد الاشتراك اضغط على زر التحقق.",
            reply_markup=subscription_keyboard()
        )


    user_modes[message.from_user.id] = "arabic"

    await message.reply_text(
        "⟡ أرسل الكلمة أو الجملة العربية الآن ⟡"
    )


@app.on_message(filters.regex(r"^• English •$"))
async def english_mode(client, message):
    if not await check_subscription(client, message.from_user.id):
        await message.reply_text(
            "⟡ يجب الاشتراك في القناة أولًا ⟡\n\n"
            "بعد الاشتراك اضغط على زر التحقق.",
            reply_markup=subscription_keyboard()
        )
        return

    user_modes[message.from_user.id] = "english"

    await message.reply_text(
        "⟡ Send your English text now ⟡"
    )



@app.on_message(filters.regex(r"^• أرقام •$"))
async def numbers_start(client, message):
    if not await check_subscription(client, message.from_user.id):
        await message.reply_text(
            "⟡ يجب الاشتراك في القناة أولًا ⟡\n\n"
            "بعد الاشتراك اضغط على زر التحقق.",
            reply_markup=subscription_keyboard()
        )
        return

    user_modes[message.from_user.id] = "numbers"

    await message.reply_text(
        "⟡ أرسل الرقم أو الوقت الآن ⟡\n"
        "مثال: 8 أو 11:12"
    )


@app.on_message(filters.regex(r"^• عن البوت •$"))
async def about(client, message):
    await message.reply_text(
        "𝐃𝐄𝐂𝐎𝐑 𝐁𝐎𝐓\n"
        "━━━━━━━━━━━━━━\n\n"
        "𖦹 زخرفة النصوص بأساليب Unicode\n"
        "𖦹 زخارف عربية وإنجليزية متنوعة\n"
        "𖦦 أنماط مركبة ولمسات خاصة\n"
        "𖦦 توليد عدد كبير من الأشكال"
    )


# =========================
# Decoration handler
# =========================

@app.on_message(filters.regex(r"^• دمج الأسماء •$"))
async def merge_names_under_development(client, message):
    await message.reply_text("الزر قيد التطوير")


@app.on_message(filters.text & ~filters.command("start"), group=1)
async def decorate(client, message):
    if not message.from_user:
        return
    if not await check_subscription(client, message.from_user.id): 
        await message.reply_text(
            "⟡ يجب الاشتراك في القناة أولًا ⟡\n\n"
            "بعد الاشتراك اضغط على زر التحقق.",
            reply_markup=subscription_keyboard()
        )
        return

    if developer_panel.MAINTENANCE_MODE and not is_developer(message.from_user.id):
        await message.reply_text(
            "⟦ البوت متوقف مؤقتًا للصيانة ⟧\n\n"
            "حاول مرة أخرى لاحقًا."
        )
        return

    text = message.text.strip()

    ignored_buttons = {
        "⟦ الإحصائيات ⟧",
        "⟦ المستخدمون ⟧",
        "⟦ الإذاعة ⟧",
        "⟦ إدارة البوت ⟧",
        "⟦ الزخارف ⟧",
        "⟦ الاشتراك ⟧",
        "⟦ السجلات ⟧",
        "⟦ تحديث ⟧",
        "⟦ الرئيسية ⟧",
        "𓏺 𝐦𝐲 𝐛𝐨𝐭 .",
        "⟦ تشغيل البوت ⟧",
        "⟦ إيقاف البوت ⟧",
        "⟦ حالة البوت ⟧",
        "⟦ رجوع ⟧",
        "• دمج الأسماء •",
        "• العربي •",
        "• English •",
        "• أرقام •",
        "• عن البوت •"
    }

    if text in ignored_buttons:
        return

    user_id = message.from_user.id
    save_user(message.from_user)
    mode = user_modes.get(user_id)

    if mode == "arabic":
        if not any("\u0600" <= char <= "\u06ff" for char in text):
            return

        results = [("Custom", arabic_custom_style(text))] + arabic_styles(text)


    elif mode == "numbers":
        if not any(char.isdigit() for char in text):
            return

        digit_sets = [
            "0123456789",
            "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗",
            "𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡",
            "𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫",
            "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵",
            "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿",
            "０１２３４５６７８９",
            "⓪①②③④⑤⑥⑦⑧⑨",
            "⁰¹²³⁴⁵⁶⁷⁸⁹",
            "₀₁₂₃₄₅₆₇₈₉",
        ]

        results = []

        for digits in digit_sets:
            table = str.maketrans("0123456789", digits)
            results.append(("Numbers", text.translate(table)))


    elif mode == "english":
        if not any(("a" <= char.lower() <= "z") for char in text):
            return

        bold_map = str.maketrans(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇"
        )

        results = [
            ("English Frame", ": 𓏺 " + text.translate(bold_map) + " ›."),
            ("Bars", english_bars(text))
        ] + english_extra(text)

        first_map = str.maketrans(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            "𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛"
        )

        chars = list(text)
        first_index = next(
            (i for i, char in enumerate(chars) if "a" <= char.lower() <= "z"),
            None
        )

        if first_index is not None:
            chars[first_index] = chars[first_index].translate(first_map)
            rest = "".join(chars[first_index + 1:]).translate(bold_map)
            fares_style = (
                "𖦹⃝֘🕷"
                + chars[first_index]
                + "ܶ𖡻‌ֹ"
                + rest
                + "︪︩〃݊𝆺𝅥"
            )
        else:
            fares_style = text

        results.insert(0, ("Fares Style", fares_style))

        vip_map = str.maketrans(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇"
        )

        vip_name = text.translate(vip_map)
        vip_style = "ᴠͥɪͣᴘͫ ➧ " + " ".join(vip_name) + " ．"

        results.insert(1, ("VIP Style", vip_style))

        ashraf_map = str.maketrans(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
            "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
        )

        ashraf_style = "𓆩𓆩 " + text.translate(ashraf_map) + " 𖣎𓅃𓆪"

        results.insert(2, ("Ashraf Style", ashraf_style))

        qamar_bold = str.maketrans(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇"
        )

        qamar_script = str.maketrans(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            "𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃"
        )

        qamar_parts = []
        for i, char in enumerate(text):
            if "a" <= char.lower() <= "z":
                upper = char.upper().translate(qamar_bold)
                lower = char.lower().translate(qamar_script)
                qamar_parts.append(f"({upper}{lower})")
            else:
                qamar_parts.append(char)

        qamar_style = "".join(qamar_parts) + "𖤤"

        results.insert(3, ("Qamar Style", qamar_style))


        results.insert(0, ("Spider", "🕷𖡻⃝֘ " + text.translate(str.maketrans(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
            "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿"
        )) + " 𖦹‌ֹ 𝆺𝅥𝆹̸𝅥"))


        results = [
            item for item in results
            if item[1].strip() != text.strip()
            and not item[1].startswith("ِـ")
            and "ــــــــ" not in item[1]
        ]

        exact = [
            item for item in results
            if item[0] in {"Exact Aesthetic", "Exact Mixed"}
        ]
        old_results = [
            item for item in results
            if item[0] not in {"Exact Aesthetic", "Exact Mixed"}
        ]
        results = exact + old_results

    else:
        return

    if not results:
        return

    mode_names = {
        "arabic": "العربي",
        "english": "English",
        "numbers": "أرقام",
    }

    try:
        developer_panel.add_log(
            f"زخرفة مستخدمة | المستخدم: {user_id} | النوع: {mode_names.get(mode, mode)}"
        )
    except Exception:
        pass

    await send_copy_message(
        client,
        message.chat.id,
        results
    )

    user_modes.pop(user_id, None)

print("Decor Bot is running...")

register_developer_panel(app)
app.run()
