from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, ChatType

from common.filters import AdminFilter
from common.views import edit_message_by_view
from top_up_bonuses.callback_data import TopUpBonusDeleteCallbackData
from top_up_bonuses.repositories import TopUpBonusRepository
from top_up_bonuses.states import TopUpBonusDeleteStates
from top_up_bonuses.views import (
    TopUpBonusDeleteAskForConfirmationView,
    TopUpBonusListView,
)

__all__ = ('register_handlers',)


async def on_ask_delete_top_up_bonus_confirmation(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
        top_up_bonus_repository: TopUpBonusRepository,
) -> None:
    top_up_bonus_id: int = callback_data['top_up_bonus_id']
    await TopUpBonusDeleteStates.confirm.set()
    await state.update_data(top_up_bonus_id=top_up_bonus_id)
    top_up_bonus = top_up_bonus_repository.get_by_id(top_up_bonus_id)
    view = TopUpBonusDeleteAskForConfirmationView(top_up_bonus)
    await edit_message_by_view(message=callback_query.message, view=view)


async def on_top_up_bonus_delete_confirm(
        callback_query: CallbackQuery,
        state: FSMContext,
        top_up_bonus_repository: TopUpBonusRepository,
) -> None:
    state_data = await state.get_data()
    top_up_bonus_id: int = state_data['top_up_bonus_id']
    top_up_bonus_repository.delete_by_id(top_up_bonus_id)
    top_up_bonuses = top_up_bonus_repository.get_all()
    view = TopUpBonusListView(top_up_bonuses)
    await edit_message_by_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_ask_delete_top_up_bonus_confirmation,
        AdminFilter(),
        TopUpBonusDeleteCallbackData().filter(),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        on_top_up_bonus_delete_confirm,
        AdminFilter(),
        Text('top-up-bonus-delete-confirm'),
        chat_type=ChatType.PRIVATE,
        state=TopUpBonusDeleteStates.confirm,
    )
