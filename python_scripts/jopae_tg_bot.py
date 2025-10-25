import os
from typing import NoReturn
from dotenv import load_dotenv

import asyncio
import pytz
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError

from python_scripts.message import get_tg_jopae_message
from python_scripts.subscriptions import init_db, add_subscriber, remove_subscriber, get_all_subscribers
from python_scripts.config.consts import GREETINGS, HELP_MESSAGE

load_dotenv()

TOKEN: str = os.getenv("JOPAE_BOT", "")
TIMEZONE: str = os.getenv("TIMEZONE", "UTC")

bot: Bot = Bot(token=TOKEN)
dp: Dispatcher = Dispatcher()
scheduler: AsyncIOScheduler = AsyncIOScheduler()
timezone: pytz.BaseTzInfo = pytz.timezone(TIMEZONE)


async def send_morning_message(chat_id: int) -> None:
    """
    Отправляет запланированное утреннее сообщение в указанный чат Telegram.
    Args:
        chat_id: уникальный идентификатор чата Telegram
    Raises:
        Exception: если отправка сообщения не удалась (например, пользователь заблокировал бота)
    """
    text: str = get_tg_jopae_message()
    await bot.send_message(chat_id, text)


@dp.message(Command("start"))
async def start_command(message: Message) -> None:
    """
    Обрабатывает команду /start: подписывает пользователя на ежедневные сообщения.
    Добавляет chat_id пользователя в базу данных и создает ежедневное задание на 10:00
    в настроенном часовом поясе. Обеспечивает идемпотентность с помощью уникального ID задания.
    Args:
        message: входящий объект сообщения Telegram
    """
    chat_id: int = message.chat.id
    add_subscriber(chat_id)

    job_id: str = f"job_{chat_id}"
    if not scheduler.get_job(job_id):
        scheduler.add_job(
            send_morning_message,
            trigger="cron",
            hour=7,
            minute=0,
            timezone=timezone,
            args=[chat_id],
            id=job_id,
            replace_existing=True,
        )

    await message.answer(GREETINGS)


@dp.message(Command("stop"))
async def stop_command(message: Message) -> None:
    """
    Обрабатывает команду /stop: отписывает пользователя от ежедневных сообщений.
    Удаляет chat_id пользователя из базы данных и удаляет запланированное задание.
    Args:
        message: входящий объект сообщения Telegram
    """
    chat_id: int = message.chat.id
    job_id: str = f"job_{chat_id}"

    try:
        scheduler.remove_job(job_id)
    except JobLookupError:
        pass

    remove_subscriber(chat_id)
    await message.answer("Вы отписались от ежедневных сообщений. Чтобы снова подписаться — отправьте /start.")


@dp.message(Command("help"))
async def help_command(message: Message) -> None:
    """
    Handle the /help command: send a description of the bot's functionality.
    :param message: Incoming Telegram message object.
    """
    await message.answer(HELP_MESSAGE)


async def restore_scheduled_jobs() -> None:
    """
    Обрабатывает команду /help: отправляет описание функциональности бота.
    Args:
        message: входящий объект сообщения Telegram
    """
    chat_ids: list[int] = get_all_subscribers()
    restored_count: int = 0

    for chat_id in chat_ids:
        job_id: str = f"job_{chat_id}"
        if not scheduler.get_job(job_id):
            scheduler.add_job(
                send_morning_message,
                trigger="cron",
                hour=10,
                minute=0,
                timezone=timezone,
                args=[chat_id],
                id=job_id,
                replace_existing=True,
            )
            restored_count += 1

    print(f"Restored {restored_count} scheduled jobs from database.")


@dp.message(Command("test"))
async def test_message(message: Message) -> None:
    """
    Обрабатывает команду /test: отправляет тестовое утреннее сообщение.
    Функция позволяет проверить работу бота, отправив утреннее сообщение
    непосредственно в чат без ожидания запланированного времени.
    После отправки основного сообщения также отправляется подтверждение.
    Args:
        message: входящий объект сообщения Telegram
    """
    await send_morning_message(message.chat.id)
    await message.answer("Тестовое сообщение отправлено.")


async def main() -> NoReturn:
    """
    Главная точка входа приложения Telegram бота.
    Инициализирует базу данных, запускает APScheduler, восстанавливает запланированные задания
    и начинает опрос обновлений Telegram.
    При нормальной работе функция не возвращает управление.
    """
    init_db()

    global scheduler
    scheduler = AsyncIOScheduler(timezone=timezone)
    scheduler.start()

    await restore_scheduled_jobs()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
