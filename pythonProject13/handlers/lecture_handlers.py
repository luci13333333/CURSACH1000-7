import os
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import LECTURES_DIR, LECTURES_LIST_FILE
from constants import ITEMS_PER_PAGE


class LectureStates(StatesGroup):
    waiting_for_lecture_name = State()
    waiting_for_lecture_content = State()


def register_handlers(dp):
    @dp.callback_query(lambda c: c.data == "write_lecture")
    async def write_lecture(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.answer("Введите название лекции:")
        await state.set_state(LectureStates.waiting_for_lecture_name)
        await callback.answer()

    @dp.message(LectureStates.waiting_for_lecture_name)
    async def lecture_name_handler(message: types.Message, state: FSMContext):
        lecture_name = message.text.strip()
        with open(LECTURES_LIST_FILE, "a") as f:
            f.write(lecture_name + "\n")
        await state.update_data(lecture_name=lecture_name)
        await message.answer("Теперь введите текст лекции:")
        await state.set_state(LectureStates.waiting_for_lecture_content)

    @dp.message(LectureStates.waiting_for_lecture_content)
    async def lecture_content_handler(message: types.Message, state: FSMContext):
        data = await state.get_data()
        lecture_name = data.get("lecture_name")
        lecture_path = os.path.join(LECTURES_DIR, f"{lecture_name}.txt")
        with open(lecture_path, "w") as f:
            f.write(message.text.strip())
        await message.answer(f"Лекция '{lecture_name}' сохранена!")
        await state.clear()

    @dp.callback_query(lambda c: c.data == "list_lectures")
    async def list_lectures(callback: types.CallbackQuery):
        await send_lecture_list(callback.message, page=1)
        await callback.answer()

    async def send_lecture_list(message: types.Message, page: int):
        with open(LECTURES_LIST_FILE, "r") as f:
            lectures = [line.strip() for line in f.readlines()]

        start, end = (page - 1) * ITEMS_PER_PAGE, page * ITEMS_PER_PAGE
        keyboard_builder = InlineKeyboardBuilder()
        for lecture in lectures[start:end]:
            keyboard_builder.row(InlineKeyboardButton(text=lecture, callback_data=f"lecture_{lecture}"))

        if page > 1:
            keyboard_builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_{page - 1}"))
        if end < len(lectures):
            keyboard_builder.row(InlineKeyboardButton(text="➡️ Вперед", callback_data=f"page_{page + 1}"))

        await message.answer("Список лекций:", reply_markup=keyboard_builder.as_markup())


    @dp.callback_query(lambda c: c.data.startswith("page_"))
    async def paginate_lectures(callback: types.CallbackQuery):
        page = int(callback.data[len("page_"):])
        await send_lecture_list(callback.message, page)
        await callback.answer()
