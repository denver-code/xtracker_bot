from asyncio import run
from logging import basicConfig, INFO
from datetime import datetime

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command, Filter
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.fsm.context import FSMContext

from bot.fsm.set_channel_states import SetChannelState
from bot.utils.config import settings

import bot.utils.redis as redis_db

router = Router()

class AdminFilter(Filter):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in settings.WHITELIST

class IsGroup(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.chat.type in (
            "group", "supergroup"
        )

@router.message(Command(commands=["start"]), AdminFilter())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Welcome to Tracker bot, {message.from_user.full_name}!")

@router.message(Command(commands=["connect"]), AdminFilter(), IsGroup())
async def command_connect_handler(message: Message) -> None:
    redis_db.set_user(message.from_user.id, {"channel_id": message.chat.id})
    await message.answer(f"Connected to \"{message.chat.title}\"")

@router.message(Command(commands=["info"]), AdminFilter())
async def command_info_handler(message: Message) -> None:
    await message.answer(f"Chat id: ```{message.chat.id}```\nSender id: ```{message.from_user.id}```")


@router.message(Command(commands=["ping"]), AdminFilter())
async def command_ping_handler(message: Message) -> None:
    await message.answer("pong!")
    
def format_message(author: str, target: str, status: str, time: str) -> str:
    return f"""
📣*New status initialised!*
Author: *{author}*
Target: *{target}*
Status: *{status}*
Time: *{time}*
"""


@router.message(Command(commands=["st"]), AdminFilter())
async def command_set_target_name_handler(message: Message) -> None:
    target_name = message.text[4:]
    
    _user = redis_db.get_user(message.from_user.id)
    _user["target_name"] = target_name
    redis_db.set_user(message.from_user.id, _user)

    await message.answer(f"Target name set to \"{target_name}\"")


@router.message(Command(commands=["sm"]), AdminFilter())
async def command_set_my_name_handler(message: Message) -> None:
    target_name = message.text[4:]
    
    _user = redis_db.get_user(message.from_user.id)
    _user["my_name"] = target_name
    redis_db.set_user(message.from_user.id, _user)

    await message.answer(f"Your name set to \"{target_name}\"")


@router.message(Command(commands=["broadcast"]), AdminFilter())
async def command_broadcast_handler(message: Message, bot: Bot) -> None:
    _user = redis_db.get_user(message.from_user.id)

    await bot.send_message(_user.get("channel_id"), format_message(
        author=_user.get("my_name", "Unknown"),
        target=_user.get("target_name", "Unknown"),
        status=message.text[11:],
        time=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    ))


@router.message(Command(commands=["add_status", "as"]), AdminFilter())
async def command_add_status_handler(message: Message, state: FSMContext) -> None:

    status_text = message.text[4 if message.text.startswith("/as") else 10:]
    
    _user = redis_db.get_user(f"{message.from_user.id}_status")
    
    status_list = _user.get("status_list", [])
    status_list.append(status_text)

    _user["status_list"] = status_list

    redis_db.set_user(f"{message.from_user.id}_status", _user)
    await message.answer(f"Status \"{status_text}\" added!")


@router.message(Command(commands=["new", "push"]), AdminFilter())
async def command_new_handler(message: Message, state: FSMContext) -> None:
    _user = redis_db.get_user(f"{message.from_user.id}_status")

    status_list = _user.get("status_list", [])
    if len(status_list) == 0:
        await message.answer("You don't have any status. Use /add_status to add status")
        return

    builder = InlineKeyboardBuilder()
    for status in status_list:
        builder.button(text=status, callback_data=f"nf_{message.from_user.id}_{status_list.index(status)}")
    
    builder.adjust(1)

    await message.answer("Choose status:", reply_markup=builder.as_markup())

@router.callback_query()
async def callback_query_handler(query: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    if query.data.startswith("nf"):
        _, user_id, status_index = query.data.split("_")
        __user = redis_db.get_user(f"{user_id}")
        _user = redis_db.get_user(f"{user_id}_status")
        status_list = _user.get("status_list", [])

        _status = status_list[int(status_index)]

        await bot.send_message(__user.get("channel_id"), format_message(
            author=__user.get("my_name", "Unknown"),
            target=__user.get("target_name", "Unknown"),
            status=_status,
            time=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        ))

        await query.message.edit_text(f"Status \"{_status}\" sent!", reply_markup=None)
    elif query.data.startswith("del"):
        _, user_id, status_index = query.data.split("_")
        _user = redis_db.get_user(f"{user_id}_status")
        status_list = _user.get("status_list", [])

        status_list.pop(int(status_index))

        _user["status_list"] = status_list

        redis_db.set_user(f"{user_id}_status", _user)

        await query.message.edit_text(f"Status deleted!", reply_markup=None)


@router.message(Command(commands=["delete_status", "ds"]), AdminFilter())
async def command_list_status_handler(message: Message, state: FSMContext) -> None:
    _user = redis_db.get_user(f"{message.from_user.id}_status")

    status_list = _user.get("status_list", [])
    if len(status_list) == 0:
        await message.answer("You don't have any status. Use /add_status to add status")
        return

    builder = InlineKeyboardBuilder()
    for status in status_list:
        builder.button(text=status, callback_data=f"del_{message.from_user.id}_{status_list.index(status)}")
    
    builder.adjust(1)

    await message.answer("Choose status to delete:", reply_markup=builder.as_markup())


async def main() -> None:
    dp = Dispatcher()
    dp.include_router(router)

    redis_db.ping()

    bot = Bot(settings.TOKEN, parse_mode="Markdown")

    await dp.start_polling(bot)


if __name__ == "__main__":
    basicConfig(level=INFO)
    run(main())
