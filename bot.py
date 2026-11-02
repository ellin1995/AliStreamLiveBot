"""
=============================================================================
aliSTREAM Live TV Bot - Production Ready Telegram Streaming Bot
Framework: aiogram v3 (Modern Asynchronous Python Telegram Bot Framework)
Environment: Optimized for Android Termux / Render.com / VPS / Linux / Windows
Player: Exclusive Direct VLC Player Integration (Auto-Launch)
Watermark: #Alistreamlivebot
=============================================================================
"""

import asyncio
import html
import logging
import os
import sys
import urllib.parse
from typing import List, Tuple

from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramUnauthorizedError
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

# ---------------------------------------------------------------------------
# 1. CONFIGURATION & CREDENTIALS
# ---------------------------------------------------------------------------
DEFAULT_TOKEN = "9238910404:AAFX1hGTJGENTAzvb8q6CL3QjpfR1DoAKYA"
BOT_TOKEN = os.getenv("BOT_TOKEN", DEFAULT_TOKEN).strip()

# Base server URL: Automatically uses Render URL if deployed on Render,
# or defaults to localhost for Termux / local execution.
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")
LOCAL_DEFAULT_URL = f"http://127.0.0.1:{os.getenv('PORT', '8080')}"
SERVER_BASE_URL = RENDER_EXTERNAL_URL if RENDER_EXTERNAL_URL else LOCAL_DEFAULT_URL

WATERMARK = "#Alistreamlivebot"
ITEMS_PER_PAGE = 8

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


def get_vlc_launch_url(stream_url: str) -> str:
    """Generates direct auto-launch URL for VLC Player."""
    encoded_stream = urllib.parse.quote(stream_url, safe="")
    return f"{SERVER_BASE_URL}/vlc?url={encoded_stream}"


# ---------------------------------------------------------------------------
# 3. KEYBOARD GENERATORS (EXCLUSIVE VLC - ZERO CLUTTER)
# ---------------------------------------------------------------------------
def build_channels_page_markup(page: int = 0) -> InlineKeyboardMarkup:
    """Builds clean paginated channels list (Channel names only)."""
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


