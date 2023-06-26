from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, Message, ChatType, ContentType

from common.filters import AdminFilter
from common.views import answer_view, edit_message_by_view
from payments.services import parse_balance_amount
from sales.repositories import SaleRepository
from users.callback_data import UserUpdateCallbackData
from users.repositories import UserRepository
from users.states import UserUpdateStates
from users.views import UserDetailView, UserUpdateMaxCartCostView

__all__ = ('register_handlers',)


async def on_start_max_cart_cost_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    user_id: int = callback_data['user_id']
    await UserUpdateStates.max_cart_cost.set()
    await state.update_data(user_id=user_id)
    view = UserUpdateMaxCartCostView()
    await edit_message_by_view(message=callback_query.message, view=view)


async def on_remove_max_cart_cost(
        callback_query: CallbackQuery,
        state: FSMContext,
        user_repository: UserRepository,
        sale_repository: SaleRepository,
) -> None:
    state_data = await state.get_data()
    user_id: int = state_data['user_id']
    user_repository.update_max_cart_cost(
        user_id=user_id,
        max_cart_cost=None,
    )
    user = user_repository.get_by_id(user_id)
    orders_count = sale_repository.count_by_user_id(user_id)
    view = UserDetailView(user=user, number_of_orders=orders_count)
    await edit_message_by_view(message=callback_query.message, view=view)


async def on_new_max_cart_cost_input(
        message: Message,
        state: FSMContext,
        user_repository: UserRepository,
        sale_repository: SaleRepository,
) -> None:
    max_cart_cost = parse_balance_amount(message.text)
    state_data = await state.get_data()
    user_id: int = state_data['user_id']
    user_repository.update_max_cart_cost(
        user_id=user_id,
        max_cart_cost=max_cart_cost,
    )
    user = user_repository.get_by_id(user_id)
    orders_count = sale_repository.count_by_user_id(user_id)
    view = UserDetailView(user=user, number_of_orders=orders_count)
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_start_max_cart_cost_update_flow,
        AdminFilter(),
        UserUpdateCallbackData().filter(field='max-cart-cost'),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        on_remove_max_cart_cost,
        AdminFilter(),
        Text('remove-max-cart-cost'),
        chat_type=ChatType.PRIVATE,
        state=UserUpdateStates.max_cart_cost,
    )
    dispatcher.register_message_handler(
        on_new_max_cart_cost_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state=UserUpdateStates.max_cart_cost,
    )
