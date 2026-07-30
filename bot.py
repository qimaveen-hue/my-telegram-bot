import asyncio
import os
from datetime import datetime
import pytz
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8982333001:AAHDy5W-kvTeP3CZSaDHLR5JOp6VrazRQvg"
ADMIN_ID = 6482057553

# Часовой пояс Владивостока (МСК+7)
TIMEZONE = pytz.timezone('Asia/Vladivostok')

bot = Bot(token=TOKEN)
dp = Dispatcher()

last_user_id = None

def is_working_hours() -> bool:
    """Проверяет, входит ли текущее время во Владивостоке в интервал с 10:00 до 01:00 ночи."""
    now = datetime.now(TIMEZONE)
    return now.hour >= 10 or now.hour == 0

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 1. Bust Up"), KeyboardButton(text="👤 2. Half Body")],
        [KeyboardButton(text="👤 3. Knee Up"), KeyboardButton(text="👤 4. Full Body")],
        [KeyboardButton(text="📜 Полный Прайс"), KeyboardButton(text="📩 Заказать арт")]
    ],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "Привет! 👋 Добро пожаловать в арт-галерею!\n\n"
        "Выбери нужную категорию с помощью кнопок ниже. "
        "Если хочешь сделать заказ — просто напиши сюда сообщение, и художница тебе ответит!",
        reply_markup=main_keyboard
    )

@dp.message()
async def handle_all_messages(message: types.Message):
    global last_user_id
    
    # Если пишет не админ и сейчас нерабочее время
    if message.from_user.id != ADMIN_ID and not is_working_hours():
        await message.answer("Режим работы закончен, с 10:00 по 01:00 Вам ответит Художник.")
        return

    if message.from_user.id != ADMIN_ID:
        last_user_id = message.from_user.id
        await message.answer("Ваше сообщение получено! Художник ответит вам в ближайшее время.")
        await bot.send_message(
            ADMIN_ID, 
            f"📩 Новое сообщение от @{message.from_user.username or 'без_юзернейма'} (ID: {message.from_user.id}):\n\n{message.text}"
        )
    else:
        if last_user_id:
            await bot.send_message(last_user_id, f"🎨 Ответ от Художника:\n\n{message.text}")
            await message.answer("Ответ успешно отправлен пользователю!")
        else:
            await message.answer("Пока нет активных пользователей для ответа.")

# Простейший веб-сервер для проверки от Render
async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def main():
    # Настройка и запуск веб-сервера
    app = web.Application()
    app.router.add_get("/", handle_ping)
    
    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    # Запускаем поллинг бота и держим процесс живым
    try:
        await dp.start_polling(bot)
    finally:
        await runner.cleanup()

if __name__ == "main":
    asyncio.run(main())
