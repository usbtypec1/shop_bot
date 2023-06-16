import shutil

import structlog
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Command
from aiogram.types import Message, CallbackQuery

import config
from common.filters import AdminFilter
from common.views import answer_view
from users.views import AdminMenuView, UserMenuView

logger = structlog.get_logger('app')


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
