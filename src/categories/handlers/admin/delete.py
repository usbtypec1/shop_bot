from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery

from categories.repositories import CategoryRepository
from categories.states import CategoryDeleteStates
from categories.views import CategoryAskDeleteConfirmationView
from common.filters import AdminFilter
from common.views import edit_message_by_view
from database.session import session_factory
from categories.callback_data import CategoryDeleteCallbackData

__all__ = ('register_handlers',)


async def on_ask_delete_category_confirmation(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext
) -> None:
    category_id: int = callback_data['category_id']
    await CategoryDeleteStates.confirm.set()
    await state.update_data(category_id=category_id)
    view = CategoryAskDeleteConfirmationView(category_id)
    await edit_message_by_view(message=callback_query.message, view=view)


async def on_delete_category_confirm(
        callback_query: CallbackQuery,
        state: FSMContext,
) -> None:
    state_data = await state.get_data()
    category_id: int = state_data['category_id']
    await state.finish()
    category_repository = CategoryRepository(session_factory)
    category_repository.delete_by_id(category_id)
    await callback_query.message.edit_text('Category has been deleted')


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_ask_delete_category_confirmation,
        CategoryDeleteCallbackData().filter(),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        on_delete_category_confirm,
        AdminFilter(),
        Text('category-delete-confirm'),
        state=CategoryDeleteStates.confirm,
    )
