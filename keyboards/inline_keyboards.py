from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Написать лекцию", callback_data="write_lecture")],
        [InlineKeyboardButton(text="Список лекций", callback_data="list_lectures")],
        [InlineKeyboardButton(text="Поиск лекций", callback_data="search_lectures")],
    ])
