# test_bot_messages.py
from aiogram.types import Message, Chat, User
from datetime import datetime
from aiogram import types

async def simulate_user_message(dp, user_id, text):
    fake_msg = Message(
        message_id=999,
        date=datetime.now(),
        chat=Chat(id=user_id, type="private"),
        from_user=User(id=user_id, is_bot=False, first_name="TestUser"),
        text=text,
        message_thread_id=None,
        is_bot=False,
        sender_chat=None
    )
    await dp.process_update(types.Update(message=fake_msg))
