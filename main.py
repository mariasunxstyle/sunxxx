import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import CommandStart
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
from steps import steps

load_dotenv()
API_TOKEN = os.getenv("TOKEN")
CHANNEL_ID = "@sunxstyle"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

def format_duration(mins):
    h, m = divmod(mins, 60)
    return f"{h}ч {m}м" if h else f"{m}м"

def get_step_buttons():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for step in steps:
        label = f"Шаг {step['step']} ({format_duration(step['duration_min'])})"
        keyboard.insert(types.KeyboardButton(label))
    keyboard.add(types.KeyboardButton("ℹ️ Инфо"))
    return keyboard

def get_control_buttons():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("⏭️ Пропустить позицию")
    keyboard.add("⛔ Завершить")
    keyboard.add("↩️ Назад на 2 шага")
    keyboard.add("📋 Вернуться к шагам")
    return keyboard

@dp.message_handler(CommandStart())
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    chat_member = await bot.get_chat_member(CHANNEL_ID, user_id)
    if chat_member.status in ["left", "kicked"]:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("✅ Я подписан(а)")
        await message.answer("Бот работает только при подписке на Telegram-канал @sunxstyle", reply_markup=keyboard)
        return

    await message.answer(
        "Привет, солнце! ☀️
"
        "Ты в таймере по методу суперкомпенсации.
"
        "Кожа адаптируется к солнцу постепенно — и загар становится ровным, глубоким и без ожогов.

"
        "Начинай с шага 1. Даже если уже немного загорел(а), важно пройти путь с начала.
"
        "Каждый новый день и после перерыва — возвращайся на 2 шага назад.

"
        "Хочешь разобраться подробнее — жми ℹ️ Инфо. Там всё по делу.",
        reply_markup=get_step_buttons()
    )

@dp.message_handler(lambda message: message.text == "ℹ️ Инфо")
async def send_info(message: types.Message):
    await message.answer(
        "ℹ️ Метод суперкомпенсации — это безопасный, пошаговый подход к загару.
"
        "Он помогает коже адаптироваться к солнцу, снижая риск ожогов и пятен.

"
        "Рекомендуем загорать с 7:00 до 11:00 и после 17:00 — в это время солнце мягкое,
"
        "и при отсутствии противопоказаний можно загорать без SPF.
"
        "Так кожа включает свою естественную защиту: вырабатывается меланин и гормоны адаптации.

"
        "С 11:00 до 17:00 — солнце более агрессивное. Если остаёшься на улице — надевай одежду, головной убор или используй SPF.

"
        "Каждый новый день и после перерыва — возвращайся на 2 шага назад.
"
        "Это нужно, чтобы кожа не перегружалась и постепенно усиливала защиту.

"
        "Если есть вопросы — пиши: @sunxbeach_director."
    )

@dp.message_handler(lambda message: message.text.startswith("Шаг"))
async def handle_step(message: types.Message):
    step_num = int(message.text.split()[1])
    step = next((s for s in steps if s["step"] == step_num), None)
    if step:
        await message.answer(f"Шаг {step['step']} — {step['duration_min']} минут.
Следи за временем и положением тела.
Если был перерыв — начни с шага “минус два” от последнего.")
        text = "
".join([f"{p['name']} — {p['min']} мин" for p in step["positions"]])
        await message.answer(text, reply_markup=get_control_buttons())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)