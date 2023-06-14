from asyncio import run
from logging import basicConfig, INFO

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command, Filter
from aiogram.types import Message

from bot.utils.config import settings


router = Router()

class AdminFilter(Filter):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in settings.WHITELIST



@router.message(Command(commands=["start"]), AdminFilter())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Welcome to Tracker bot, {message.from_user.full_name}!")



async def main() -> None:
    dp = Dispatcher()
    dp.include_router(router)

    bot = Bot(settings.TOKEN, parse_mode="HTML")

    await dp.start_polling(bot)


if __name__ == "__main__":
    basicConfig(level=INFO)
    run(main())
