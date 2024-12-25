from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import API_TOKEN, DATABASE_URL
from handlers import start_handlers, lecture_handlers
import database

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Подключение к базе данных при запуске бота
database.connect_to_db()

# Регистрация хэндлеров
start_handlers.register_handlers(dp)
lecture_handlers.register_handlers(dp)

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
