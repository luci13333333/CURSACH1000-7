import sqlite3
from aiogram import Router
from aiogram import types
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class Lecture(StatesGroup):
    lecture = State()
    content = State()

router = Router()

@router.callback_query(lambda c: c.data.startswith("write_lecture"))
async def write_lecture(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.answer("Введите название лекции:")
        await state.set_state(Lecture.lecture)
        await callback.answer()

@router.message(Lecture.lecture)
async def lecture_name_handler(message: types.Message, state: FSMContext):
        lecture_name = message.text
        await state.update_data(lecture_name=lecture_name)
        await message.answer("Теперь введите текст лекции:")
        await state.set_state(Lecture.content)

@router.message(Lecture.content)
async def lecture_content_handler(message: types.Message, state: FSMContext):
        data = await state.get_data()
        lecture_name = data['lecture_name']
        content = message.text
        user_id = message.from_user.id

        conn = sqlite3.connect("./database/database.db")
        cur = conn.cursor()

        # Проверка существования лекции
        cur.execute(f"SELECT * FROM lectures WHERE title = '{lecture_name}' AND user_id = {user_id}")
        if cur.fetchone():
            await message.answer(f"Лекция '{lecture_name}' уже существует.")
        else:
            cur.execute(f"""
            INSERT INTO lectures (title, content, user_id)
            VALUES ('{lecture_name}','{content}', {user_id})
            """)
            conn.commit()
            await message.answer(f"Лекция '{lecture_name}' сохранена!")

        conn.close()
        with open(f'./database/{lecture_name}.txt', 'w', encoding="utf-8") as lecture_file:
            lecture_file.write(content)
        await state.clear()



    # Список лекций
@router.callback_query(lambda c: c.data == "list_lectures")
async def list_lectures(callback: types.CallbackQuery):
    await send_lecture_list(callback.message, page=1, edit=False)
    await callback.answer()

async def send_lecture_list(message: types.Message, page: int, edit: bool = False):
    conn = sqlite3.connect("./database/database.db")
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT COUNT(*) FROM lectures;
        """)
        total_lectures = cur.fetchone()[0]

        cur.execute(f"""
            SELECT l.title, u.username
            FROM lectures l
            JOIN users u ON l.user_id = u.id
            ORDER BY l.id DESC
            LIMIT ? OFFSET ?;
        """, (10, (page - 1) * 10))

        lectures = cur.fetchall()
        start, end = (page - 1) * 10, min(page * 10, total_lectures)
        keyboard_builder = InlineKeyboardBuilder()

        for i, (title, username) in enumerate(lectures, start=start):
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
        if end < total_lectures:
            keyboard_builder.row(
                InlineKeyboardButton(text="➡️ Вперед", callback_data=f"page_{page + 1}")
            )

        if edit:
            await message.edit_text("Список лекций:", reply_markup=keyboard_builder.as_markup())
        else:
            await message.answer("Список лекций:", reply_markup=keyboard_builder.as_markup())
    finally:
        conn.close()

@router.callback_query(lambda c: c.data.startswith("page_"))
async def paginate_lectures(callback: types.CallbackQuery):
    page = int(callback.data[len("page_"):])
    await send_lecture_list(callback.message, page, edit=True)
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("lecture_"))
async def send_lecture_file(callback: types.CallbackQuery):
    lecture_index = int(callback.data[8:])
    conn = sqlite3.connect("./database/database.db")
    cur = conn.cursor()

    try:
        cur.execute(f"""
            SELECT l.title, u.username, l.content
            FROM lectures l
            JOIN users u ON l.user_id = u.id
            ORDER BY l.id DESC
            LIMIT 1 OFFSET ?;
        """, (lecture_index,))
        lecture = cur.fetchone()

        if lecture:
            title, username, content = lecture
            lecture_name = title
            await callback.message.answer_document(
                document=FSInputFile(f'./database/{lecture_name}.txt'),
                caption=f"Лекция от {username}: {title}"
            )
        else:
            await callback.message.answer("Лекция не найдена.")
    finally:
        conn.close()