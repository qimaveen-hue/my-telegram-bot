import asyncio
from datetime import datetime
import pytz
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8982333001:AAHj9wFST4PIEot8OA6tLP_duDmsr7tVvkQ"
ADMIN_ID = 6482057553

# Часовой пояс Владивостока (МСК+7)
TIMEZONE = pytz.timezone('Asia/Vladivostok')

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Переменная для хранения ID последнего написавшего пользователя
last_user_id = None

def is_working_hours() -> bool:
    """Проверяет, входит ли текущее время во Владивостоке в интервал с 10:00 до 23:00."""
    now = datetime.now(TIMEZONE)
    return 10 <= now.hour < 23

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
    print(f"👤 Пользователь @{message.from_user.username} запустил бота (/start)")
    await message.answer(
        "Привет! 👋 Добро пожаловать в арт-галерею!\n\n"
        "Выбери нужную категорию с помощью кнопок ниже. "
        "Если хочешь сделать заказ — просто напиши сюда сообщение, и художница тебе ответит!",
        reply_markup=main_keyboard
    )

# Обработчик всех остальных сообщений
@dp.message()
async def handle_all_messages(message: types.Message):
    global last_user_id
    
    # Если пишет НЕ админ и сейчас НЕ рабочее время по Владивостоку
    if message.from_user.id != ADMIN_ID and not is_working_hours():
        await message.answer("Режим работы закончен, с 10:00 по 23:00 Вам ответит Художник.")
        return

    # Логика для админа или в рабочее время
    if message.from_user.id != ADMIN_ID:
        last_user_id = message.from_user.id
        await message.answer("Ваше сообщение получено! Художник ответит вам в ближайшее время.")
        # Пересылка сообщения админу
        await bot.send_message(
            ADMIN_ID, 
            f"📩 Новое сообщение от @{message.from_user.username} (ID: {message.from_user.id}):\n\n{message.text}"
        )
    else:
        # Ответ админа пользователю
        if last_user_id:
            await bot.send_message(last_user_id, f"🎨 Ответ от Художника:\n\n{message.text}")
            await message.answer("Ответ успешно отправлен пользователю!")
        else:
            await message.answer("Пока нет активных пользователей для ответа.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
