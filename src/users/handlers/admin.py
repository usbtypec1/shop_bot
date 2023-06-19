import decimal

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, Update, CallbackQuery

import database
import responses.users
from common.filters import AdminFilter
from common.views import answer_view
from database import queries, session_factory
from keyboards.inline import common_keybords
from keyboards.inline.callback_factories import (
    UserCallbackFactory,
    EditUserBalanceCallbackFactory,
    TopUpUserBalanceCallbackFactory,
)
from users.exceptions import UserNotInDatabase
from users.repositories import UserRepository
from users.states import (
    SearchUsersStates,
    EditBalanceStates,
    TopUpBalanceStates,
)
from users.views import UsersView


async def user_not_in_db_error(
        update: Update,
        _: UserNotInDatabase,
) -> bool:
    text = "❌ You aren't in the database! Enter /start to register"
    if update.callback_query is not None:
        await update.callback_query.message.answer(text)
    elif update.message is not None:
        await update.message.answer(text)
    return True


async def on_show_users_menu(message: Message) -> None:
    user_repository = UserRepository(session_factory)
    with database.create_session() as session:
        total_balance = user_repository.get_total_balance()
        page_size = 10
        view = UsersView(
            users=queries.get_users(session, page_size + 1),
            total_balance=float(total_balance),
            page_size=page_size,
        )
        await answer_view(message=message, view=view)


async def users(query: CallbackQuery, callback_data: dict) -> None:
    user_repository = UserRepository(session_factory)
    total_balance = user_repository.get_total_balance()
    with database.create_session() as session:
        page, page_size = int(callback_data['page']), 10
        view = UsersView(
            users=queries.get_users(session, page_size + 1, page * page_size),
            total_balance=float(total_balance),
            page_size=page_size,
            page=page,
        )
        await answer_view(message=query.message, view=view)


async def search_users(query: CallbackQuery) -> None:
    await responses.users.SearchUserResponse(query)
    await SearchUsersStates.waiting_identifiers.set()


async def search_users_ids_input(
        message: Message,
        state: FSMContext,
):
    await state.finish()
    usernames, ids = [], []
    page, page_size = 0, 10
    total_balance = decimal.Decimal('0')
    for identifier in message.text.split():
        if identifier.isdigit():
            ids.append(int(identifier))
        else:
            usernames.append(identifier.lower())
    with database.create_session() as session:
        user_list = queries.get_users(session, page_size + 1, page_size * page,
                                      usernames, ids)
        for user in user_list:
            total_balance += decimal.Decimal(str(user.balance))
        filter_message = await responses.users.FoundUsersResponse(message)
        view = UsersView(
            users=user_list,
            total_balance=float(total_balance),
            users_filter=filter_message.message_id,
            page=page,
            page_size=page_size,
        )
        await answer_view(message=message, view=view)


async def users_show(query: CallbackQuery, callback_data: dict) -> None:
    usernames, ids = [], []
    page, page_size = int(callback_data['page']), 10
    total_balance = decimal.Decimal('0')
    filter_message = await bot.edit_message_reply_markup(
        query.message.chat.id, int(callback_data['filter']),
        reply_markup=common_keybords.MockKeyboard()
    )
    await filter_message.delete_reply_markup()
    for identifier in filter_message.text.split(': ', 1)[-1].split():
        if identifier.isdigit():
            ids.append(int(identifier))
        else:
            usernames.append(identifier.lower())
    with database.create_session() as session:
        user_list = queries.get_users(session, page_size + 1, page_size * page,
                                      usernames, ids)
        for user in user_list:
            total_balance += decimal.Decimal(str(user.balance))
        view = UsersView(
            users=user_list,
            total_balance=float(total_balance),
            users_filter=query.message.message_id,
            page=page,
            page_size=page_size,
        )
        await answer_view(message=query.message, view=view)


async def user_menu(
        query: CallbackQuery,
        callback_data: dict[str: str],
) -> None:
    with database.create_session() as session:
        user = queries.get_user(session, int(callback_data['id']))
        number_of_orders = queries.count_user_orders(session, user.id)
        await responses.users.UserResponse(query, user, number_of_orders,
                                           callback_data)


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


async def delete_user(
        query: CallbackQuery,
        callback_data: dict[str: str],
) -> None:
    with database.create_session() as session:
        user = queries.get_user(session, int(callback_data['id']))
        await responses.users.DeleteUserAlert(query, user, callback_data)


async def delete_user_confirm(
        query: CallbackQuery,
        callback_data: dict[str, str],
        user_repository: UserRepository,
) -> None:
    with database.create_session() as session:
        user_id = int(callback_data['id'])
        user = queries.get_user(session, user_id)
        if callback_data['is_confirmed'] == 'yes':
            user_repository.delete_by_id(user_id)
            total_balance = user_repository.get_total_balance()
            page, page_size = int(callback_data['page']), 10
            await responses.users.SuccessUserRemovalResponse(query, user)
            view = UsersView(
                users=queries.get_users(session, page_size + 1,
                                        page * page_size),
                total_balance=total_balance,
                page=page,
                page_size=page_size,
            )
            await answer_view(message=query.message, view=view)
        else:
            number_of_orders = queries.count_user_orders(session, user.id)
            await responses.users.UserResponse(query, user, number_of_orders,
                                               callback_data)


async def edit_balance(
        query: CallbackQuery,
        callback_data: dict[str, str],
) -> None:
    await responses.users.NewBalanceResponse(query)
    await EditBalanceStates.waiting_balance.set()
    await dp.current_state().update_data({'callback_data': callback_data})


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
) -> None:
    await responses.users.NewBalanceResponse(query)
    await TopUpBalanceStates.waiting_balance.set()
    await dp.current_state().update_data({'callback_data': callback_data})


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
    dispatcher.register_errors_handler(
        user_not_in_db_error,
        exception=UserNotInDatabase,
    )
    dispatcher.register_message_handler(
        on_show_users_menu,
        Text('🙍‍♂ Users'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        users,
        UserCallbackFactory().filter(filter='', id='', action=''),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        search_users,
        UserCallbackFactory().filter(id='', action='search'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_message_handler(
        search_users_ids_input,
        AdminFilter(),
        state=SearchUsersStates.waiting_identifiers,
    )
    dispatcher.register_callback_query_handler(
        users_show,
        UserCallbackFactory().filter(id='', action=''),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        user_menu,
        UserCallbackFactory().filter(action='manage'),
        AdminFilter(),
        state='*',
    )
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
        delete_user,
        UserCallbackFactory().filter(action='delete', is_confirmed=''),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        delete_user_confirm,
        UserCallbackFactory().filter(action='delete'),
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
