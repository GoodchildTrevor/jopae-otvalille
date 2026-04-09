import os
import asyncio
from dotenv import load_dotenv

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
timezone: pytz.BaseTzInfo = pytz.timezone(TIMEZONE)
scheduler: AsyncIOScheduler = AsyncIOScheduler(timezone=timezone)


async def send_morning_message(chat_id: int) -> None:
    """
    Send a scheduled morning message to the specified Telegram chat.

    :param chat_id: Unique identifier of the Telegram chat.
    :raises Exception: If message sending fails (e.g., user blocked the bot).
    """
    try:
        text: str = get_tg_jopae_message()
        await bot.send_message(chat_id, text)
    except Exception as e:
        print(f"Error sending message to chat {chat_id}: {e}")


@dp.message(Command("start"))
async def start_command(message: Message) -> None:
    """
    Handle the /start command: subscribe the user to daily messages.

    Adds the user's chat_id to the database and creates a daily job at 7:00 AM
    in the configured timezone. Ensures idempotency using a unique job ID.

    :param message: Incoming Telegram message object.
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
    Handle the /stop command: unsubscribe the user from daily messages.

    Removes the user's chat_id from the database and removes the scheduled job.

    :param message: Incoming Telegram message object.
    """
    chat_id: int = message.chat.id
    job_id: str = f"job_{chat_id}"

    try:
        scheduler.remove_job(job_id)
    except JobLookupError:
        pass

    remove_subscriber(chat_id)
    await message.answer("You have unsubscribed from daily messages. To subscribe again, send /start.")


@dp.message(Command("help"))
async def help_command(message: Message) -> None:
    """
    Handle the /help command: send a description of the bot's functionality.

    :param message: Incoming Telegram message object.
    """
    await message.answer(HELP_MESSAGE)


async def restore_scheduled_jobs() -> None:
    """
    Restore scheduled jobs for all subscribers from the database.

    Iterates through all subscribed chat IDs and adds missing jobs to the scheduler.
    This ensures jobs persist across bot restarts.
    """
    chat_ids: list[int] = get_all_subscribers()
    restored_count: int = 0

    for chat_id in chat_ids:
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
            restored_count += 1

    print(f"Restored {restored_count} scheduled jobs from database.")


@dp.message(Command("test"))
async def test_message(message: Message) -> None:
    """
    Handle the /test command: send a test morning message immediately.

    Allows testing the bot functionality by sending a morning message
    directly to the chat without waiting for the scheduled time.
    Sends a confirmation message after the main message.

    :param message: Incoming Telegram message object.
    """
    await send_morning_message(message.chat.id)
    await message.answer("Test message sent.")


async def main() -> None:
    """
    Main entry point for the Telegram bot application.

    Initializes the database, starts the APScheduler, restores scheduled jobs,
    and starts polling for Telegram updates.
    Does not return control during normal operation.
    """
    init_db()

    if not scheduler.running:
        scheduler.start()

    await restore_scheduled_jobs()

    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
