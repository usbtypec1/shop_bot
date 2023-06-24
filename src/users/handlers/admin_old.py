import decimal

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

import database
import responses.users
from common.filters import AdminFilter
from database import queries
from keyboards.inline.callback_factories import (
    UserCallbackFactory,
    EditUserBalanceCallbackFactory,
    TopUpUserBalanceCallbackFactory,
)
from users.repositories import UserRepository
from users.states import (
    EditBalanceStates,
    TopUpBalanceStates,
)


async def ban_user(query: CallbackQuery, callback_data: dict[str: str]) -> None:
    with database.create_session() as session:
        user = queries.get_user(session, int(callback_data['id']))
        await responses.users.BanUserAlertResponse(query, user, callback_data)


async def ban_user_confirm(
        query: CallbackQuery,
        callback_data: dict[str, str],
        user_repository: UserRepository,
) -> None:
    user_id = int(callback_data['id'])
    if callback_data['is_confirmed'] == 'yes':
        user_repository.ban_by_id(user_id)
    user = user_repository.get_by_id(user_id)

    with database.create_session() as session:
        number_of_orders = queries.count_user_orders(session, user.id)
        await responses.users.UserResponse(query, user, number_of_orders,
                                           callback_data)


async def unban_user(
        query: CallbackQuery,
        callback_data: dict[str: str],
) -> None:
    with database.create_session() as session:
        user = queries.get_user(session, int(callback_data['id']))
        await responses.users.UnbanUserAlertResponse(query, user, callback_data)


async def unban_user_confirm(
        query: CallbackQuery,
        callback_data: dict[str, str],
        user_repository: UserRepository,
) -> None:
    user_id = int(callback_data['id'])
    if callback_data['is_confirmed'] == 'yes':
        user_repository.unban_by_id(user_id)
    user = user_repository.get_by_id(user_id)

    with database.create_session() as session:
        number_of_orders = queries.count_user_orders(session, user.id)
        await responses.users.UserResponse(query, user, number_of_orders,
                                           callback_data)


async def edit_balance(
        query: CallbackQuery,
        callback_data: dict[str, str],
        state: FSMContext,
) -> None:
    await responses.users.NewBalanceResponse(query)
    await EditBalanceStates.waiting_balance.set()
    await state.update_data({'callback_data': callback_data})


async def enter_new_balance(
        message: Message,
        state: FSMContext,
) -> None:
    if message.text.replace('.', '').isdigit():
        callback_data = (await state.get_data())['callback_data']
        with database.create_session() as session:
            user = queries.get_user(session, callback_data['user_id'])
            await responses.users.EditBalanceAlertResponse(
                message, user, message.text, callback_data
            )
            await state.finish()
    else:
        await responses.users.IncorrectBalanceResponse(message)


async def balance_editing_reason(
        query: CallbackQuery,
        callback_data: dict[str, str],
) -> None:
    if callback_data['is_confirmed'] == 'yes':
        await responses.users.BalanceEditingReasonResponse(query, callback_data)
    else:
        with database.create_session() as session:
            user_id = int(callback_data['user_id'])
            user = queries.get_user(session, user_id)
            await responses.users.UserResponse(
                query, user, queries.count_user_orders(session, user_id)
            )


async def edit_balance_cb(
        query: CallbackQuery,
        callback_data: dict[str, str],
) -> None:
    with database.create_session() as session:
        new_balance = float(callback_data['balance'])
        user_id = int(callback_data['user_id'])
        match callback_data['reason']:
            case 'p2p_delivery':
                reason = 'P2P delivery'
            case 'admin_mistake':
                reason = 'Admin mistake'
            case 'refunded_payment':
                reason = 'Refunded payment'
            case _:
                reason = None
        user = queries.get_user(session, user_id)
        if reason is not None:
            await responses.users.SuccessBalanceEditing(query, user,
                                                        new_balance, reason)
            queries.update_balance(session, user_id, new_balance)
            number_of_orders = queries.count_user_orders(session, user.id)
            await responses.users.UserResponse(query, user, number_of_orders)


async def top_up_balance(
        query: CallbackQuery,
        callback_data: dict[str, str],
        state: FSMContext,
) -> None:
    await responses.users.NewBalanceResponse(query)
    await TopUpBalanceStates.waiting_balance.set()
    await state.update_data({'callback_data': callback_data})


async def enter_balance(
        message: Message,
        state: FSMContext,
) -> None:
    if message.text.replace('.', '').isdigit():
        callback_data = (await state.get_data())['callback_data']
        with database.create_session() as session:
            user = queries.get_user(session, callback_data['user_id'])
            await responses.users.TopUpBalanceAlertResponse(
                message, user, message.text, callback_data
            )
            await state.finish()
    else:
        await responses.users.IncorrectBalanceResponse(message)


async def balance_refill_method(
        query: CallbackQuery,
        callback_data: dict[str, str],
) -> None:
    if callback_data['is_confirmed'] == 'yes':
        await responses.users.BalanceRefillMethodResponse(query, callback_data)
    else:
        with database.create_session() as session:
            user_id = int(callback_data['user_id'])
            user = queries.get_user(session, user_id)
            await responses.users.UserResponse(
                query, user, queries.count_user_orders(session, user_id)
            )


async def top_up_balance_cb(
        query: CallbackQuery,
        callback_data: dict[str, str],
) -> None:
    with database.create_session() as session:
        balance_delta = decimal.Decimal(callback_data['balance_delta'])
        user_id = int(callback_data['user_id'])
        reason = callback_data['payment_method'].capitalize()
        queries.top_up_balance(session, user_id, balance_delta)
        user = queries.get_user(session, user_id)
        await responses.users.SuccessBalanceRefillResponse(query, user,
                                                           float(balance_delta),
                                                           reason)
        number_of_orders = queries.count_user_orders(session, user.id)
        await responses.users.UserResponse(query, user, number_of_orders)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        ban_user,
        UserCallbackFactory().filter(action='ban', is_confirmed=''),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        ban_user_confirm,
        UserCallbackFactory().filter(action='ban'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        unban_user,
        UserCallbackFactory().filter(action='unban', is_confirmed=''),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        unban_user_confirm,
        UserCallbackFactory().filter(action='unban'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        edit_balance,
        EditUserBalanceCallbackFactory().filter(is_confirmed=''),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_message_handler(
        enter_new_balance,
        AdminFilter(),
        state=EditBalanceStates.waiting_balance,
    )
    dispatcher.register_callback_query_handler(
        balance_editing_reason,
        EditUserBalanceCallbackFactory().filter(reason=''),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        edit_balance_cb,
        EditUserBalanceCallbackFactory().filter(),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        top_up_balance,
        TopUpUserBalanceCallbackFactory().filter(is_confirmed=''),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_message_handler(
        enter_balance,
        AdminFilter(),
        state=TopUpBalanceStates.waiting_balance,
    )
    dispatcher.register_callback_query_handler(
        balance_refill_method,
        TopUpUserBalanceCallbackFactory().filter(payment_method=''),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        top_up_balance_cb,
        TopUpUserBalanceCallbackFactory().filter(),
        AdminFilter(),
        state='*',
    )
