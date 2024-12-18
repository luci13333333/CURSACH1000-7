from aiogram import types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def register_handlers(dp):
    @dp.message(Command("start"))
    async def start_command(message: types.Message):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Написать лекцию", callback_data="write_lecture")],
            [InlineKeyboardButton(text="Список лекций", callback_data="list_lectures")],
        ])
        await message.answer("Выберите действие:", reply_markup=keyboard)
