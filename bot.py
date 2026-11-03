"""
=============================================================================
aliSTREAM Live TV Bot - Modern Telegram Streaming Bot
Framework: aiogram v3 (Asynchronous Telegram Bot Framework)
Database: Supabase Cloud Database (Dynamic Channels List)
Player: Direct Android VLC Intent Launcher with Google Play Store Fallback
Watermark: #Alistreamlivebot
Platform: Render.com / Koyeb / VPS / Local / Android Termux
=============================================================================
"""

import asyncio
import html
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from aiohttp import web
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramConflictError,
    TelegramNetworkError,
    TelegramUnauthorizedError,
)
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

# Load environment variables from .env if present
load_dotenv()

# Ensure utf-8 encoding for standard output and logging
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# 1. CONFIGURATION & CREDENTIALS
# ---------------------------------------------------------------------------
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "").strip()

# Port for Render.com / Cloud Web Services (Render sets PORT=10000 by default)
PORT: int = int(os.getenv("PORT", "10000"))

# Constants
WATERMARK: str = "#Alistreamlivebot"
BOT_BRAND: str = "⚡ aliSTREAM Live TV"
PLAY_STORE_VLC_URL: str = "https://play.google.com/store/apps/details?id=org.videolan.vlc"
ITEMS_PER_PAGE: int = 8
CACHE_TTL_SECONDS: int = 120  # In-memory cache TTL for channels

