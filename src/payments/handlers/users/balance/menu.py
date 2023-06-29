from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from common.views import answer_view
from payments.views import UserBalanceMenuView
from users.repositories import UserRepository

__all__ = ('register_handlers',)


async def on_show_user_balance_menu(
        message: Message,
        state: FSMContext,
        user_repository: UserRepository,
) -> None:
    await state.finish()
    user = user_repository.get_by_telegram_id(message.from_user.id)
    view = UserBalanceMenuView(balance=user.balance)
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_user_balance_menu,
        Text('💲 Balance'),
        state='*',
    )
