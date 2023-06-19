from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message

from categories.repositories import CategoryRepository
from categories.states import CategoryUpdateStates
from categories.views import CategoryDetailView
from common.views import answer_view
from categories.callback_data import CategoryUpdateCallbackData

__all__ = ('register_handlers',)


async def on_start_category_name_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
):
    category_id: int = callback_data['category_id']
    await CategoryUpdateStates.name.set()
    await state.update_data(category_id=category_id)
    await callback_query.message.edit_text('Provide new title')


async def on_category_name_input(
        message: Message,
        state: FSMContext,
        category_repository: CategoryRepository,
):
    state_data = await state.get_data()
    await state.finish()

    category_id: int = state_data['category_id']
    category_name = message.text

    category_repository.update_name(
        category_id=category_id,
        category_name=category_name,
    )
    category = category_repository.get_by_id(category_id)
    subcategories = category_repository.get_subcategories(parent_id=category_id)

    view = CategoryDetailView(category=category, subcategories=subcategories)
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_start_category_name_update_flow,
        CategoryUpdateCallbackData().filter(field='name'),
        state='*',
    )
    dispatcher.register_message_handler(
        on_category_name_input,
        content_types=ContentType.TEXT,
        state=CategoryUpdateStates.name,
    )
