"""
=============================================================================
aliSTREAM Live TV Bot - Production Ready Telegram Streaming Bot
Framework: aiogram v3 (Modern Asynchronous Python Telegram Bot Framework)
Environment: Optimized for Android Termux / Render.com / VPS / Linux / Windows
Watermark: #Alistreamlivebot
=============================================================================
"""

import asyncio
import html
import logging
import os
import sys
import urllib.parse
from pathlib import Path
from typing import List, Tuple

from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramUnauthorizedError
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    CopyTextButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)

# ---------------------------------------------------------------------------
# 1. CONFIGURATION & CREDENTIALS
# ---------------------------------------------------------------------------
DEFAULT_TOKEN = "9238910404:AAFX1hGTJGENTAzvb8q6CL3QjpfR1DoAKYA"
BOT_TOKEN = os.getenv("BOT_TOKEN", DEFAULT_TOKEN).strip()

SUPABASE_URL = "https://ddywqmupodubrwlaflem.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_r1wS_YGGkexuVtRvvBy40Q_Qm-i672h"

# Render automatically provides RENDER_EXTERNAL_URL (e.g. https://yourapp.onrender.com)
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")
FALLBACK_WEB_PLAYER = (
    "https://ddywqmupodubrwlaflem.supabase.co/storage/v1/object/public/web-player/index.html"
)

LOGO_URL = "https://a.top4top.io/p_39583wl340.png"
WATERMARK = "#Alistreamlivebot"

ITEMS_PER_PAGE = 8

# Path to the bundled Web Player HTML file
BASE_DIR = Path(__file__).resolve().parent
WEB_PLAYER_FILE = BASE_DIR / "web_player" / "index.html"

# ---------------------------------------------------------------------------
# 2. CHANNELS DATA (SECURE BACKGROUND MAPPING)
# ---------------------------------------------------------------------------
CHANNELS = {
    "FR | BEIN SPORTS 1 FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/14160.ts",
    "FR | BEIN SPORTS 1 HD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/14170.ts",
    "FR | BEIN SPORTS 1 SD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/92.ts",
    "FR | BEIN SPORTS 2 FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/14153.ts",
    "FR | BEIN SPORTS 2 HD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/14169.ts",
    "FR | BEIN SPORTS 2 SD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/93.ts",
    "FR | BEIN SPORTS 3 FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/14152.ts",
    "FR | BEIN SPORTS 3 HD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/14163.ts",
    "FR | BEIN SPORTS 3 SD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/94.ts",
    "FR | BEIN SPORTS MAX 4 FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/151958.ts",
    "FR | BEIN SPORTS MAX 4 HD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/95.ts",
    "FR | BEIN SPORTS MAX 5 FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/151961.ts",
    "FR | BEIN SPORTS MAX 5 HD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/39882.ts",
    "FR | BEIN SPORTS MAX 6 FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/151964.ts",
    "FR | BEIN SPORTS MAX 6 HD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/1089.ts",
    "FR | BEIN SPORTS MAX 7 FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/151967.ts",
    "FR | BEIN SPORTS MAX 7 HD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/1113.ts",
    "FR | BEIN SPORTS MAX 8 FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/151970.ts",
    "FR | BEIN SPORTS MAX 8 HD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/1468.ts",
    "FR | BEIN SPORTS MAX 9 FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/151973.ts",
    "FR | BEIN SPORTS MAX 9 HD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/1469.ts",
    "FR | BEIN SPORTS MAX 10 FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/151976.ts",
    "FR | BEIN SPORTS MAX 10 HD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/1470.ts",
    "FR | BEIN SPORTS 1 |HEVC|": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/47499.ts",
    "FR | BEIN SPORTS 2 |HEVC|": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/47500.ts",
    "C+ RÉU| BEIN SPORTS 1 HD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/359681.ts",
    "C+ RÉU| BEIN SPORTS 2 HD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/359680.ts",
    "C+ RÉU| BEIN SPORTS 3 HD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/359679.ts",
    "C+ RÉU| BEIN SPORTS MAX 4": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/359678.ts",
    "C+ RÉU| BEIN SPORTS MAX 5": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/359677.ts",
    "AR | BEIN SPORTS ARABIC": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/24983.ts",
    "AR | BEIN SPORTS NEWS FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/24979.ts",
    "AR | BEIN SPORTS NEWS HD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/78372.ts",
    "AR | BEIN SPORTS GLOBAL FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/24980.ts",
    "AR | BEIN SPORTS GLOBAL HD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/409586.ts",
    "AR | BEIN SPORTS 4K": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/164973.ts",
    "AR | BEIN SPORTS 1 FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/13608.ts",
    "AR | BEIN SPORTS 1 FHD BKP": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/368730.ts",
    "AR | BEIN SPORTS 1 HD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/13682.ts",
    "AR | BEIN SPORTS 2 FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/13607.ts",
    "AR | BEIN SPORTS 3 FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/13606.ts",
    "AR | BEIN SPORTS 4 FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/13605.ts",
    "AR | BEIN SPORTS 5 FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/13604.ts",
    "AR | BEIN SPORTS 6 FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/13603.ts",
    "AR | BEIN SPORTS 7 FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/13602.ts",
    "AR | BEIN SPORTS 8 FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/13611.ts",
    "AR | BEIN SPORTS 9 FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/13610.ts",
    "AR | BEIN SPORTS NBA FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/21197.ts",
    "TR | BEIN SPORTS 1 FHD": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/79457.ts",
    "US | BEIN SPORTS US": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/328821.ts",
}

