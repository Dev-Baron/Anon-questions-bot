import os
import asyncio
import structlog
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from bot.database.database import db
from bot.handlers.user_handlers import router

load_dotenv()
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

logger = structlog.get_logger()

async def main():
    
    try:
        await db.init_db()
        dp.include_router(router)
        logger.info('BOT STARTED')
        await dp.start_polling(bot)
    
    except KeyboardInterrupt:
        logger.info('BOT STOPPED')

if __name__ == '__main__':
    asyncio.run(main())