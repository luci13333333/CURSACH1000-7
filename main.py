import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config_data.config import Config, load_config
from handlers import handlers,lecture_handlers
from aiogram.types import BotCommand
from database.database import create_tables


async def main():
    config: Config = load_config()

    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(handlers.router)
    dp.include_router(lecture_handlers.router)

    create_tables()

    async def set_main_menu(bot: Bot):
        # Создаем список с командами и их описанием для кнопки menu
        main_menu_commands = [
            BotCommand(command='/start',
                       description='Запуск бота'),
            BotCommand(command='/help',
                       description='Справка по работе бота'),
        ]

        await bot.set_my_commands(main_menu_commands)

    # Регистрируем асинхронную функцию в диспетчере,
    # которая будет выполняться на старте бота,
        await dp.startup.register(set_main_menu)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())