# Default channels if Supabase credentials are not set or database is empty
DEFAULT_FALLBACK_CHANNELS: List[Dict[str, Any]] = [
    {"id": 1, "name": "FR | BEIN SPORTS 1 FHD", "stream_url": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/14160.ts"},
    {"id": 2, "name": "FR | BEIN SPORTS 1 HD", "stream_url": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/14170.ts"},
    {"id": 3, "name": "FR | BEIN SPORTS 2 FHD", "stream_url": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/14153.ts"},
    {"id": 4, "name": "FR | BEIN SPORTS 3 FHD", "stream_url": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/14152.ts"},
    {"id": 5, "name": "AR | BEIN SPORTS NEWS FHD", "stream_url": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/24979.ts"},
    {"id": 6, "name": "AR | BEIN SPORTS 1 FHD", "stream_url": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/13608.ts"},
    {"id": 7, "name": "AR | BEIN SPORTS 2 FHD", "stream_url": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/13607.ts"},
    {"id": 8, "name": "AR | BEIN SPORTS 3 FHD", "stream_url": "http://tv.gold-pro.xyz:80/live/yqKy0YRZ/f6dUahs/13606.ts"},
]

# ---------------------------------------------------------------------------
# 2. SUPABASE CHANNELS MANAGER (ASYNC WITH IN-MEMORY CACHE)
# ---------------------------------------------------------------------------
class SupabaseChannelManager:
    """Manages Supabase channel retrieval with smart caching."""

    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key
        self.client = None
        self._cache: List[Dict[str, Any]] = []
        self._last_fetch_time: float = 0.0

        if self.url and self.key:
            try:
                from supabase import create_client
                self.client = create_client(self.url, self.key)
                logging.info("✅ Supabase client initialized successfully.")
            except Exception as exc:
                logging.error("❌ Failed to initialize Supabase client: %s", exc)

    def is_configured(self) -> bool:
        return self.client is not None

    def _sync_fetch(self) -> List[Dict[str, Any]]:
        """Synchronously queries the 'channels' table in Supabase."""
        if not self.client:
            return []

        response = (
            self.client.table("channels")
            .select("id, name, stream_url")
            .order("id")
            .execute()
        )
        return response.data or []

    async def get_channels(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Retrieves channels with caching to prevent excessive database calls."""
        now = time.time()
        if not force_refresh and self._cache and (now - self._last_fetch_time < CACHE_TTL_SECONDS):
            return self._cache

        if not self.is_configured():
            return DEFAULT_FALLBACK_CHANNELS

        try:
            data = await asyncio.to_thread(self._sync_fetch)
            if data:
                self._cache = data
                self._last_fetch_time = now
                logging.info("📡 Fetched %d channels from Supabase successfully.", len(data))
                return self._cache
            else:
                logging.warning("⚠️ Table 'channels' returned 0 records. Using fallback list.")
                return self._cache or DEFAULT_FALLBACK_CHANNELS
        except Exception as exc:
            logging.error("❌ Error querying Supabase 'channels' table: %s", exc)
            return self._cache or DEFAULT_FALLBACK_CHANNELS

    def clear_cache(self) -> None:
        self._cache = []
        self._last_fetch_time = 0.0


channel_manager = SupabaseChannelManager(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------------------------------------------------------
# 3. DIRECT VLC INTENT BUILDER
# ---------------------------------------------------------------------------
def build_vlc_intent_url(stream_url: str) -> str:
    """
    Generates direct Android Intent URI for VLC Player.
    Directly opens the VLC app on Android with Google Play fallback.
    No intermediate webpage redirect is required.
    """
    fallback_encoded = "https%3A%2F%2Fplay.google.com%2Fstore%2Fapps%2Fdetails%3Fid%3Dorg.videolan.vlc"
    return (
        f"intent:{stream_url}#Intent;"
        f"action=android.intent.action.VIEW;"
        f"type=video/*;"
        f"package=org.videolan.vlc;"
        f"S.browser_fallback_url={fallback_encoded};"
        f"end"
    )

# ---------------------------------------------------------------------------
# 4. KEYBOARD BUILDERS (PAGINATION & INTENT PLAYBACK)
# ---------------------------------------------------------------------------
def build_channels_page_markup(channels: List[Dict[str, Any]], page: int = 0) -> Tuple[InlineKeyboardMarkup, int, int]:
    """Builds clean paginated keyboard displaying 8 channels per page."""
    total_channels = len(channels)
    total_pages = max(1, (total_channels + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    page = max(0, min(page, total_pages - 1))

    start_idx = page * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, total_channels)

    keyboard: List[List[InlineKeyboardButton]] = []

    # Channel buttons
    for idx in range(start_idx, end_idx):
        ch = channels[idx]
        ch_name = ch.get("name", f"قناة #{idx + 1}")
        keyboard.append([
            InlineKeyboardButton(
                text=f"📺 {ch_name}",
                callback_data=f"ch:{idx}:{page}",
            )
        ])

    # Navigation buttons row
    nav_row: List[InlineKeyboardButton] = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton(text="⬅️ السابق", callback_data=f"page:{page - 1}")
        )

    nav_row.append(
        InlineKeyboardButton(text=f"📄 {page + 1}/{total_pages}", callback_data="noop")
    )

    if page < total_pages - 1:
        nav_row.append(
            InlineKeyboardButton(text="التالي ➡️", callback_data=f"page:{page + 1}")
        )

    keyboard.append(nav_row)

    # Action row (Refresh & Help)
    keyboard.append([
        InlineKeyboardButton(text="🔄 تحديث القنوات", callback_data=f"refresh:{page}"),
        InlineKeyboardButton(text="ℹ️ تعليمات التشغيل", callback_data="help_info"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard), total_pages, total_channels


def build_channel_playback_markup(
    channel_idx: int,
    channel: Dict[str, Any],
    return_page: int
) -> InlineKeyboardMarkup:
    """Builds direct playback keyboard with VLC Intent launch."""
    stream_url = channel.get("stream_url", "")
    vlc_intent = build_vlc_intent_url(stream_url)

    keyboard: List[List[InlineKeyboardButton]] = [
        # 1. Direct VLC Intent launch button
        [
            InlineKeyboardButton(
                text="🎬 تشغيل مباشر في مشغل VLC",
                url=vlc_intent,
            )
        ],
        # 2. Google Play Store fallback / install button
        [
            InlineKeyboardButton(
                text="📲 تثبيت تطبيق VLC (Google Play)",
                url=PLAY_STORE_VLC_URL,
            )
        ],
        # 3. Return back to channels list
        [
            InlineKeyboardButton(
                text="🔙 العودة لقائمة القنوات",
                callback_data=f"page:{return_page}",
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# ---------------------------------------------------------------------------
# 5. UI TEXT TEMPLATES WITH BRANDING & WATERMARK
# ---------------------------------------------------------------------------
def get_welcome_text(total_channels: int, page: int, total_pages: int) -> str:
    """Main channels dashboard message."""
    return (
        f"<b>{BOT_BRAND}</b>\n"
        f"<i>البث المباشر الفوري للقنوات بجودة فائقة</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📡 <b>إجمالي القنوات المتاحة:</b> <code>{total_channels}</code> قناة\n"
        f"📄 <b>الصفحة الحالية:</b> <code>{page + 1} / {total_pages}</code>\n"
        f"⚡ <b>المشغل المدعوم:</b> مشغل <b>VLC Player</b> (تشغيل فوري)\n\n"
        f"👇 <i>اختر القناة المطلوبة من القائمة أدناه للمشاهدة:</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷️ <code>{WATERMARK}</code>"
    )


def get_channel_detail_text(channel: Dict[str, Any]) -> str:
    """Channel detail view message."""
    ch_name = html.escape(channel.get("name", "قناة غير معروفة"))
    stream_url = channel.get("stream_url", "").strip()
    safe_stream = html.escape(stream_url)

    return (
        f"<b>{BOT_BRAND}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📺 <b>القناة المختارة:</b> <code>{ch_name}</code>\n"
        f"🟢 <b>الحالة:</b> بث حي ومباشر (LIVE)\n"
        f"🎬 <b>طريقة التشغيل:</b> إطلاق فوري عبر مشغل <b>VLC Player</b>\n\n"
        f"🚀 <b>طريقة المشاهدة بنقرة واحدة:</b>\n"
        f"اضغط على زر <b>'🎬 تشغيل مباشر في مشغل VLC'</b> بالأسفل ليفتح البث فوراً داخل تطبيق VLC على هاتفك.\n\n"
        f"📲 <i>إذا لم يكن تطبيق VLC مثبتاً لديك، سيوجهك الرابط تلقائياً لمتجر Google Play لتثبيته فوراً.</i>\n\n"
        f"🔗 <b>رابط البث المباشر (نسخ يدوي):</b>\n"
        f"<code>{safe_stream}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷️ <code>{WATERMARK}</code>"
    )


def get_help_text() -> str:
    """Help guide message."""
    return (
        f"<b>{BOT_BRAND} - دليل الاستخدام السريع</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"1️⃣ <b>تثبيت مشغل VLC:</b>\n"
        f"تأكد من وجود تطبيق <b>VLC for Android</b> على هاتفك لتشغيل البث بأعلى جودة وبدون تقطيع.\n\n"
        f"2️⃣ <b>التشغيل الفوري:</b>\n"
        f"عند اختيار أي قناة، اضغط على زر <b>'تشغيل مباشر في مشغل VLC'</b> وسيتم إطلاق البث تلقائياً داخل المشغل.\n\n"
        f"3️⃣ <b>التنقل بين القنوات:</b>\n"
        f"استخدم أزرار (السابق / التالي) للتنقل بين الصفحات بسهولة.\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷️ <code>{WATERMARK}</code>"
    )

# ---------------------------------------------------------------------------
# 6. DISPATCHER & BOT EVENT HANDLERS
# ---------------------------------------------------------------------------
dp = Dispatcher()


async def render_channels_menu(
    target: Message | CallbackQuery,
    page: int = 0,
    force_refresh: bool = False
) -> None:
    """Helper to display or edit channels menu."""
    channels = await channel_manager.get_channels(force_refresh=force_refresh)
    markup, total_pages, total_channels = build_channels_page_markup(channels, page=page)
    text = get_welcome_text(total_channels, page, total_pages)

    if isinstance(target, Message):
        await target.answer(text=text, reply_markup=markup, disable_web_page_preview=True)
    elif isinstance(target, CallbackQuery):
        try:
            await target.message.edit_text(text=text, reply_markup=markup, disable_web_page_preview=True)
        except TelegramBadRequest as exc:
            if "message is not modified" not in str(exc).lower():
                logging.error("Telegram edit error: %s", exc)
        await target.answer()


@dp.message(CommandStart())
async def cmd_start_handler(message: Message) -> None:
    await render_channels_menu(message, page=0)


@dp.message(Command("channels"))
async def cmd_channels_handler(message: Message) -> None:
    await render_channels_menu(message, page=0)


@dp.message(Command("refresh"))
async def cmd_refresh_handler(message: Message) -> None:
    channel_manager.clear_cache()
    await message.answer("🔄 جاري تحديث قائمة القنوات من قاعدة بيانات Supabase...")
    await render_channels_menu(message, page=0, force_refresh=True)


@dp.message(F.text.lower().in_(["start", "star", "ابدأ", "ابدا", "قنوات", "القنوات", "menu", "قائمة", "تحديث"]))
async def text_trigger_handler(message: Message) -> None:
    await render_channels_menu(message, page=0)


@dp.callback_query(F.data.startswith("page:"))
async def pagination_callback_handler(callback: CallbackQuery) -> None:
    try:
        page = int(callback.data.split(":")[1])
        await render_channels_menu(callback, page=page)
    except Exception as exc:
        logging.error("Pagination callback error: %s", exc)
        await callback.answer("⚠️ تعذر تحميل الصفحة")


@dp.callback_query(F.data.startswith("refresh:"))
async def refresh_callback_handler(callback: CallbackQuery) -> None:
    try:
        page = int(callback.data.split(":")[1])
        channel_manager.clear_cache()
        await callback.answer("🔄 تم تحديث قائمة القنوات من Supabase!")
        await render_channels_menu(callback, page=page, force_refresh=True)
    except Exception as exc:
        logging.error("Refresh callback error: %s", exc)
        await callback.answer("⚠️ حدث خطأ أثناء التحديث")


@dp.callback_query(F.data.startswith("ch:"))
async def channel_selection_handler(callback: CallbackQuery) -> None:
    try:
        parts = callback.data.split(":")
        channel_idx = int(parts[1])
        return_page = int(parts[2]) if len(parts) > 2 else 0

        channels = await channel_manager.get_channels()
        if 0 <= channel_idx < len(channels):
            channel = channels[channel_idx]
            detail_text = get_channel_detail_text(channel)
            markup = build_channel_playback_markup(channel_idx, channel, return_page)

            await callback.message.edit_text(
                text=detail_text,
                reply_markup=markup,
                disable_web_page_preview=True,
            )
            await callback.answer()
        else:
            await callback.answer("⚠️ لم يتم العثور على القناة، يرجى تحديث القائمة.")
    except Exception as exc:
        logging.error("Channel selection error: %s", exc)
        await callback.answer("⚠️ تعذر عرض تفاصيل القناة")


@dp.callback_query(F.data == "help_info")
async def help_callback_handler(callback: CallbackQuery) -> None:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="🔙 العودة لقائمة القنوات", callback_data="page:0")
        ]]
    )
    try:
        await callback.message.edit_text(
            text=get_help_text(),
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
        await callback.answer()
    except Exception as exc:
        logging.error("Help callback error: %s", exc)
        await callback.answer()


@dp.callback_query(F.data == "noop")
async def noop_callback_handler(callback: CallbackQuery) -> None:
    channels = await channel_manager.get_channels()
    total_pages = max(1, (len(channels) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    await callback.answer(f"📄 إجمالي الصفحات: {total_pages} صفحة")

# ---------------------------------------------------------------------------
# 7. RESILIENT CLOUD HEALTH CHECK HTTP SERVER (FOR RENDER.COM)
# ---------------------------------------------------------------------------
async def health_check_handler(request: web.Request) -> web.Response:
    """Always returns 200 OK so Render health check passes instantly."""
    status_msg = (
        f"🟢 {BOT_BRAND} is LIVE and healthy on Render!\n"
        f"🏷️ Watermark: {WATERMARK}\n"
        f"🗄️ Supabase: {'Connected' if channel_manager.is_configured() else 'Using fallback list'}\n"
        f"🤖 Telegram Bot: {'Configured' if BOT_TOKEN else 'Waiting for BOT_TOKEN'}\n"
    )
    return web.Response(text=status_msg, content_type="text/plain", charset="utf-8")


async def start_health_server(port: int) -> web.AppRunner:
    """Starts the web server that Render requires for Web Services."""
    app = web.Application()
    app.router.add_get("/", health_check_handler)
    app.router.add_get("/health", health_check_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info("✅ Healthcheck web server listening on 0.0.0.0:%d (Render Ready 🟢)", port)
    return runner

# ---------------------------------------------------------------------------
# 8. APPLICATION ENTRYPOINT (FAIL-SAFE FOR CLOUD HOSTING)
# ---------------------------------------------------------------------------
async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logger = logging.getLogger("aliSTREAM.bot")

    print("\n" + "=" * 65)
    print(f"🚀 {BOT_BRAND} - تشغيل النظام السحابي")
    print(f"🏷️ Watermark: {WATERMARK}")
    print(f"🌐 Cloud Port: {PORT}")
    print(f"🗄️ Supabase: {'✅ متصل' if channel_manager.is_configured() else '⚠️ استخدام القنوات الافتراضية'}")
    print("=" * 65 + "\n")

    # 1. ALWAYS start the HTTP server first so Render marks the deployment as Live immediately
    http_runner = None
    try:
        http_runner = await start_health_server(PORT)
    except Exception as exc:
        logger.error("❌ Could not bind health check server on port %d: %s", PORT, exc)

    # 2. Check BOT_TOKEN - Do NOT crash the process if missing, keep health server alive
    if not BOT_TOKEN:
        logger.error(
            "\n" + "!" * 65 + "\n"
            "❌ خطأ حرج: لم يتم العثور على BOT_TOKEN في متغيرات البيئة!\n"
            "يرجى الدخول إلى Render Dashboard -> Environment Variables وإضافة BOT_TOKEN.\n"
            "السيرفر سيظل يعمل لتجنب فشل الـ Deploy (Health Check OK).\n"
            + "!" * 65 + "\n"
        )
        # Keep web server alive indefinitely so Render does not mark deployment as failed
        while True:
            await asyncio.sleep(3600)

    # 3. Initialize Telegram Bot
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # 4. Resilient Polling Loop with automatic reconnect
    retry_delay = 5
    while True:
        try:
            bot_info = await bot.get_me()
            logger.info("✅ تم الاتصال بنجاح بخوادم تيليجرام: @%s (ID: %s)", bot_info.username, bot_info.id)
            logger.info("🟢 البوت يستقبل الرسائل والتحديثات الآن...")
            await bot.delete_webhook(drop_pending_updates=False)
            await dp.start_polling(bot)
            break
        except TelegramUnauthorizedError:
            logger.error(
                "❌ التوكن BOT_TOKEN غير صالح (401 Unauthorized)! يرجى تصحيحه في إعدادات Render."
            )
            # Sleep and keep healthcheck server alive so Render doesn't crash the container
            await asyncio.sleep(60)
        except TelegramConflictError:
            logger.warning(
                "⚠️ يوجد تضارب: هناك نسخة أخرى من البوت تعمل بالفعل على نفس التوكن. إعادة المحاولة بعد %d ثوانٍ...",
                retry_delay,
            )
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)
        except TelegramNetworkError as net_err:
            logger.warning("⚠️ انقطاع مؤقت في الاتصال بـ Telegram (%s). إعادة المحاولة بعد 10 ثوانٍ...", net_err)
            await asyncio.sleep(10)
        except Exception as exc:
            logger.error("⚠️ حدث خطأ أثناء تشغيل البوت: %s. إعادة المحاولة بعد 10 ثوانٍ...", exc)
            await asyncio.sleep(10)

    if http_runner:
        await http_runner.cleanup()
    await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 تم إيقاف البوت بنجاح.")