def build_vlc_only_markup(channel_idx: int, return_page: int) -> InlineKeyboardMarkup:
    """
    Builds the playback keyboard:
    - Single Primary VLC Auto-Launch Button.
    - Back to Channels Menu Button.
    No other players or download buttons.
    """
    _, stream_url = CHANNEL_LIST[channel_idx]
    vlc_url = get_vlc_launch_url(stream_url)

    keyboard: List[List[InlineKeyboardButton]] = [
        # 1. Sole Primary VLC Player Auto-Launch Button
        [
            InlineKeyboardButton(
                text="🎬 تشغيل فوري في مشغل VLC",
                url=vlc_url,
            )
        ],
        # 2. Back to menu
        [
            InlineKeyboardButton(
                text="🔙 العودة لقائمة القنوات",
                callback_data=f"page:{return_page}",
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ---------------------------------------------------------------------------
# 4. MESSAGE TEXT TEMPLATES
# ---------------------------------------------------------------------------
def get_welcome_text() -> str:
    return (
        f"👋 <b>مرحباً بك في بوت aliSTREAM للبث المباشر!</b>\n\n"
        f"⚽ <b>باقة قنوات beIN SPORTS المشفرة بأعلى جودة</b>\n"
        f"📡 إجمالي القنوات المتاحة: <b>{TOTAL_CHANNELS}</b> قناة\n\n"
        f"👇 <i>اختر القناة المطلوبة للتشغيل الفوري في مشغل VLC:</i>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🏷️ <i>{WATERMARK}</i>"
    )


def get_channel_detail_text(channel_idx: int) -> str:
    channel_name, stream_url = CHANNEL_LIST[channel_idx]
    safe_name = html.escape(channel_name)
    safe_stream = html.escape(stream_url)

    return (
        f"📺 <b>القناة:</b> <code>{safe_name}</code>\n"
        f"🟢 <b>الحالة:</b> بث حي ومباشر (LIVE)\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎬 <b>المشغل الرسمي للبوت:</b> مشغل VLC Player\n\n"
        f"👇 <i>اضغط على زر <b>'تشغيل فوري في مشغل VLC'</b> أدناه لفتح البث المباشر فوراً على هاتفك بأعلى دقة وبدون أي تقطيع!</i>\n\n"
        f"🔗 <b>رابط البث المباشر (نسخ يدوي):</b>\n"
        f"<code>{safe_stream}</code>\n"
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


@dp.message(F.text.lower().in_(["start", "star", "ابدأ", "ابدا", "قنوات", "القنوات", "menu", "قائمة", "vlc"]))
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
    When any channel is clicked, shows ONLY VLC Player auto-launch button!
    """
    try:
        parts = callback.data.split(":")
        channel_idx = int(parts[1])
        return_page = int(parts[2]) if len(parts) > 2 else 0

        detail_text = get_channel_detail_text(channel_idx)
        markup = build_vlc_only_markup(channel_idx, return_page)

        await callback.message.edit_text(
            text=detail_text,
            reply_markup=markup,
            disable_web_page_preview=True,
        )
        await callback.answer()

    except Exception as exc:
        logging.error("Error opening channel: %s", exc)
        await callback.answer("⚠️ حدث خطأ أثناء فتح القناة")


@dp.callback_query(F.data == "noop")
async def noop_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer(f"الصفحة الحالية من أصل {TOTAL_PAGES}")


# ---------------------------------------------------------------------------
# 6. DIRECT VLC AUTO-LAUNCH REDIRECT ENGINE (HTTP BRIDGE)
# ---------------------------------------------------------------------------
async def render_health_handler(request: web.Request) -> web.Response:
    return web.Response(
        text="aliSTREAM VLC Live TV Bot is LIVE and running! 🟢",
        content_type="text/plain; charset=utf-8",
    )


async def vlc_auto_launch_handler(request: web.Request) -> web.Response:
    """
    Direct VLC Auto-Launcher:
    When user taps the button in Telegram, this page opens for a split-second
    and AUTOMATICALLY fires the Android Intent directly into VLC Player!
    The channel plays immediately in VLC with hardware acceleration!
    """
    stream_url = request.query.get("url", "").strip()
    if not stream_url:
        return web.Response(text="Missing stream URL", status=400)

    # Android intent syntax to directly launch VLC Player with the stream URL
    vlc_intent = (
        f"intent:{stream_url}#Intent;action=android.intent.action.VIEW;"
        f"type=video/*;package=org.videolan.vlc;end"
    )

    html_launcher = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>تشغيل في VLC</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      background: #090c12;
      color: #ffffff;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
      padding: 24px;
      text-align: center;
    }}
    .vlc-icon {{
      font-size: 70px;
      margin-bottom: 16px;
      animation: pulse 1.5s infinite;
    }}
    @keyframes pulse {{
      0%, 100% {{ transform: scale(1); }}
      50% {{ transform: scale(1.08); }}
    }}
    h1 {{
      font-size: 22px;
      font-weight: 800;
      color: #ff8800;
      margin-bottom: 8px;
    }}
    p {{
      color: #8fa0b5;
      font-size: 14px;
      line-height: 1.5;
      margin-bottom: 28px;
      max-width: 320px;
    }}
    .btn-launch {{
      background: linear-gradient(135deg, #ff8800, #ff5500);
      color: #ffffff;
      padding: 16px 36px;
      border-radius: 14px;
      font-size: 16px;
      font-weight: 800;
      text-decoration: none;
      box-shadow: 0 4px 20px rgba(255, 115, 0, 0.45);
      display: inline-block;
      transition: transform 0.15s ease;
    }}
    .btn-launch:active {{
      transform: scale(0.97);
    }}
    .footer-watermark {{
      position: absolute;
      bottom: 25px;
      color: #00e5ff;
      font-weight: 800;
      font-size: 13px;
      letter-spacing: 0.8px;
      text-shadow: 0 0 8px rgba(0, 229, 255, 0.6);
    }}
  </style>
  <script>
    const intentUrl = "{vlc_intent}";
    // Fire VLC Intent immediately on page load
    window.location.href = intentUrl;

    // Fallback re-fire
    setTimeout(function() {{
      window.location.href = intentUrl;
    }}, 1200);
  </script>
</head>
<body>
  <div class="vlc-icon">🎬</div>
  <h1>جاري فتح القناة في مشغل VLC...</h1>
  <p>يتم الآن إطلاق البث المباشر تلقائياً داخل تطبيق VLC على هاتفك بأعلى جودة وبدون تقطيع.</p>
  <a class="btn-launch" href="{vlc_intent}">🚀 تشغيل الآن في VLC</a>
  <div class="footer-watermark">#Alistreamlivebot</div>
</body>
</html>"""
    return web.Response(text=html_launcher, content_type="text/html; charset=utf-8")


async def start_http_server(port: int) -> web.AppRunner:
    app = web.Application()
    app.router.add_get("/", render_health_handler)
    app.router.add_get("/health", render_health_handler)
    app.router.add_get("/vlc", vlc_auto_launch_handler)

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
    print("🚀 بدء تشغيل بوت aliSTREAM Live TV (VLC Edition)...")
    print(f"📡 عدد القنوات المحملة: {TOTAL_CHANNELS} قناة")
    print(f"🎬 المشغل الأساسي: VLC Player (Auto-Launch)")
    print(f"🌐 رابط السيرفر: {SERVER_BASE_URL}")
    print("=" * 55 + "\n")

    web_port = int(os.getenv("PORT", "8080"))
    http_runner = None
    try:
        http_runner = await start_http_server(web_port)
        logger.info("✅ VLC Auto-Launch Bridge Server started on port %d (Live 🟢)", web_port)
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
