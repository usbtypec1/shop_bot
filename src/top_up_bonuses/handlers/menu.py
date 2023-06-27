from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ContentType, ChatType

from common.filters import AdminFilter
from common.views import answer_view
from top_up_bonuses.views import TopUpBonusMenuView

__all__ = ('register_handlers',)


async def on_show_top_up_bonus_menu(
        message: Message,
        state: FSMContext,
) -> None:
    await state.finish()
    view = TopUpBonusMenuView()
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_top_up_bonus_menu,
        AdminFilter(),
        Text('Top Up Bonuses'),
        chat_type=ChatType.PRIVATE,
        content_types=ContentType.TEXT,
        state='*',
    )
