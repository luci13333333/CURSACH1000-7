import os
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import LECTURES_DIR, LECTURES_LIST_FILE
from constants import ITEMS_PER_PAGE
import database

class LectureStates(StatesGroup):
    waiting_for_lecture_name = State()
    waiting_for_lecture_content = State()


def register_handlers(dp):
    @dp.callback_query(lambda c: c.data.startswith("write_lecture"))
    async def write_lecture(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.answer("Введите название лекции:")
        await state.set_state(LectureStates.waiting_for_lecture_name)
        await callback.answer()

    @dp.message(LectureStates.waiting_for_lecture_name)
    async def lecture_name_handler(message: types.Message, state: FSMContext):
        lecture_name = message.text.strip()
        await state.update_data(lecture_name=lecture_name)
        await message.answer("Теперь введите текст лекции:")
        await state.set_state(LectureStates.waiting_for_lecture_content)

    @dp.message(LectureStates.waiting_for_lecture_content)
    async def lecture_content_handler(message: types.Message, state: FSMContext):
        data = await state.get_data()
        lecture_name = data['lecture_name']
        content = message.text.strip()

        conn = database.get_connection()
        cur = conn.cursor()

        # Проверка существования лекции
        cur.execute("SELECT * FROM lectures WHERE title = %s AND user_id = %s", (lecture_name, state.user.id))
        if cur.fetchone():
            await message.answer(f"Лекция '{lecture_name}' уже существует.")
        else:
            cur.execute("""
            INSERT INTO lectures (title, content, user_id)
            VALUES (%s, %s, %s)
            """, (lecture_name, content, state.user.id))
            conn.commit()
            await message.answer(f"Лекция '{lecture_name}' сохранена!")

        conn.close()
        await state.clear()



    # Список лекций
    @dp.callback_query(lambda c: c.data == "list_lectures")
    async def list_lectures(callback: types.CallbackQuery):
        await send_lecture_list(callback.message, page=1, edit=False)
        await callback.answer()

    async def send_lecture_list(message: types.Message, page: int, edit: bool = False):
        conn = database.get_connection()
        cur = conn.cursor()

        cur.execute("""
        SELECT l.title, u.username
        FROM lectures l
        JOIN users u ON l.user_id = u.id
        ORDER BY l.id DESC
        LIMIT %s OFFSET %s;
        """, (ITEMS_PER_PAGE, (page - 1) * ITEMS_PER_PAGE))

        lectures = cur.fetchall()
        start, end = (page - 1) * ITEMS_PER_PAGE, page * ITEMS_PER_PAGE
        keyboard_builder = InlineKeyboardBuilder()
        for i, (title, username) in enumerate(lectures[start:end], start=start):
            keyboard_builder.row(
                InlineKeyboardButton(
                    text=f"{username} - {title}",
                    callback_data=f"lecture_{i}"
                )
            )

        if page > 1:
            keyboard_builder.row(
                InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_{page - 1}")
            )
        if end < len(lectures):
            keyboard_builder.row(
                InlineKeyboardButton(text="➡️ Вперед", callback_data=f"page_{page + 1}")
            )

        if edit:
            await message.edit_text("Список лекций:", reply_markup=keyboard_builder.as_markup())
        else:
            await message.answer("Список лекций:", reply_markup=keyboard_builder.as_markup())

        conn.close()

    @dp.callback_query(lambda c: c.data.startswith("page_"))
    async def paginate_lectures(callback: types.CallbackQuery):
        page = int(callback.data[len("page_"):])
        await send_lecture_list(callback.message, page, edit=True)
        await callback.answer()

    # Отправка файла лекции
    @dp.callback_query(lambda c: c.data.startswith("lecture_"))
    async def send_lecture_file(callback: types.CallbackQuery):
        lecture_index = int(callback.data[9:])
        conn = database.get_connection()
        cur = conn.cursor()

        cur.execute("""
        SELECT l.title, u.username, l.content
        FROM lectures l
        JOIN users u ON l.user_id = u.id
        ORDER BY l.id DESC
        LIMIT 1 OFFSET %s;
        """, (lecture_index,))
        lecture = cur.fetchone()

        if lecture:
            title, username, content = lecture
            await callback.message.answer_document(
                document=types.FSInputFile(content),
                caption=f"Лекция от {username}: {title}"
            )
        else:
            await callback.message.answer(f"Лекция не найдена.")
        conn.close()
