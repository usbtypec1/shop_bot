from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import (
    BaseMiddleware,
    LifetimeControllerMiddleware,
)
from aiogram.types import Update

import database
from database import queries

__all__ = ('BannedUserMiddleware', 'DependencyInjectMiddleware')


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


class DependencyInjectMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self, **kwargs):
        super().__init__()
        self.__kwargs = kwargs

    async def pre_process(self, obj, data, *args):
        for key, value in self.__kwargs.items():
            data[key] = value
