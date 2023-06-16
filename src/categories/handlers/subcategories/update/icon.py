from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message
from emoji import is_emoji

from categories.callback_data import SubcategoryUpdateCallbackData
from categories.repositories import CategoryRepository
from categories.states import SubcategoryUpdateStates
from categories.views import SubcategoryDetailView
from common.views import answer_view
from loader import dp


@dp.callback_query_handler(
    SubcategoryUpdateCallbackData().filter(field='icon'),
    state='*',
)
async def on_start_subcategory_icon_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext
):
    subcategory_id: int = callback_data['subcategory_id']
    await SubcategoryUpdateStates.icon.set()
    await state.update_data(subcategory_id=subcategory_id)
    await callback_query.message.edit_text(
        'Provide new icon (Enter any A-Z text to delete)'
    )


@dp.message_handler(
    content_types=ContentType.TEXT,
    state=SubcategoryUpdateStates.icon,
)
async def on_subcategory_icon_input(
        message: Message,
        state: FSMContext,
        category_repository: CategoryRepository,
):
    state_data = await state.get_data()
    await state.finish()

    subcategory_id: int = state_data['subcategory_id']
    category_icon = message.text if is_emoji(message.text) else None

    category_repository.update_icon(
        category_id=subcategory_id,
        category_icon=category_icon,
    )
    subcategory = category_repository.get_by_id(subcategory_id)

    view = SubcategoryDetailView(subcategory)
    await answer_view(message=message, view=view)
