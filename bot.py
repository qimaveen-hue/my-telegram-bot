import asyncio
from datetime import datetime
import pytz
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8982333001:AAGHdSLAu3OPg6agkMfv7qaASf47DQUNnWU"
ADMIN_ID = 6482057553

TIMEZONE = pytz.timezone('Asia/Vladivostok')

bot = Bot(token=TOKEN)
dp = Dispatcher()

last_user_id = None

def is_working_hours() -> bool:
    now = datetime.now(TIMEZONE)
    return now.hour >= 10 or now.hour == 0

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ᨳິ Bust Up"), KeyboardButton(text="👤 2. Half Body")],
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
    
    if message.text == "ᨳິ Bust Up":
        photo_url = "https://i.ibb.co/60BrtmG8/image-18.png"
        caption_text = (
            "**ᨳິ Bust Up**\n\n"
            "• Портрет по грудь.\n"
            "• Детализированная проработка.\n\n"
            "Если хотите заказать этот тип арта — напишите сообщение прямо в этот чат!"
        )
        await message.answer_photo(photo=photo_url, caption=caption_text, parse_mode="Markdown")
        return

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

async def main():
    await dp.start_polling(bot)

if __name__ == "main":
    asyncio.run(main())
