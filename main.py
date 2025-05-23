import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from steps import steps
import os

API_TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "@sunxstyle"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

def get_step_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for step in steps:
        total = step["duration_min"]
        hours = int(total // 60)
        mins = int(total % 60)
        time_str = f"{hours} ч {mins} м" if hours else f"{mins} м"
        label = f"Шаг {step['step']} ({time_str})"
        keyboard.insert(KeyboardButton(label))
    keyboard.add(KeyboardButton("ℹ️ Инфо"))
    return keyboard

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(
        "Привет, солнце! ☀️\n"
        "Ты в таймере по методу суперкомпенсации.\n"
        "Кожа адаптируется к солнцу постепенно — и загар становится ровным, глубоким и без ожогов.\n\n"
        "Начинай с шага 1. Даже если уже немного загорел(а), важно пройти путь с начала.\n"
        "Каждый новый день и после перерыва — возвращайся на 2 шага назад.\n\n"
        "Хочешь разобраться подробнее — жми ℹ️ Инфо.",
        reply_markup=get_step_buttons()
    )

@dp.message_handler(lambda message: message.text == "ℹ️ Инфо")
async def send_info(message: types.Message):
    await message.answer(
        "ℹ️ Метод суперкомпенсации — это безопасный, пошаговый подход к загару.\n"
        "Он помогает коже адаптироваться к солнцу, снижая риск ожогов и пятен.\n\n"
        "Рекомендуем загорать с 7:00 до 11:00 и после 17:00 — в это время солнце мягкое,\n"
        "и при отсутствии противопоказаний можно загорать без SPF.\n"
        "Так кожа включает свою естественную защиту: вырабатывается меланин и гормоны адаптации.\n\n"
        "С 11:00 до 17:00 — солнце более агрессивное. Если остаёшься на улице — надевай одежду, головной убор или используй SPF.\n\n"
        "Каждый новый день и после перерыва — возвращайся на 2 шага назад.\n"
        "Если есть вопросы — пиши: @sunxbeach_director."
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
