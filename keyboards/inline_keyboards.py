from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_start_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Регистрация", callback_data="register")
        ],
        [
            InlineKeyboardButton(text="Написать лекцию", callback_data="write_lecture"),
            InlineKeyboardButton(text="Список лекций", callback_data="list_lectures")
        ]
    ])

def get_lecture_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назначить лекцию", callback_data="assign_lecture")]
    ])

def get_pagination_keyboard(current_page: int, total_pages: int):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        []
    ])

    if current_page > 1:
        keyboard.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_{current_page - 1}"))

    if current_page < total_pages:
        keyboard.insert(InlineKeyboardButton(text="➡️ Вперед", callback_data=f"page_{current_page + 1}"))

    return keyboard
