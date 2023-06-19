from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Update

import database
from database import queries

__all__ = ('BannedUserMiddleware',)


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
