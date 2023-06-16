from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text, CommandStart
from aiogram.types import Message

import database
from common.filters import AdminFilter
from common.views import answer_view
from database import queries
from services import notifications
from users.repositories import UserRepository
from users.views import RulesView, AdminMenuView, UserGreetingsView


async def accept_rules(
        message: Message,
        user_repository: UserRepository,
) -> None:
    user_repository.create(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
    )
    await answer_view(message=message, view=UserGreetingsView())
    await answer_view(message=message, view=AdminMenuView())
    await notifications.NewUserNotification(
        user_id=message.from_user.id,
        username=message.from_user.username,
    ).send()


async def start(message: Message) -> None:
    with database.create_session() as session:
        if queries.check_is_user_exists(session, message.from_user.id):
            await message.answer('Comeback Message')
            await answer_view(message=message, view=AdminMenuView())
        else:
            await answer_view(message=message, view=RulesView())


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        accept_rules,
        Text('✅ Accept'),
        state='*',
    )
    dispatcher.register_message_handler(
        start,
        CommandStart(),
        AdminFilter(),
        state='*',
    )
