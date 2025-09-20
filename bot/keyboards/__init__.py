from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot, types

async def get_share_keyboard(message: types.Message, bot: Bot) -> InlineKeyboardMarkup:
    bot_info = await bot.get_me()
    user = message.from_user
    share_text = (
        f"Привет! Напиши мне анонимное сообщение, и я отвечу на него 😉\n\n"
        f"-- https://t.me/{bot_info.username}?start={user.id}"
    )
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🔗 Поделиться ссылкой', switch_inline_query=share_text)]
        ]
    )