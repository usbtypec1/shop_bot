from decimal import Decimal

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import (
    CallbackQuery,
    Message,
    ContentType,
    ChatType,
)

from common.filters import AdminFilter
from common.views import edit_message_by_view, answer_view
from payments.services import parse_balance_amount
from sales.repositories import SaleRepository
from users.callback_data import UserSetSpecificBalanceCallbackData
from users.repositories import UserRepository
from users.states import UserSetSpecificBalanceStates
from users.views import (
    UserSetSpecificBalanceAskForConfirmationView,
    UserSetSpecificBalanceReceiptView, UserDetailView,
    UserSetSpecificBalanceReasonsView,
)

__all__ = ('register_handlers',)


async def on_start_balance_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    user_id: int = callback_data['user_id']
    await UserSetSpecificBalanceStates.amount.set()
    await state.update_data(user_id=user_id)
    await callback_query.message.edit_text(
        '💱 Please type the amount for the new balance'
    )


async def on_new_balance_amount_input(
        message: Message,
        state: FSMContext,
) -> None:
    balance_amount = parse_balance_amount(message.text)
    await UserSetSpecificBalanceStates.reason.set()
    await state.update_data(amount_to_set=balance_amount)
    view = UserSetSpecificBalanceReasonsView()
    await answer_view(message=message, view=view)


async def on_balance_update_reason_choice(
        callback_query: CallbackQuery,
        state: FSMContext,
        user_repository: UserRepository,
) -> None:
    reason = callback_query.data
    await UserSetSpecificBalanceStates.confirm.set()
    await state.update_data(reason=reason)
    state_data = await state.get_data()
    user_id: int = state_data['user_id']
    amount_to_set: Decimal = state_data['amount_to_set']
    user = user_repository.get_by_id(user_id)
    view = UserSetSpecificBalanceAskForConfirmationView(
        user=user,
        amount_to_set=amount_to_set,
        reason=reason
    )
    await edit_message_by_view(message=callback_query.message, view=view)


async def on_set_specific_balance_confirm(
        callback_query: CallbackQuery,
        state: FSMContext,
        user_repository: UserRepository,
        sale_repository: SaleRepository,
) -> None:
    state_data = await state.get_data()
    await state.finish()
    user_id: int = state_data['user_id']
    amount_to_set: Decimal = state_data['amount_to_set']
    reason: str = state_data['reason']

    user = user_repository.get_by_id(user_id)
    old_balance = user.balance

    user_repository.update_balance(
        user_id=user_id,
        amount_to_set=amount_to_set,
    )
    user = user_repository.get_by_id(user_id)
    orders_count = sale_repository.count_by_user_id(user_id)
    view = UserSetSpecificBalanceReceiptView(
        user=user,
        reason=reason,
        old_balance=old_balance,
        new_balance=user.balance,
    )
    await edit_message_by_view(message=callback_query.message, view=view)
    view = UserDetailView(
        user=user,
        number_of_orders=orders_count,
    )
    await answer_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_start_balance_update_flow,
        AdminFilter(),
        UserSetSpecificBalanceCallbackData().filter(),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_message_handler(
        on_new_balance_amount_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state=UserSetSpecificBalanceStates.amount,
    )
    dispatcher.register_callback_query_handler(
        on_balance_update_reason_choice,
        AdminFilter(),
        chat_type=ChatType.PRIVATE,
        state=UserSetSpecificBalanceStates.reason,
    )
    dispatcher.register_callback_query_handler(
        on_set_specific_balance_confirm,
        AdminFilter(),
        Text('set-specific-user-balance-confirm'),
        chat_type=ChatType.PRIVATE,
        state=UserSetSpecificBalanceStates.confirm,
    )
