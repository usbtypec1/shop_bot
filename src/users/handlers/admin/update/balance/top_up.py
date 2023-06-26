from decimal import Decimal

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ContentType,
    ChatType,
)

from common.filters import AdminFilter
from common.views import edit_message_by_view, answer_view
from payments.services import parse_balance_amount
from sales.repositories import SaleRepository
from users.callback_data import UserBalanceTopUpCallbackData
from users.repositories import UserRepository
from users.states import UserBalanceTopUpStates
from users.views import (
    UserBalanceTopUpAskForConfirmationView,
    UserBalanceTopUpReceiptView, UserDetailView,
)

__all__ = ('register_handlers',)


async def on_start_top_up_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    user_id: int = callback_data['user_id']
    await UserBalanceTopUpStates.amount.set()
    await state.update_data(user_id=user_id)
    await callback_query.message.answer(
        '💱 Please enter the amount'
        ' you would like to add to the user\'s balance'
    )


async def on_amount_to_top_up_input(
        message: Message,
        state: FSMContext,
) -> None:
    balance_amount = parse_balance_amount(message.text)
    await UserBalanceTopUpStates.payment_method.set()
    await state.update_data(amount_to_top_up=balance_amount)
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='💳 Cashapp',
                    callback_data='cashapp',
                ),
            ],
            [
                InlineKeyboardButton(
                    text='💎 Other',
                    callback_data='other',
                )
            ],
        ]
    )
    await message.answer(
        text='❓ Enter the manual payment method the user paid',
        reply_markup=markup,
    )


async def on_balance_top_up_method_choice(
        callback_query: CallbackQuery,
        state: FSMContext,
        user_repository: UserRepository,
) -> None:
    payment_method = callback_query.data
    await UserBalanceTopUpStates.confirm.set()
    await state.update_data(payment_method=payment_method)
    state_data = await state.get_data()
    user_id: int = state_data['user_id']
    amount_to_top_up: Decimal = state_data['amount_to_top_up']
    user = user_repository.get_by_id(user_id)
    view = UserBalanceTopUpAskForConfirmationView(
        user=user,
        amount_to_top_up=amount_to_top_up,
        payment_method=payment_method
    )
    await edit_message_by_view(message=callback_query.message, view=view)


async def on_balance_top_up_confirm(
        callback_query: CallbackQuery,
        state: FSMContext,
        user_repository: UserRepository,
        sale_repository: SaleRepository,
) -> None:
    state_data = await state.get_data()
    await state.finish()
    user_id: int = state_data['user_id']
    amount_to_top_up: Decimal = state_data['amount_to_top_up']
    payment_method: str = state_data['payment_method']

    user_repository.top_up_balance(
        user_id=user_id,
        amount_to_top_up=amount_to_top_up
    )
    user = user_repository.get_by_id(user_id)
    orders_count = sale_repository.count_by_user_id(user_id)
    view = UserBalanceTopUpReceiptView(
        user=user,
        amount_to_top_up=amount_to_top_up,
        payment_method=payment_method,
    )
    await edit_message_by_view(message=callback_query.message, view=view)
    view = UserDetailView(
        user=user,
        number_of_orders=orders_count,
    )
    await answer_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_start_top_up_flow,
        AdminFilter(),
        UserBalanceTopUpCallbackData().filter(),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_message_handler(
        on_amount_to_top_up_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state=UserBalanceTopUpStates.amount,
    )
    dispatcher.register_callback_query_handler(
        on_balance_top_up_method_choice,
        AdminFilter(),
        chat_type=ChatType.PRIVATE,
        state=UserBalanceTopUpStates.payment_method,
    )
    dispatcher.register_callback_query_handler(
        on_balance_top_up_confirm,
        AdminFilter(),
        Text('top-up-user-balance-confirm'),
        chat_type=ChatType.PRIVATE,
        state=UserBalanceTopUpStates.confirm,
    )
