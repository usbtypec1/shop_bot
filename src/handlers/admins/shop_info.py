from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ContentType

import models
from filters.is_admin import IsUserAdmin
from keyboards.inline.callback_factories import ShopInfoUpdateCallbackData
from loader import dp
from repositories.database import ShopInfoRepository
from database.session import session_factory
from states.shop_info_states import ShopInfoUpdateStates
from views import ShopInfoMenuView, answer_view, ShopInfoDetailView


@dp.message_handler(
    Text('🏪 Shop Information'),
    IsUserAdmin(),
    state='*',
)
async def on_show_shop_info_menu(message: Message) -> None:
    view = ShopInfoMenuView()
    await answer_view(message=message, view=view)


@dp.message_handler(
    Text(equals=[i.value for i in models.ShopInfo]),
    IsUserAdmin(),
    state='*',
)
async def on_show_shop_info_detail(message: Message) -> None:
    shop_info = models.ShopInfo(message.text)
    shop_info_repository = ShopInfoRepository(session_factory)
    value = shop_info_repository.get_value_or_none(key=shop_info.name)
    value = value or message.text
    view = ShopInfoDetailView(key=shop_info.name, value=value)
    await answer_view(message=message, view=view)


@dp.callback_query_handler(
    ShopInfoUpdateCallbackData().filter(),
    state='*',
)
async def on_start_shop_info_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    key: str = callback_data['key']
    await ShopInfoUpdateStates.value.set()
    await state.update_data(key=key)
    await callback_query.message.edit_text('📝 Enter new value')


@dp.message_handler(
    content_types=ContentType.TEXT,
    state=ShopInfoUpdateStates.value,
)
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
