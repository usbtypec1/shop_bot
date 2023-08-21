from collections.abc import Iterable

from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import (
    LifetimeControllerMiddleware,
)
from aiogram.types import CallbackQuery, Message

__all__ = (
    'AdminIdentifierMiddleware',
    'BannedUserMiddleware',
)

from users.repositories import UserRepository


class AdminIdentifierMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ("error", "update",)

    def __init__(self, admin_telegram_ids: Iterable[int]):
        super().__init__()
        self.__admin_telegram_ids = set(admin_telegram_ids)

    async def pre_process(self, obj: Message | CallbackQuery, data, *args):
        data['is_admin'] = obj.from_user.id in self.__admin_telegram_ids


class BannedUserMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ('update', 'error')

    def __init__(self, user_repository: UserRepository):
        super().__init__()
        self.__user_repository = user_repository

    async def pre_process(self, obj: Message | CallbackQuery, data, *args):
        user = self.__user_repository.get_by_telegram_id(obj.from_user.id)
        if user.is_banned:
            raise CancelHandler
        data['user'] = user
