from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from config import settings

# Commands for the target chat only.
chat_router = Router(name="chat")
chat_router.message.filter(F.chat.id == settings.CHAT_ID)

# Works in any chat, so the admin can discover chat/thread IDs during setup.
admin_router = Router(name="admin")
admin_router.message.filter(F.from_user.id == settings.ADMIN_ID)


@chat_router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer("🤖 Welcome to the LZT Helper Bot!")


@admin_router.message(Command("debug"))
async def debug(message: Message) -> None:
    await message.answer(
        f"User ID: <code>{message.from_user.id}</code>\n"
        f"Chat ID: <code>{message.chat.id}</code>\n"
        f"Thread ID: <code>{message.message_thread_id}</code>"
    )
