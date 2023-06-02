import aiogram.types
from aiogram import types
from aiogram.dispatcher import filters

import database
import responses.main_menu
import responses.start
from database import queries, session_factory
from loader import dp
from repositories.database.users import UserRepository
from services import notifications


@dp.message_handler(filters.Text('✅ Accept'))
async def accept_rules(message: aiogram.types.Message):
    user_repository = UserRepository(session_factory)
    user_repository.create(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
    )
    await responses.start.NewUserResponse(message)
    await responses.main_menu.UserMainMenuResponse(message)
    await notifications.NewUserNotification(
        user_id=message.from_user.id,
        username=message.from_user.username,
    ).send()


@dp.message_handler(filters.CommandStart())
async def start(message: types.Message):
    with database.create_session() as session:
        if queries.check_is_user_exists(session, message.from_user.id):
            await responses.start.UserExistsResponse(message)
            await responses.main_menu.UserMainMenuResponse(message)
        else:
            await responses.start.RulesResponse(message)
