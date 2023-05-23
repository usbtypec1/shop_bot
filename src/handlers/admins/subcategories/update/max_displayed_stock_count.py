from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message

from keyboards.inline.callback_factories import SubcategoryUpdateCallbackData
from loader import dp
from repositories.database import SubcategoryRepository
from services.db_api.session import session_factory
from states.category_states import SubcategoryUpdateStates
from views import SubcategoryDetailView, answer_view


@dp.callback_query_handler(
    SubcategoryUpdateCallbackData().filter(field='max-displayed-stock-count'),
    state='*',
)
async def on_start_category_max_displayed_stock_count_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext
):
    subcategory_id: int = callback_data['subcategory_id']
    await SubcategoryUpdateStates.max_displayed_stocks_count.set()
    await state.update_data(subcategory_id=subcategory_id)
    await callback_query.message.edit_text('Provide max displayed stock')


@dp.message_handler(
    content_types=ContentType.TEXT,
    state=SubcategoryUpdateStates.max_displayed_stocks_count,
)
async def on_subcategory_max_displayed_stock_input(
        message: Message,
        state: FSMContext,
):
    if not message.text.isdigit():
        await message.answer('Max displayed stock must be a number')
        return

    state_data = await state.get_data()
    await state.finish()

    subcategory_id: int = state_data['subcategory_id']
    max_displayed_stock_count = int(message.text)

    subcategory_repository = SubcategoryRepository(session_factory)

    subcategory_repository.update_max_displayed_stock_count(
        subcategory_id=subcategory_id,
        max_displayed_stock_count=max_displayed_stock_count,
    )
    subcategory = subcategory_repository.get_by_id(subcategory_id)

    view = SubcategoryDetailView(subcategory)
    await answer_view(message=message, view=view)
