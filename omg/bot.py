import os
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web
from aiogram.webhook.aiohttp_impl import SimpleRequestHandler, setup_application

from config import BOT_TOKEN
from database import init_db

# Handlers import qilinadi
from handlers import common, register, jobs, admin

# Logger sozlamalari
sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

async def main():
    if not BOT_TOKEN or "example" in BOT_TOKEN:
        logger.error("BOT_TOKEN sozlanmagan! Iltimos, .env faylini to'ldiring.")
        return

    # Ma'lumotlar bazasini initsializatsiya qilish
    logger.info("Ma'lumotlar bazasi yuklanmoqda...")
    await init_db()

    # Bot va Dispatcher yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Routerlarni ulash
    dp.include_router(common.router)
    dp.include_router(register.router)
    dp.include_router(jobs.router)
    dp.include_router(admin.router)

    # Render uchun Webhook yoki mahalliy Polling rejimini aniqlash
    render_url = os.getenv("RENDER_EXTERNAL_URL")

    if render_url:
        logger.info(f"Render muhiti aniqlandi. Webhook rejimida ishga tushmoqda: {render_url}")
        
        # Webhook manzilini o'rnatish
        webhook_path = "/webhook"
        await bot.set_webhook(
            url=f"{render_url}{webhook_path}",
            drop_pending_updates=True
        )
        
        # aiohttp ilovasini sozlash
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot
        )
        webhook_requests_handler.register(app, path=webhook_path)
        setup_application(app, dp, bot=bot)
        
        # Portni olish (Render portni o'zi taqdim etadi)
        port = int(os.getenv("PORT", 8080))
        
        # Web serverni ishga tushirish
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        
        logger.info(f"Web server port {port} da ishga tushdi.")
        
        # Serverni cheksiz ushlab turish
        await asyncio.Event().wait()
    else:
        logger.info("Mahalliy muhit aniqlandi. Polling rejimida ishga tushmoqda...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi.")
