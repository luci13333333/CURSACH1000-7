import sqlite3
from aiogram import Router
from aiogram.filters import Command
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import inline_keyboards as ikb
from lexicon.lexicon import LEXICON_RU

class Profile(StatesGroup):
    reg = State()

router = Router()

@router.message(Command(commands=['start']))
async def process_start_command(message: types.Message):
    keyboard = ikb.get_start_keyboard()
    await message.answer(LEXICON_RU['/start'])
    await message.answer("Выберите действие:",reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "register")
async def register_user(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Profile.reg)
    await callback.message.answer("Для создания профиля используйте уникальное имя пользователя.\nПаролем является user_id от Вашего Telegram-аккаунта.")
    await callback.message.answer("Введите имя пользователя:")
    await callback.answer()

@router.message(Profile.reg)
async def process_username(message: types.Message,state: FSMContext):
    username = message.text
    user_id = message.from_user.id
    await state.update_data(username=username)
    data = await state.get_data()
    username = data.get("username")
    # Проверка существования пользователя
    conn = sqlite3.connect("./database/database.db")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM users WHERE username = '{username}'")
    if cur.fetchone():
        await message.answer("Пользователь уже существует.")
    else:
        hashed_password = message.from_user.id
        cur.execute(f"INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (?, ?, ?)", (user_id, username, hashed_password))
        conn.commit()
        await message.answer(f"Вы успешно зарегистрированы!")
    conn.close()
    await state.clear()

# Обработчик команды /help
@router.message(Command(commands=["help"]))
async def start_command(message:types.Message):
    await message.answer(text=LEXICON_RU['/help'])