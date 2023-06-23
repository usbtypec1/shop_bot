import shutil

import structlog
from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, CommandStart
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery
from aiogram.types import Message

import config
from common.filters import AdminFilter
from common.views import answer_view, send_views
from users.exceptions import UserNotInDatabase
from users.repositories import UserRepository
from users.views import (
    AdminMenuView, UserGreetingsView,
    NewUserNotificationView
)
from users.views import UserMenuView, RulesView

logger = structlog.get_logger('app')


async def on_accept_rules(
        message: Message,
        user_repository: UserRepository,
        bot: Bot,
        is_admin: bool,
) -> None:
    user_repository.create(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
    )
    await answer_view(
        message=message,
        view=UserGreetingsView(message.from_user.full_name),
    )
    view = AdminMenuView() if is_admin else UserMenuView()
    await answer_view(message=message, view=view)

    view = NewUserNotificationView(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
    )
    await send_views(
        bot=bot,
        chat_ids=config.AppSettings().admins_id,
        view=view
    )


async def on_start(
        message: Message,
        state: FSMContext,
        user_repository: UserRepository,
        is_admin: bool,
) -> None:
    await state.finish()
    try:
        user = user_repository.get_by_telegram_id(message.from_user.id)
    except UserNotInDatabase:
        await answer_view(message=message, view=RulesView())
        return
    view = AdminMenuView() if is_admin else UserMenuView()
    await answer_view(message=message, view=view)


async def cancel(
        message: Message,
        state: FSMContext,
):
    shutil.rmtree(
        config.PENDING_DIR_PATH / str(message.from_user.id),
        ignore_errors=True,
    )
    await state.finish()
    await message.answer('⛔️ Canceled')


async def close(
        query: CallbackQuery,
        state: FSMContext,
):
    shutil.rmtree(
        config.PENDING_DIR_PATH / str(query.from_user.id),
        ignore_errors=True,
    )
    await state.finish()
    await query.message.delete()


async def admin_back(
        message: Message,
        state: FSMContext,
):
    shutil.rmtree(
        config.PENDING_DIR_PATH / str(message.from_user.id),
        ignore_errors=True,
    )
    await state.finish()
    await answer_view(message=message, view=AdminMenuView())


async def user_back(
        message: Message,
        state: FSMContext,
):
    shutil.rmtree(
        config.PENDING_DIR_PATH / str(message.from_user.id),
        ignore_errors=True,
    )
    await state.finish()
    await answer_view(message=message, view=UserMenuView())


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_accept_rules,
        Text('✅ Accept'),
        state='*',
    )
    dispatcher.register_message_handler(
        on_start,
        CommandStart(),
        state='*',
    )
    dispatcher.register_message_handler(
        cancel,
        Command('cancel'),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        close,
        Text('close'),
        state='*',
    )
    dispatcher.register_message_handler(
        admin_back,
        AdminFilter(),
        Text('⬅️ Back'),
        state='*',
    )
    dispatcher.register_message_handler(
        user_back,
        Text('⬅️ Back'),
        state='*',
    )
    logger.debug('Registered common handlers')
