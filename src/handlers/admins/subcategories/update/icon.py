from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message
from emoji import is_emoji

from keyboards.inline.callback_factories import SubcategoryUpdateCallbackData
from loader import dp
from repositories.database import SubcategoryRepository
from database.session import session_factory
from states.category_states import SubcategoryUpdateStates
from views import SubcategoryDetailView, answer_view


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
):
    state_data = await state.get_data()
    await state.finish()

    subcategory_id: int = state_data['subcategory_id']
    category_icon = message.text if is_emoji(message.text) else None

    subcategory_repository = SubcategoryRepository(session_factory)

    subcategory_repository.update_icon(
        subcategory_id=subcategory_id,
        subcategory_icon=category_icon,
    )
    subcategory = subcategory_repository.get_by_id(subcategory_id)

    view = SubcategoryDetailView(subcategory)
    await answer_view(message=message, view=view)
