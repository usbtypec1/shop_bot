from collections.abc import Iterable
from typing import Protocol

from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import (
    LifetimeControllerMiddleware,
)
from aiogram.types import CallbackQuery, Message

__all__ = (
    'AdminIdentifierMiddleware',
    'BannedUserMiddleware',
)


class HasIsUserBannedMethod(Protocol):

    def is_banned(self, telegram_id: int) -> bool: ...


class AdminIdentifierMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ("error", "update",)

    def __init__(self, admin_telegram_ids: Iterable[int]):
        super().__init__()
        self.__admin_telegram_ids = set(admin_telegram_ids)

    async def pre_process(self, obj: Message | CallbackQuery, data, *args):
        data['is_admin'] = obj.from_user.id in self.__admin_telegram_ids


class BannedUserMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ('update', 'error')

    def __init__(self, user_repository: HasIsUserBannedMethod):
        super().__init__()
        self.__user_repository = user_repository

    async def pre_process(self, obj: Message | CallbackQuery, data, *args):
        if self.__user_repository.is_banned(obj.from_user.id):
            raise CancelHandler
