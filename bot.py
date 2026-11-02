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

# Render provides RENDER_EXTERNAL_URL automatically (e.g. https://your-bot.onrender.com)
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")
FALLBACK_WEB_PLAYER = (
    "https://ddywqmupodubrwlaflem.supabase.co/storage/v1/object/public/web-player/index.html"
)

LOGO_URL = "https://a.top4top.io/p_39583wl340.png"
WATERMARK = "#Alistreamlivebot"

ITEMS_PER_PAGE = 8

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
    """Returns player URL (hosted on Render if available, or Supabase)."""
    if RENDER_EXTERNAL_URL:
        return f"{RENDER_EXTERNAL_URL}/player"
    return FALLBACK_WEB_PLAYER


def get_vlc_bridge_url(stream_url: str) -> str:
    """Returns web bridge URL that triggers VLC/external player directly."""
    if RENDER_EXTERNAL_URL:
        return f"{RENDER_EXTERNAL_URL}/vlc?url={urllib.parse.quote(stream_url, safe='')}"
    return f"intent:{stream_url}#Intent;action=android.intent.action.VIEW;type=video/*;package=org.videolan.vlc;end"


# ---------------------------------------------------------------------------
# 3. KEYBOARD GENERATORS (CLEAN & PROFESSIONAL - NO DOWNLOAD BUTTONS)
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
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def build_channel_player_markup(
    channel_idx: int,
    return_page: int,
    include_intent_button: bool = True,
) -> InlineKeyboardMarkup:
    """
    Builds professional playback controls for the selected channel:
    1. Primary Web Player (Live stream with logo mask hiding channel logo & watermark).
    2. Primary External Player (VLC / MX Player on Android).
    3. One-tap Copy Stream URL.
    4. Back to Channels menu.
    * NOTE: All file download buttons are completely removed per user request.
    """
    channel_name, stream_url = CHANNEL_LIST[channel_idx]

    encoded_stream = urllib.parse.quote(stream_url, safe="")
    encoded_title = urllib.parse.quote(channel_name, safe="")
    base_player = get_web_player_base_url()
    web_player_url = f"{base_player}?url={encoded_stream}&title={encoded_title}"

    keyboard: List[List[InlineKeyboardButton]] = []

    # 1. Primary In-App Web Player (Covers channel logo + Watermark)
    keyboard.append([
        InlineKeyboardButton(
            text="▶️ تشغيل البث المباشر (المشغل الأساسي)",
            web_app=WebAppInfo(url=web_player_url),
        )
    ])

    # 2. Primary External Player Launcher (VLC / MX Player)
    vlc_url = get_vlc_bridge_url(stream_url)
    if include_intent_button:
        try:
            keyboard.append([
                InlineKeyboardButton(
                    text="🎬 تشغيل في مشغل خارجي (VLC / MX)",
                    url=vlc_url,
                )
            ])
        except Exception:
            pass

    # 3. Direct Copy Text Button (Telegram native clipboard copy)
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

    # 4. Back to Channels Menu Button
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
        f"👇 <i>اضغط على أي قناة لبدء البث المباشر فوراً:</i>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🏷️ <i>{WATERMARK}</i>"
    )


def get_channel_detail_text(channel_idx: int) -> str:
    channel_name, stream_url = CHANNEL_LIST[channel_idx]
    vlc_intent = f"intent:{stream_url}#Intent;action=android.intent.action.VIEW;type=video/*;package=org.videolan.vlc;end"

    safe_name = html.escape(channel_name)
    safe_stream = html.escape(stream_url)
    safe_vlc = html.escape(vlc_intent)

    return (
        f"📺 <b>القناة:</b> <code>{safe_name}</code>\n"
        f"🟢 <b>الحالة:</b> بث مباشر مستمر (LIVE 24/7)\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎬 <b>المشغل الخارجي الأساسي (VLC Player):</b>\n"
        f"<code>{safe_vlc}</code>\n\n"
        f"🔗 <b>رابط البث المباشر (نسخ يدوي):</b>\n"
        f"<code>{safe_stream}</code>\n\n"
        f"💡 <i>اضغط على <b>'تشغيل البث المباشر'</b> للمشاهدة فوراً مع شعار البوت، أو افتحه في <b>VLC Player</b> بأعلى جودة!</i>\n"
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


@dp.message(F.text.lower().in_(["start", "star", "ابدأ", "ابدا", "قنوات", "القنوات", "menu", "قائمة"]))
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
    """
    When any channel is clicked, immediately opens playback view with:
    - Primary Web Player (with logo masking original beIN sports logo & watermark).
    - Primary External Player launcher (VLC / MX Player).
    """
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
# 6. EMBEDDED HTTP WEB SERVER & EXTERNAL PLAYER REDIRECT BRIDGE
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


async def vlc_external_bridge_handler(request: web.Request) -> web.Response:
    """
    HTTP redirect bridge that automatically launches VLC / External Player on Android!
    """
    stream_url = request.query.get("url", "")
    if not stream_url:
        return web.Response(text="Missing stream URL", status=400)

    intent_url = f"intent:{stream_url}#Intent;action=android.intent.action.VIEW;type=video/*;package=org.videolan.vlc;end"

    # HTML page that immediately fires the Android Intent
    html_redirect = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>جاري فتح مشغل VLC...</title>
    <script>
        window.location.href = "{intent_url}";
        setTimeout(function() {{
            window.location.href = "{stream_url}";
        }}, 2000);
    </script>
</head>
<body style="background:#000;color:#fff;text-align:center;padding-top:20%;font-family:sans-serif;">
    <h2>🎬 جاري فتح القناة في مشغل VLC...</h2>
    <p>إذا لم يفتح المشغل تلقائياً، <a href="{intent_url}" style="color:#00e5ff;">اضغط هنا للتشغيل</a></p>
</body>
</html>"""
    return web.Response(text=html_redirect, content_type="text/html; charset=utf-8")


async def start_http_server(port: int) -> web.AppRunner:
    app = web.Application()
    app.router.add_get("/", render_health_handler)
    app.router.add_get("/health", render_health_handler)
    app.router.add_get("/player", web_player_handler)
    app.router.add_get("/vlc", vlc_external_bridge_handler)

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
