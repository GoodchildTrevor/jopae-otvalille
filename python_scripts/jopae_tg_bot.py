import os
from dotenv import load_dotenv

import asyncio
import pytz
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from python_scripts.message import get_tg_jopae_message

from python_scripts.config.consts import GREETINGS

load_dotenv()

TOKEN = os.getenv("JOPAE_BOT")
TIMEZONE = os.getenv("TIMEZONE")
# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()
# Создание планировщика задач
scheduler = AsyncIOScheduler()
timezone = pytz.timezone(TIMEZONE)


async def send_morning_message(chat_id):
    text = get_tg_jopae_message()
    await bot.send_message(chat_id, text)


@dp.message(Command("start"))
async def start_command(message: Message):
    chat_id = message.chat.id
    scheduler.add_job(
        send_morning_message,
        'cron',
        hour=10, minute=0, timezone=timezone,
        args=[chat_id]
    )
    await message.answer(GREETINGS)


async def main():

    loop = asyncio.get_running_loop()
    tz = pytz.timezone(TIMEZONE)

    global scheduler
    scheduler = AsyncIOScheduler(event_loop=loop, timezone=tz)
    scheduler.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
