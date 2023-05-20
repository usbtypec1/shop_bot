import aiogram.types

import exceptions
import responses.support
from keyboards.inline import callback_factories
from loader import dp
from services import db_api
from services.db_api import queries


@dp.callback_query_handler(
    callback_factories.SupportCallbackFactory().filter(is_open='',
                                                       request_id='',
                                                       action=''),
    chat_type='private'
)
async def support_requests(query: aiogram.types.CallbackQuery):
    with db_api.create_session() as session:
        if not queries.check_is_user_exists(session, query.from_user.id):
            raise exceptions.UserNotInDatabase
        requests = queries.get_user_support_requests(session,
                                                     query.from_user.id)
        await responses.support.UserSupportRequestsResponse(query, requests)


@dp.callback_query_handler(
    callback_factories.SupportCallbackFactory().filter(is_open='', action=''),
    chat_type='private'
)
async def support_request_menu(query: aiogram.types.CallbackQuery,
                               callback_data: dict[str: str]):
    with db_api.create_session() as session:
        if not queries.check_is_user_exists(session, query.from_user.id):
            raise exceptions.UserNotInDatabase
        request = queries.get_support_request(session,
                                              int(callback_data['request_id']))
        await responses.support.SupportRequestResponse(query, request,
                                                       user_id=query.from_user.id)
