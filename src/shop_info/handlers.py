import structlog
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ContentType

from common.filters import AdminFilter
from common.views import answer_view
from database.session import session_factory
from keyboards.inline.callback_factories import ShopInfoUpdateCallbackData
from shop_info.models import ShopInfo
from shop_info.repositories import ShopInfoRepository
from shop_info.states import ShopInfoUpdateStates
from shop_info.views import (
    ShopInfoMenuView,
    ShopInfoDetailView,
    ShopManagementView,
)

logger = structlog.get_logger('app')


async def shop_management(message: Message):
    await answer_view(message=message, view=ShopManagementView())


async def on_show_shop_info_menu(message: Message) -> None:
    await answer_view(message=message, view=ShopInfoMenuView())


async def on_show_shop_info_detail(
        message: Message,
        is_admin: bool,
) -> None:
    shop_info = ShopInfo(message.text)
    shop_info_repository = ShopInfoRepository(session_factory)
    value = shop_info_repository.get_value_or_none(key=shop_info.name)
    value = value or message.text
    if is_admin:
        view = ShopInfoDetailView(key=shop_info.name, value=value)
        await answer_view(message=message, view=view)
    else:
        await message.answer(value)


async def on_start_shop_info_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    key: str = callback_data['key']
    await ShopInfoUpdateStates.value.set()
    await state.update_data(key=key)
    await callback_query.message.edit_text('📝 Enter new value')


async def on_shop_info_value_input(
        message: Message,
        state: FSMContext,
) -> None:
    state_data = await state.get_data()
    await state.finish()
    key = state_data['key']
    shop_info_repository = ShopInfoRepository(session_factory)
    shop_info_repository.upsert(key=key, value=message.html_text)
    view = ShopInfoDetailView(key=key, value=message.html_text)
    await message.answer('✅ Shop information has been updated')
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        shop_management,
        Text('🗂 Mng Categories & Prod'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_message_handler(
        on_show_shop_info_menu,
        Text('🏪 Shop Information'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_message_handler(
        on_show_shop_info_detail,
        Text(equals=[i.value for i in ShopInfo]),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        on_start_shop_info_update_flow,
        ShopInfoUpdateCallbackData().filter(),
        state='*',
    )
    dispatcher.register_message_handler(
        on_shop_info_value_input,
        content_types=ContentType.TEXT,
        state=ShopInfoUpdateStates.value,
    )
    logger.debug('Registered shop info handlers')
