import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from steps import steps

API_TOKEN = "7856116405:AAFWDJM4yfMydjmnI7m-iYnTdEEbcnq9d9Y"
CHANNEL_ID = "@sunxstyle"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

user_state = {}

def get_step_buttons():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for step in steps:
        minutes = int(step['duration_min']) if step['duration_min'].is_integer() else step['duration_min']
        total = step['duration_min']
        if total >= 60:
            hours = int(total // 60)
            mins = int(total % 60)
            time_str = f"{hours} ч {mins} м" if mins else f"{hours} ч"
        else:
            time_str = f"{int(total)} м" if total.is_integer() else f"{total} м"
        label = f"Шаг {step['step']} ({time_str})"
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

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(
        "Привет, солнце! ☀️ Ты в таймере по методу суперкомпенсации. "
        "Кожа адаптируется к солнцу постепенно — и загар становится ровным, глубоким и без ожогов. "
        "Начинай с шага 1. Даже если уже немного загорел(а), важно пройти путь с начала. "
        "Каждый новый день и после перерыва — возвращайся на 2 шага назад. "
        "Хочешь разобраться подробнее — жми ℹ️ Инфо. Там всё по делу.",
        reply_markup=get_step_buttons()
    )

@dp.message_handler(lambda message: message.text == "ℹ️ Инфо")
async def send_info(message: types.Message):
    await message.answer(
        "ℹ️ Метод суперкомпенсации — это безопасный, пошаговый подход к загару. "
        "Он помогает коже адаптироваться к солнцу, снижая риск ожогов и пятен. "
        "Рекомендуем загорать с 7:00 до 11:00 и после 17:00 — в это время солнце мягкое, "
        "и при отсутствии противопоказаний можно загорать без SPF. "
        "Так кожа включает свою естественную защиту: вырабатывается меланин и гормоны адаптации. "
        "С 11:00 до 17:00 — солнце более агрессивное. Если остаёшься на улице — надевай одежду, головной убор или используй SPF. "
        "Каждый новый день и после перерыва — возвращайся на 2 шага назад. "
        "Если есть вопросы — пиши: @sunxbeach_director."
    )

async def run_step_positions(message, step_data):
    user_id = message.from_user.id
    user_state[user_id] = {
        "cancel": False,
        "position_index": 0,
        "step": step_data,
        "task": None,
    }

    await message.answer(
        f"Шаг {step_data['step']} — {step_data['duration_min']} минут.\n"

    async def timer():
        for i, pos in enumerate(step_data["positions"]):
            if user_state[user_id]["cancel"]:
                return
            user_state[user_id]["position_index"] = i
            minutes = int(pos['min']) if pos['min'].is_integer() else pos['min']
            await message.answer(f"{pos['name']} — {minutes} мин", reply_markup=get_control_buttons())
            await asyncio.sleep(pos["min"] * 60)
        await message.answer("Шаг завершён! ☀️", reply_markup=get_step_buttons())

    task = asyncio.create_task(timer())
    user_state[user_id]["task"] = task

@dp.message_handler(lambda message: message.text.startswith("Шаг"))
async def handle_step(message: types.Message):
    step_num = int(message.text.split()[1])
    step = next((s for s in steps if s["step"] == step_num), None)
    if step:
        await run_step_positions(message, step)

@dp.message_handler(lambda message: message.text == "⏭️ Пропустить позицию")
async def skip_position(message: types.Message):
    user_id = message.from_user.id
    state = user_state.get(user_id)
    if not state:
        return
    state["cancel"] = True
    step_data = state["step"]
    next_index = state["position_index"] + 1
    if next_index >= len(step_data["positions"]):
        await message.answer("Шаг завершён! ☀️", reply_markup=get_step_buttons())
        return
    await run_step_positions(message, {
        "step": step_data["step"],
        "duration_min": sum(p["min"] for p in step_data["positions"][next_index:]),
        "positions": step_data["positions"][next_index:]
    })

@dp.message_handler(lambda message: message.text == "⛔ Завершить")
async def stop_session(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_state:
        user_state[user_id]["cancel"] = True
        user_state.pop(user_id)
    await message.answer("Сеанс завершён. Можешь вернуться позже и начать заново ☀️", reply_markup=get_step_buttons())

@dp.message_handler(lambda message: message.text == "↩️ Назад на 2 шага")
async def go_back(message: types.Message):
    await message.answer("Вернись на 2 шага назад — выбери нужный шаг вручную", reply_markup=get_step_buttons())

@dp.message_handler(lambda message: message.text == "📋 Вернуться к шагам")
async def return_to_steps(message: types.Message):
    await message.answer("Выбирай шаг:", reply_markup=get_step_buttons())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)