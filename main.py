import logging
import sys
import os
from dotenv import load_dotenv
from aiohttp import web

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# Импортируем ваши обработчики
from handlers.start_handlers import start_router
from handlers.bdika_gilui_handlers import bdika_gilui_router

# Загружаем переменные окружения из .env файла

load_dotenv()

# Получаем токен бота и имя приложения Heroku из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

# Настройки веб-сервера
WEB_SERVER_HOST = '0.0.0.0'  # Слушать все сетевые интерфейсы
WEB_SERVER_PORT = os.environ.get('PORT')  # Порт, предоставленный Heroku
WEBHOOK_SECRET_PATH = f"{BOT_TOKEN}"  # Уникальный путь для вебхука
BASE_WEBHOOK_URL = f"https://{HEROKU_APP_NAME}.herokuapp.com/{WEBHOOK_SECRET_PATH}"

# Создаем роутер
router = Router()


# Функция запуска приложения
async def on_startup(bot: Bot) -> None:
    # If you have a self-signed SSL certificate, then you will need to send a public
    # certificate to Telegram
    await bot.set_webhook(BASE_WEBHOOK_URL)


def main() -> None:
    # Dispatcher is a root router
    dp = Dispatcher()
    # ... and all other routers should be attached to Dispatcher
    dp.include_router(router)
    # Регистрируем роутеры
    dp.include_router(start_router)
    dp.include_router(bdika_gilui_router)
    # Register startup hook to initialize webhook
    dp.startup.register(on_startup)
    # Initialize Bot instance with a default parse mode which will be passed to all API
    bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
    # Create aiohttp.web.Application instance
    app = web.Application()
    # Create an instance of request handler,
    # aiogram has few implementations for different cases of usage
    # In this example we use SimpleRequestHandler which is designed to handle simplecases
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )
    # Register webhook handler on application
    webhook_requests_handler.register(app, path=WEBHOOK_SECRET_PATH)
    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)
    # And finally start webserver
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


# Запуск веб-сервера
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()

# import os
# import logging
# from dotenv import load_dotenv
# import asyncio
# from aiogram import Bot, Dispatcher, F
# from aiogram.types import Message
#
# # #from proj
# from handlers.start_handlers import start_router
# from handlers.bdika_gilui_handlers import bdika_gilui_router
#
# # Load environment variables from a .env file
# load_dotenv()
# # Get the bot token from environment variables
# BOT_TOKEN = os.getenv('BOT_TOKEN')
# # Initialize the bot
# bot = Bot(token=BOT_TOKEN)
# # Initialize the dispatcher
# dp = Dispatcher()
#
#
# # Register handlers from other modules
# # Polling, updates cycle
#
# # Define a function to start the polling and handle updates
# # Register handlers from other modules
# # Polling, updates cycle
# async def main():
#     # Register handlers
#     dp.include_router(start_router)
#     dp.include_router(bdika_gilui_router)
#     # Start polling for updates
#     await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
#
#
# # Define an echo function to respond when a message is not understood
# async def echo(message: Message):
#     await message.answer('I dont understand you..')
#
#
# # Entry point of the script
# if __name__ == '__main__':
#     try:
#         # Set up logging
#         logging.basicConfig(level=logging.INFO)
#         logger = logging.getLogger(__name__)
#         # Run the main function to start the bot
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print('Exit')
