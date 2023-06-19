from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message, CallbackQuery

import config

__all__ = ('AdminFilter',)


class AdminFilter(BoundFilter):
    async def check(
            self,
            message_or_callback_query: Message | CallbackQuery,
    ) -> bool:
        user_telegram_id = message_or_callback_query.from_user.id
        if isinstance(message_or_callback_query, (Message, CallbackQuery)):
            return user_telegram_id in config.AppSettings().admins_id
