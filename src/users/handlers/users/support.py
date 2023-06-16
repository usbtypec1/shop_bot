from aiogram import Dispatcher
from aiogram.types import ChatType, CallbackQuery

import database
import responses.support
from database import queries
from keyboards.inline.callback_factories import SupportCallbackFactory
from users.exceptions import UserNotInDatabase


async def support_requests(query: CallbackQuery):
    with database.create_session() as session:
        if not queries.check_is_user_exists(session, query.from_user.id):
            raise UserNotInDatabase
        requests = queries.get_user_support_requests(
            session,
            query.from_user.id,
        )
        await responses.support.UserSupportRequestsResponse(query, requests)


async def support_request_menu(
        query: CallbackQuery,
        callback_data: dict[str: str],
) -> None:
    with database.create_session() as session:
        if not queries.check_is_user_exists(session, query.from_user.id):
            raise UserNotInDatabase
        request = queries.get_support_request(
            session,
            int(callback_data['request_id']),
        )
        await responses.support.SupportRequestResponse(
            query,
            request,
            user_id=query.from_user.id,
        )


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        support_requests,
        SupportCallbackFactory().filter(is_open='', request_id='', action=''),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        support_request_menu,
        SupportCallbackFactory().filter(is_open='', action=''),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
