from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ChatType

from common.filters import AdminFilter
from common.views import edit_message_by_view
from top_up_bonuses.callback_data import TopUpBonusDetailCallbackData
from top_up_bonuses.repositories import TopUpBonusRepository
from top_up_bonuses.views import TopUpBonusDetailView

__all__ = ('register_handlers',)


async def on_show_top_up_bonus_detail(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
        top_up_bonus_repository: TopUpBonusRepository,
) -> None:
    await state.finish()
    top_up_bonus_id: int = callback_data['top_up_bonus_id']
    top_up_bonus = top_up_bonus_repository.get_by_id(top_up_bonus_id)
    view = TopUpBonusDetailView(top_up_bonus)
    await edit_message_by_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_show_top_up_bonus_detail,
        AdminFilter(),
        TopUpBonusDetailCallbackData().filter(),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
