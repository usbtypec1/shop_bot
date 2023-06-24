from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

import database
import responses.users
from common.filters import AdminFilter
from database import queries
from keyboards.inline.callback_factories import EditUserBalanceCallbackFactory
from users.states import EditBalanceStates


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


def register_handlers(dispatcher: Dispatcher) -> None:
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
