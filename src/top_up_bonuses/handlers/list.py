from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ChatType, ContentType

from common.filters import AdminFilter
from common.views import answer_view, edit_message_by_view
from top_up_bonuses.repositories import TopUpBonusRepository
from top_up_bonuses.views import TopUpBonusListView

__all__ = ('register_handlers',)


async def on_show_top_up_bonuses_list(
        message_or_callback_query: Message | CallbackQuery,
        state: FSMContext,
        top_up_bonus_repository: TopUpBonusRepository,
) -> None:
    await state.finish()
    top_up_bonuses = top_up_bonus_repository.get_all()
    view = TopUpBonusListView(top_up_bonuses)
    if isinstance(message_or_callback_query, Message):
        await answer_view(message=message_or_callback_query, view=view)
    else:
        await edit_message_by_view(
            message=message_or_callback_query.message,
            view=view
        )


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_top_up_bonuses_list,
        AdminFilter(),
        Text('View Active Top Up Bonuses'),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        on_show_top_up_bonuses_list,
        AdminFilter(),
        Text('show-top-up-bonuses-list'),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
