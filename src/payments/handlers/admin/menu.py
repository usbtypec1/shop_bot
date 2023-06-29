import contextlib

import structlog
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, Update
from aiogram.utils.exceptions import MessageNotModified
from structlog.stdlib import BoundLogger

from common.filters import AdminFilter
from common.views import answer_view, edit_message_by_view
from payments.callback_data import PaymentSystemCredentialsStatusCallbackData
from payments.exceptions import BalanceAmountValidatorError
from payments.views import PaymentManagementMenuView, CoinbaseManagementMenuView
from services.payments_apis import CoinbaseAPI

logger: BoundLogger = structlog.get_logger('app')


async def on_balance_amount_validation_error(
        update: Update,
        _: BalanceAmountValidatorError,
) -> bool:
    text = '❌ Incorrect balance amount!'
    if update.message is not None:
        await update.message.answer(text)
    if update.callback_query is not None:
        await update.callback_query.answer(text, show_alert=True)
    return True


async def payments_management(
        message: Message,
        state: FSMContext,
) -> None:
    await state.finish()
    view = PaymentManagementMenuView()
    await answer_view(message=message, view=view)


async def on_show_coinbase_management_menu(
        message_or_callback_query: Message | CallbackQuery,
        coinbase_api: CoinbaseAPI,
        state: FSMContext,
) -> None:
    await state.finish()
    is_valid = coinbase_api.check()
    view = CoinbaseManagementMenuView(is_valid)
    if isinstance(message_or_callback_query, Message):
        await answer_view(message=message_or_callback_query, view=view)
        return
    with contextlib.suppress(MessageNotModified):
        await edit_message_by_view(
            message=message_or_callback_query.message,
            view=view,
        )


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_errors_handler(
        on_balance_amount_validation_error,
        exception=BalanceAmountValidatorError,
    )
    dispatcher.register_message_handler(
        payments_management,
        Text('💳 Payment Management'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_message_handler(
        on_show_coinbase_management_menu,
        Text('🌐 Coinbase'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        on_show_coinbase_management_menu,
        PaymentSystemCredentialsStatusCallbackData().filter(),
        AdminFilter(),
        state='*',
    )
