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
WEBHOOK_SECRET_PATH = f"/{BOT_TOKEN}"  # Уникальный путь для вебхука
BASE_WEBHOOK_URL = f"https://{HEROKU_APP_NAME}.herokuapp.com/{BOT_TOKEN}"

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
    # Register startup hook to initialize webhook
    dp.startup.register(on_startup)
    # Initialize Bot instance with a default parse mode which will be passed to all API
    bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp.include_router(bdika_gilui_router)
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
