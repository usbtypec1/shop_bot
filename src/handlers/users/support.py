import aiogram.types
from aiogram import dispatcher
from aiogram.dispatcher import filters

import exceptions
import responses.support
from filters import is_admin
from keyboards.inline import callback_factories
from loader import dp
from services import db_api, notifications
from services.db_api import queries
from states import support_states


@dp.message_handler(filters.Text('👨‍💻 Support'), ~is_admin.IsUserAdmin())
async def support(message: aiogram.types.Message):
    with db_api.create_session() as session:
        if not queries.check_is_user_exists(session, message.from_user.id):
            raise exceptions.UserNotInDatabase
    await responses.support.UserSupportMenuResponse(message)


@dp.message_handler(filters.Text('📋 New Support Request'), ~is_admin.IsUserAdmin())
async def new_support_request(message: aiogram.types.Message):
    with db_api.create_session() as session:
        if not queries.check_is_user_exists(session, message.from_user.id):
            raise exceptions.UserNotInDatabase
        subjects = queries.get_all_support_subjects(session)
        await responses.support.NewSupportRequestResponse(message, subjects)


@dp.callback_query_handler(callback_factories.CreateSupportCallbackFactory().filter())
async def new_support_request(query: aiogram.types.CallbackQuery, callback_data: dict[str: str]):
    with db_api.create_session() as session:
        if not queries.check_is_user_exists(session, query.from_user.id):
            raise exceptions.UserNotInDatabase
    await responses.support.NewSupportRequestIssueResponse(query)
    await support_states.AddSupportRequest.waiting_issue.set()
    await dp.current_state().update_data({'subject_id': callback_data['subject_id']})


@dp.message_handler(state=support_states.AddSupportRequest.waiting_issue)
async def new_support_request(message: aiogram.types.Message, state: dispatcher.FSMContext):
    subject_id = int((await state.get_data())['subject_id'])
    await state.finish()
    with db_api.create_session() as session:
        if not queries.check_is_user_exists(session, message.from_user.id):
            raise exceptions.UserNotInDatabase
        request = queries.add_support_request(
            session, message.from_user.id, message.from_user.username, subject_id, message.text
        )
        await responses.support.SuccessAddingSupportRequestResponse(
            message, queries.count_open_support_requests(session)
        )
        await notifications.NewSupportRequestNotification(request).send()


@dp.message_handler(filters.Text('🆘 New Support Subject'))
async def new_support_subject(message: aiogram.types.Message):
    with db_api.create_session() as session:
        if not queries.check_is_user_exists(session, message.from_user.id):
            raise exceptions.UserNotInDatabase
    await responses.support.NewSupportSubjectResponse(message)
    await support_states.AddSupportSubject.waiting_subject.set()


@dp.message_handler(state=support_states.AddSupportSubject.waiting_subject)
async def new_support_subject(message: aiogram.types.Message, state: dispatcher.FSMContext):
    await state.finish()
    with db_api.create_session() as session:
        if not queries.check_is_user_exists(session, message.from_user.id):
            raise exceptions.UserNotInDatabase
        queries.add_support_subject(session, message.text)
    await responses.support.SuccessAddingSupportSubjectResponse(message)


@dp.message_handler(filters.Text('📓 My Support Requests'), ~is_admin.IsUserAdmin(), chat_type='private')
async def support_requests(message: aiogram.types.Message):
    with db_api.create_session() as session:
        if not queries.check_is_user_exists(session, message.from_user.id):
            raise exceptions.UserNotInDatabase
        requests = queries.get_user_support_requests(session, message.from_user.id)
        await responses.support.UserSupportRequestsResponse(message, requests)


@dp.callback_query_handler(
    callback_factories.SupportCallbackFactory().filter(is_open='', request_id='', action=''), chat_type='private'
)
async def support_requests(query: aiogram.types.CallbackQuery):
    with db_api.create_session() as session:
        if not queries.check_is_user_exists(session, query.from_user.id):
            raise exceptions.UserNotInDatabase
        requests = queries.get_user_support_requests(session, query.from_user.id)
        await responses.support.UserSupportRequestsResponse(query, requests)


@dp.callback_query_handler(
    callback_factories.SupportCallbackFactory().filter(is_open='', action=''), chat_type='private'
)
async def support_request_menu(query: aiogram.types.CallbackQuery, callback_data: dict[str: str]):
    with db_api.create_session() as session:
        if not queries.check_is_user_exists(session, query.from_user.id):
            raise exceptions.UserNotInDatabase
        request = queries.get_support_request(session, int(callback_data['request_id']))
        await responses.support.SupportRequestResponse(query, request, user_id=query.from_user.id)
