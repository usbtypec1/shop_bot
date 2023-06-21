from collections.abc import Iterable

from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import (
    BaseMiddleware,
    LifetimeControllerMiddleware,
)
from aiogram.types import Update, CallbackQuery, Message

import database
from database import queries

__all__ = (
    'AdminIdentifierMiddleware',
    'BannedUserMiddleware',
)


class AdminIdentifierMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ("error", "update",)

    def __init__(self, admin_telegram_ids: Iterable[int]):
        super().__init__()
        self.__admin_telegram_ids = set(admin_telegram_ids)

    async def pre_process(self, obj: Message | CallbackQuery, data, *args):
        data['is_admin'] = obj.from_user.id in self.__admin_telegram_ids


class BannedUserMiddleware(BaseMiddleware):
    @staticmethod
    async def on_pre_process_update(update: Update, *args, **kwargs):
        user_id = None
        if update.message:
            user_id = update.message.from_user.id
        elif update.callback_query:
            user_id = update.callback_query.from_user.id
        if user_id is not None:
            with database.create_session() as session:
                if queries.check_is_user_banned(session, user_id):
                    raise CancelHandler()
