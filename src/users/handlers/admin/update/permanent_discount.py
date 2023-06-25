from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, Message, ChatType, ContentType

from common.filters import AdminFilter
from common.views import edit_message_by_view, answer_view
from sales.repositories import SaleRepository
from users.callback_data import UserUpdateCallbackData
from users.repositories import UserRepository
from users.services import parse_permanent_discount
from users.states import UserGrantPermanentDiscountStates
from users.views import (
    UserDetailView,
    UserPermanentDiscountGrantingReasonsView,
    UserPermanentDiscountGrantingConfirmView,
)

__all__ = ('register_handlers',)


async def on_start_permanent_discount_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    user_id: int = callback_data['user_id']
    await UserGrantPermanentDiscountStates.discount_value.set()
    await state.update_data(user_id=user_id)
    await callback_query.message.edit_text(
        'Please enter the permanent discount percentage'
        ' you would like to grant to the user (from 0 to 99).'
        '\nTo remove discount for the user, enter "0"'
    )


async def on_permanent_discount_value_input(
        message: Message,
        state: FSMContext,
) -> None:
    permanent_discount = parse_permanent_discount(message.text)
    await UserGrantPermanentDiscountStates.reason.set()
    await state.update_data(permanent_discount=permanent_discount)
    view = UserPermanentDiscountGrantingReasonsView()
    await answer_view(message=message, view=view)


async def on_permanent_discount_granting_reason_choice(
        callback_query: CallbackQuery,
        state: FSMContext,
        user_repository: UserRepository,
) -> None:
    state_data = await state.get_data()
    user_id: int = state_data['user_id']
    permanent_discount: int = state_data['permanent_discount']
    reason: str = callback_query.data
    await UserGrantPermanentDiscountStates.confirm.set()
    await state.update_data(reason=reason)
    user = user_repository.get_by_id(user_id)
    view = UserPermanentDiscountGrantingConfirmView(
        user=user,
        reason=reason,
        permanent_discount=permanent_discount,
    )
    await edit_message_by_view(message=callback_query.message, view=view)


async def on_permanent_discount_grant_confirm(
        callback_query: CallbackQuery,
        state: FSMContext,
        user_repository: UserRepository,
        sale_repository: SaleRepository,
) -> None:
    state_data = await state.get_data()
    await state.finish()
    user_id: int = state_data['user_id']
    permanent_discount: int = state_data['permanent_discount']
    user_repository.update_permanent_discount(
        user_id=user_id,
        permanent_discount=permanent_discount,
    )
    user = user_repository.get_by_id(user_id)
    orders_count = sale_repository.count_by_user_id(user_id)
    view = UserDetailView(user=user, number_of_orders=orders_count)
    await edit_message_by_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_start_permanent_discount_update_flow,
        AdminFilter(),
        UserUpdateCallbackData().filter(field='permanent-discount'),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_message_handler(
        on_permanent_discount_value_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state=UserGrantPermanentDiscountStates.discount_value,
    )
    dispatcher.register_callback_query_handler(
        on_permanent_discount_granting_reason_choice,
        AdminFilter(),
        chat_type=ChatType.PRIVATE,
        state=UserGrantPermanentDiscountStates.reason,
    )
    dispatcher.register_callback_query_handler(
        on_permanent_discount_grant_confirm,
        AdminFilter(),
        Text('permanent-discount-granting-confirm'),
        chat_type=ChatType.PRIVATE,
        state=UserGrantPermanentDiscountStates.confirm,
    )
