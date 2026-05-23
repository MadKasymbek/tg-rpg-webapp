import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# ВАЖНО: Замените на токен вашего бота, полученный от @BotFather
BOT_TOKEN = "8447546621:AAGGqV0YMPjcSJ3hkiZ7niFHo4LvAkNTjmg"

# ВАЖНО: Замените на ссылку вашего GitHub Pages после деплоя фронтенда
WEBAPP_URL = "https://madkasymbek.github.io/tg-rpg-webapp/"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    """
    Хэндлер на команду /start.
    Отправляет приветственное сообщение и кнопку с Web App.
    """
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗡 В бой!", 
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ]
        ]
    )
    
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n\n"
        "Добро пожаловать в текстовую RPG. Твои приключения начинаются здесь. Нажми кнопку ниже, чтобы войти в игру.",
        reply_markup=markup
    )

async def main():
    # Запуск поллинга
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
