from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message

from categories.callback_data import SubcategoryUpdateCallbackData
from categories.repositories import CategoryRepository
from categories.states import SubcategoryUpdateStates
from categories.views import SubcategoryDetailView
from common.views import answer_view
from loader import dp


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
        category_repository: CategoryRepository,
):
    if not message.text.isdigit():
        await message.answer('Max displayed stock must be a number')
        return

    state_data = await state.get_data()
    await state.finish()

    subcategory_id: int = state_data['subcategory_id']
    max_displayed_stock_count = int(message.text)

    category_repository.update_max_displayed_stock_count(
        category_id=subcategory_id,
        max_displayed_stock_count=max_displayed_stock_count,
    )
    category = category_repository.get_by_id(subcategory_id)

    view = SubcategoryDetailView(category)
    await answer_view(message=message, view=view)