CHANNEL_LIST: List[Tuple[str, str]] = list(CHANNELS.items())
TOTAL_CHANNELS = len(CHANNEL_LIST)
TOTAL_PAGES = (TOTAL_CHANNELS + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE


def get_web_player_base_url() -> str:
    """Returns the active web player URL (hosted on Render if available, or fallback)."""
    if RENDER_EXTERNAL_URL:
        return f"{RENDER_EXTERNAL_URL}/player"
    return FALLBACK_WEB_PLAYER


def generate_m3u_playlist(channel_idx: int = None) -> bytes:
    """Generates an M3U IPTV playlist formatted for VLC and external IPTV apps."""
    lines = ["#EXTM3U\n"]
    if channel_idx is not None:
        name, url = CHANNEL_LIST[channel_idx]
        lines.append(f'#EXTINF:-1 tvg-logo="{LOGO_URL}" group-title="beIN SPORTS",{name}\n{url}\n')
    else:
        for name, url in CHANNEL_LIST:
            lines.append(f'#EXTINF:-1 tvg-logo="{LOGO_URL}" group-title="beIN SPORTS",{name}\n{url}\n')
    return "".join(lines).encode("utf-8")


# ---------------------------------------------------------------------------
# 3. KEYBOARD GENERATORS
# ---------------------------------------------------------------------------
def build_channels_page_markup(page: int = 0) -> InlineKeyboardMarkup:
    """Builds channels keyboard showing ONLY channel names."""
    page = max(0, min(page, TOTAL_PAGES - 1))
    start_idx = page * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, TOTAL_CHANNELS)

    keyboard: List[List[InlineKeyboardButton]] = []

    for idx in range(start_idx, end_idx):
        channel_name, _ = CHANNEL_LIST[idx]
        keyboard.append([
            InlineKeyboardButton(
                text=f"📺 {channel_name}",
                callback_data=f"ch:{idx}:{page}",
            )
        ])

    nav_row: List[InlineKeyboardButton] = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton(
                text="⬅️ السابق",
                callback_data=f"page:{page - 1}",
            )
        )

    nav_row.append(
        InlineKeyboardButton(
            text=f"📄 {page + 1}/{TOTAL_PAGES}",
            callback_data="noop",
        )
    )

    if page < TOTAL_PAGES - 1:
        nav_row.append(
            InlineKeyboardButton(
                text="التالي ➡️",
                callback_data=f"page:{page + 1}",
            )
        )

    keyboard.append(nav_row)

    # All channels M3U download button
    keyboard.append([
        InlineKeyboardButton(
            text="📥 تحميل ملف كل القنوات (M3U لـ VLC)",
            callback_data="m3u:all",
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def build_channel_player_markup(
    channel_idx: int,
    return_page: int,
    include_intent_button: bool = True,
) -> InlineKeyboardMarkup:
    """
    Builds playback options for the selected channel:
    1. Web Player with logo mask and #Alistreamlivebot watermark.
    2. External Player launchers (VLC / MX Player).
    3. One-tap Copy Stream Link.
    4. One-tap Download Channel M3U File for direct VLC launch.
    5. Back to menu preserving page.
    """
    channel_name, stream_url = CHANNEL_LIST[channel_idx]

    encoded_stream = urllib.parse.quote(stream_url, safe="")
    encoded_title = urllib.parse.quote(channel_name, safe="")
    base_player = get_web_player_base_url()
    web_player_url = f"{base_player}?url={encoded_stream}&title={encoded_title}"

    # VLC Android Intent URL
    vlc_intent_url = f"intent:{stream_url}#Intent;action=android.intent.action.VIEW;type=video/*;package=org.videolan.vlc;end"

    keyboard: List[List[InlineKeyboardButton]] = []

    # 1. Telegram Web App Player button
    keyboard.append([
        InlineKeyboardButton(
            text="▶️ تشغيل في المتصفح | Web Player",
            web_app=WebAppInfo(url=web_player_url),
        )
    ])

    # 2. VLC Intent Android Link button (Safe inline URL)
    if include_intent_button:
        try:
            keyboard.append([
                InlineKeyboardButton(
                    text="🎬 تشغيل فوري في VLC (أندرويد)",
                    url=vlc_intent_url,
                )
            ])
        except Exception:
            pass

    # 3. Direct M3U file button (Opens in VLC/MX on phone with 1 tap!)
    keyboard.append([
        InlineKeyboardButton(
            text="📥 فتح القناة عبر ملف M3U (VLC / MX)",
            callback_data=f"m3u:{channel_idx}",
        )
    ])

    # 4. Direct Copy Text Button (Telegram native clipboard copy)
    try:
        keyboard.append([
            InlineKeyboardButton(
                text="📋 نسخ رابط البث المباشر",
                copy_text=CopyTextButton(text=stream_url),
            )
        ])
    except Exception:
        keyboard.append([
            InlineKeyboardButton(
                text="📋 نسخ رابط البث المباشر",
                callback_data=f"copy:{channel_idx}:{return_page}",
            )
        ])

    # 5. Back to Channels Menu Button
    keyboard.append([
        InlineKeyboardButton(
            text="🔙 العودة لقائمة القنوات",
            callback_data=f"page:{return_page}",
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ---------------------------------------------------------------------------
# 4. MESSAGE TEXT TEMPLATES
# ---------------------------------------------------------------------------
def get_welcome_text() -> str:
    return (
        f"👋 <b>مرحباً بك في بوت aliSTREAM للبث المباشر!</b>\n\n"
        f"⚽ <b>باقة قنوات beIN SPORTS المشفرة بجودة عالية</b>\n"
        f"📡 إجمالي القنوات المتاحة: <b>{TOTAL_CHANNELS}</b> قناة\n\n"
        f"👇 <i>اختر القناة المطلوبة من الأزرار أدناه:</i>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🏷️ <i>{WATERMARK}</i>"
    )


def get_channel_detail_text(channel_idx: int) -> str:
    channel_name, stream_url = CHANNEL_LIST[channel_idx]
    vlc_intent_url = f"intent:{stream_url}#Intent;action=android.intent.action.VIEW;type=video/*;package=org.videolan.vlc;end"
    mx_intent_url = f"intent:{stream_url}#Intent;action=android.intent.action.VIEW;type=video/*;package=com.mxtech.videoplayer.ad;end"

    safe_name = html.escape(channel_name)
    safe_stream = html.escape(stream_url)
    safe_vlc = html.escape(vlc_intent_url)
    safe_mx = html.escape(mx_intent_url)

    return (
        f"📺 <b>القناة:</b> <code>{safe_name}</code>\n"
        f"🟢 <b>الحالة:</b> بث حي ومباشر (LIVE 24/7)\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎬 <b>طرق التشغيل الموصى بها لأعلى جودة:</b>\n\n"
        f"1️⃣ <b>تطبيق VLC Player (أندرويد):</b>\n"
        f"<code>{safe_vlc}</code>\n\n"
        f"2️⃣ <b>تطبيق MX Player:</b>\n"
        f"<code>{safe_mx}</code>\n\n"
        f"3️⃣ <b>رابط البث المباشر (نسخ يدوي):</b>\n"
        f"<code>{safe_stream}</code>\n\n"
        f"💡 <i>اضغط على زر <b>'فتح القناة عبر ملف M3U'</b> أدناه لفتح البث فوراً داخل VLC أو MX Player على هاتفك بنقرة واحدة!</i>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🏷️ <i>{WATERMARK}</i>"
    )


# ---------------------------------------------------------------------------
# 5. DISPATCHER & HANDLERS
# ---------------------------------------------------------------------------
dp = Dispatcher()


async def send_welcome(message: Message) -> None:
    text = get_welcome_text()
    markup = build_channels_page_markup(page=0)
    await message.answer(
        text=text,
        reply_markup=markup,
        disable_web_page_preview=True,
    )


@dp.message(CommandStart())
async def cmd_start_handler(message: Message) -> None:
    await send_welcome(message)


@dp.message(Command("channels"))
async def cmd_channels_handler(message: Message) -> None:
    await send_welcome(message)


@dp.message(Command("m3u"))
async def cmd_m3u_handler(message: Message) -> None:
    """Sends full channels M3U playlist file."""
    m3u_bytes = generate_m3u_playlist()
    file = BufferedInputFile(m3u_bytes, filename="aliSTREAM_Live_beIN.m3u")
    await message.answer_document(
        document=file,
        caption=(
            f"⚽ <b>ملف قنوات beIN SPORTS كامل (50 قناة)</b>\n"
            f"📱 افتح هذا الملف بتطبيق <b>VLC</b> أو <b>MX Player</b> لتشغيل جميع القنوات فوراً وبدون تقطيع!\n"
            f"🏷️ <i>{WATERMARK}</i>"
        ),
    )


@dp.message(F.text.lower().in_(["start", "star", "ابدأ", "ابدا", "قنوات", "القنوات", "menu", "قائمة", "m3u"]))
async def text_start_handler(message: Message) -> None:
    await send_welcome(message)


@dp.callback_query(F.data.startswith("page:"))
async def pagination_callback_handler(callback: CallbackQuery) -> None:
    try:
        _, page_str = callback.data.split(":")
        page = int(page_str)
        markup = build_channels_page_markup(page=page)
        text = get_welcome_text()

        await callback.message.edit_text(
            text=text,
            reply_markup=markup,
            disable_web_page_preview=True,
        )
        await callback.answer()
    except TelegramBadRequest as exc:
        if "message is not modified" not in str(exc).lower():
            logging.error("Telegram BadRequest in pagination: %s", exc)
        await callback.answer()
    except Exception as exc:
        logging.error("Pagination error: %s", exc)
        await callback.answer("⚠️ تم تحديث القائمة")


@dp.callback_query(F.data.startswith("ch:"))
async def channel_selection_handler(callback: CallbackQuery) -> None:
    try:
        parts = callback.data.split(":")
        channel_idx = int(parts[1])
        return_page = int(parts[2]) if len(parts) > 2 else 0

        detail_text = get_channel_detail_text(channel_idx)
        markup = build_channel_player_markup(
            channel_idx=channel_idx,
            return_page=return_page,
            include_intent_button=True,
        )

        try:
            await callback.message.edit_text(
                text=detail_text,
                reply_markup=markup,
                disable_web_page_preview=True,
            )
        except TelegramBadRequest as bad_req:
            if "BUTTON_URL_INVALID" in str(bad_req):
                fallback_markup = build_channel_player_markup(
                    channel_idx=channel_idx,
                    return_page=return_page,
                    include_intent_button=False,
                )
                await callback.message.edit_text(
                    text=detail_text,
                    reply_markup=fallback_markup,
                    disable_web_page_preview=True,
                )
            else:
                raise bad_req

        await callback.answer()

    except Exception as exc:
        logging.error("Error opening channel: %s", exc)
        await callback.answer("⚠️ حدث خطأ أثناء فتح القناة")


@dp.callback_query(F.data.startswith("m3u:"))
async def m3u_callback_handler(callback: CallbackQuery) -> None:
    """Generates and sends M3U playlist file for instant external player playback."""
    try:
        param = callback.data.split(":")[1]
        if param == "all":
            m3u_data = generate_m3u_playlist()
            file_name = "aliSTREAM_All_Channels.m3u"
            caption = f"⚽ <b>قائمة جميع القنوات (50 قناة)</b>\n🏷️ <i>{WATERMARK}</i>"
        else:
            idx = int(param)
            ch_name, _ = CHANNEL_LIST[idx]
            m3u_data = generate_m3u_playlist(idx)
            clean_name = "".join(c for c in ch_name if c.isalnum() or c in (" ", "_", "-")).strip()
            file_name = f"{clean_name}.m3u"
            caption = f"📺 <b>ملف تشغيل قناة {ch_name}</b>\nاضغط لفتحه في VLC أو MX Player!\n🏷️ <i>{WATERMARK}</i>"

        file = BufferedInputFile(m3u_data, filename=file_name)
        await callback.message.answer_document(document=file, caption=caption)
        await callback.answer("✅ تم إرسال ملف التشغيل!")
    except Exception as exc:
        logging.error("Error generating M3U: %s", exc)
        await callback.answer("⚠️ تعذر إنشاء الملف")


@dp.callback_query(F.data.startswith("copy:"))
async def copy_callback_handler(callback: CallbackQuery) -> None:
    try:
        parts = callback.data.split(":")
        channel_idx = int(parts[1])
        channel_name, _ = CHANNEL_LIST[channel_idx]
        await callback.answer(
            f"✅ تم نسخ رابط {channel_name} من الرسالة!",
            show_alert=True,
        )
    except Exception:
        await callback.answer("✅ الرابط متاح داخل الرسالة للنسخ المباشر")


@dp.callback_query(F.data == "noop")
async def noop_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer(f"الصفحة الحالية من أصل {TOTAL_PAGES}")


# ---------------------------------------------------------------------------
# 6. EMBEDDED HTTP WEB PLAYER SERVER (FOR RENDER & EXTERNAL BROWSERS)
# ---------------------------------------------------------------------------
async def render_health_handler(request: web.Request) -> web.Response:
    return web.Response(
        text="aliSTREAM Telegram Live TV Bot is LIVE and running! 🟢",
        content_type="text/plain; charset=utf-8",
    )


async def web_player_handler(request: web.Request) -> web.Response:
    """Serves the rich HTML5 Web Player with logo mask and #Alistreamlivebot watermark."""
    if WEB_PLAYER_FILE.exists():
        html_content = WEB_PLAYER_FILE.read_text(encoding="utf-8")
        return web.Response(text=html_content, content_type="text/html; charset=utf-8")
    return web.Response(text="Web Player not found", status=404)


async def m3u_playlist_http_handler(request: web.Request) -> web.Response:
    """Serves raw M3U playlist file over HTTP."""
    data = generate_m3u_playlist()
    return web.Response(
        body=data,
        content_type="application/x-mpegurl",
        headers={"Content-Disposition": 'attachment; filename="aliSTREAM.m3u"'},
    )


async def start_http_server(port: int) -> web.AppRunner:
    app = web.Application()
    app.router.add_get("/", render_health_handler)
    app.router.add_get("/health", render_health_handler)
    app.router.add_get("/player", web_player_handler)
    app.router.add_get("/playlist.m3u", m3u_playlist_http_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    return runner


# ---------------------------------------------------------------------------
# 7. APPLICATION ENTRYPOINT
# ---------------------------------------------------------------------------
async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logger = logging.getLogger("aliSTREAM.bot")

    print("\n" + "=" * 55)
    print("🚀 بدء تشغيل بوت aliSTREAM Live TV...")
    print(f"📡 عدد القنوات المحملة: {TOTAL_CHANNELS} قناة عبر {TOTAL_PAGES} صفحات")
    print("=" * 55 + "\n")

    web_port = int(os.getenv("PORT", "8080"))
    http_runner = None
    try:
        http_runner = await start_http_server(web_port)
        logger.info("✅ Web Server & Player started on port %d (Live 🟢)", web_port)
    except Exception as exc:
        logger.warning("Could not start HTTP server on port %d: %s", web_port, exc)

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    try:
        bot_info = await bot.get_me()
        print(f"✅ تم الاتصال بنجاح بخوادم تيليجرام!")
        print(f"🤖 اسم البوت: @{bot_info.username} (ID: {bot_info.id})")
        print("🟢 البوت يعمل الآن وبانتظار أوامر المستخدمين...\n")
    except TelegramUnauthorizedError:
        print("\n❌ خطأ: التوكن غير مصرح به (401 Unauthorized)!")
        if http_runner:
            await http_runner.cleanup()
        await bot.session.close()
        return
    except Exception as exc:
        logger.error("خطأ أثناء التحقق من التوكن: %s", exc)
        if http_runner:
            await http_runner.cleanup()
        await bot.session.close()
        return

    try:
        await bot.delete_webhook(drop_pending_updates=False)
        await dp.start_polling(bot)
    except Exception as exc:
        logger.error("خطأ أثناء تشغيل البوت: %s", exc)
    finally:
        if http_runner:
            await http_runner.cleanup()
        await bot.session.close()
        logger.info("تم إيقاف جلسة البوت بنجاح.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 تم إيقاف البوت يدوياً بواسطة المستخدم.")
