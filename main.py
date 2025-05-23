import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import CommandStart
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
        label = f"Шаг {step['step']} ({step['duration_min']}м)"
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

async def start_step(message, step_data):
    user_id = message.from_user.id
    user_state[user_id] = {"cancel": False, "position_index": 0, "task": None, "step": step_data}

    await message.answer(
        await message.answer(
            f"Шаг {step_data['step']} — {step_data['duration_min']} минут.\n"
            "Следи за временем и положением тела.\n"
            "Если был перерыв — начни с шага “минус два” от последнего."
        )
    )

    async def run_positions():
        for i, pos in enumerate(step_data["positions"]):
            if user_state[user_id]["cancel"]:
                return
            user_state[user_id]["position_index"] = i
            await message.answer(f"{pos['name']} — {pos['min']} мин", reply_markup=get_control_buttons())
            await asyncio.sleep(pos["min"] * 60)
        await message.answer("Шаг завершён! ☀️", reply_markup=get_step_buttons())

    task = asyncio.create_task(run_positions())
    user_state[user_id]["task"] = task

@dp.message_handler(lambda message: message.text.startswith("Шаг"))
async def handle_step(message: types.Message):
    step_num = int(message.text.split()[1])
    step = next((s for s in steps if s["step"] == step_num), None)
    if step:
        await start_step(message, step)

@dp.message_handler(lambda message: message.text == "⏭️ Пропустить позицию")
async def skip_position(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_state:
        state = user_state[user_id]
        task = state.get("task")
        if task and not task.done():
            task.cancel()
        state["cancel"] = False
        state["position_index"] += 1
        pos_index = state["position_index"]
        step_data = state["step"]
        if pos_index >= len(step_data["positions"]):
            await message.answer("Шаг завершён! ☀️", reply_markup=get_step_buttons())
            return
        pos = step_data["positions"][pos_index]
        async def continue_step():
            await message.answer(f"{pos['name']} — {pos['min']} мин", reply_markup=get_control_buttons())
            await asyncio.sleep(pos["min"] * 60)
            await skip_position(message)
        task = asyncio.create_task(continue_step())
        state["task"] = task

@dp.message_handler(lambda message: message.text == "⛔ Завершить")
async def stop_session(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_state:
        task = user_state[user_id].get("task")
        if task and not task.done():
            task.cancel()
        del user_state[user_id]
    await message.answer("Сеанс завершён. Можешь вернуться позже и начать заново ☀️", reply_markup=get_step_buttons())

@dp.message_handler(lambda message: message.text == "📋 Вернуться к шагам")
async def return_to_steps(message: types.Message):
    await message.answer("Выбирай шаг:", reply_markup=get_step_buttons())

@dp.message_handler(lambda message: message.text == "↩️ Назад на 2 шага")
async def go_back_2_steps(message: types.Message):
    current_text = message.text
    await message.answer("Вернись на 2 шага назад — выбери нужный шаг вручную 👇", reply_markup=get_step_buttons())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)