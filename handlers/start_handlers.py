from aiogram import types
from aiogram.filters import Command
import inline_keyboards as ikb
import database

def register_handlers(dp):
    @dp.message(Command("start"))
    async def start_command(message: types.Message):
        keyboard = ikb.get_start_keyboard()
        await message.answer("Выберите действие:", reply_markup=keyboard)

    @dp.callback_query(lambda c: c.data == "register")
    async def register_user(callback: types.CallbackQuery):
        await callback.message.answer("Введите имя пользователя:")
        await callback.answer()

    @dp.message(lambda m: m.text)
    async def process_username(message: types.Message):
        username = message.text.strip()
        # Проверка существования пользователя
        conn = database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            await message.answer("Пользователь уже существует.")
        else:
            hashed_password = hash_password(username)
            cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            await message.answer("Вы успешно зарегистрированы!")
        conn.close()

    @dp.callback_query(lambda c: c.data == "login")
    async def login_user(callback: types.CallbackQuery):
        await callback.message.answer("Введите имя пользователя:")
        await callback.answer()

    @dp.message(lambda m: m.text)
    async def process_login(message: types.Message):
        username = message.text.strip()
        conn = database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if user:
            password = hash_password(username)
            if password == user[1]:
                await message.answer("Добро пожаловать, " + username + "!")
                # Здесь можно добавить дополнительную логику после входа
            else:
                await message.answer("Неверный пароль.")
        else:
            await message.answer("Пользователь не найден.")
        conn.close()

    @dp.callback_query(lambda c: c.data == "write_lecture")
    async def write_lecture(callback: types.CallbackQuery):
        await callback.message.answer("Введите название лекции:")
        await callback.answer()

    @dp.message(lambda m: m.text)
    async def lecture_name_handler(message: types.Message):
        lecture_name = message.text.strip()
        await message.answer(f"Теперь введите текст лекции '{lecture_name}':")
        await message.answer("Напишите содержимое лекции:")

    @dp.message(lambda m: m.text)
    async def lecture_content_handler(message: types.Message):
        content = message.text.strip()
        await message.answer(f"Лекция '{message.text}' сохранена!")

    @dp.callback_query(lambda c: c.data == "list_lectures")
    async def list_lectures(callback: types.CallbackQuery):
        await send_lecture_list(callback.message, page=1, edit=False)


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


async def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# Функция для установки хеш-пароля при регистрации
def set_password(user: str, password: str):
    conn = database.get_connection()
    cur = conn.cursor()
    hashed_password = hash_password(password)
    cur.execute("UPDATE users SET password_hash = %s WHERE username = %s", (hashed_password, user))
    conn.commit()
    conn.close()
