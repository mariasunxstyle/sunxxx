# run_bot_test.py
import asyncio
from main import dp
from test_bot_messages import simulate_user_message

async def test_all():
    user_id = 123456789
    await simulate_user_message(dp, user_id, "Шаг 1")
    await asyncio.sleep(1)
    await simulate_user_message(dp, user_id, "⏭️ Пропустить")
    await asyncio.sleep(1)
    await simulate_user_message(dp, user_id, "📋 Вернуться к шагам")
    await asyncio.sleep(1)
    await simulate_user_message(dp, user_id, "⛔ Завершить")

if __name__ == '__main__':
    asyncio.run(test_all())
