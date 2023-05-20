from sqlalchemy import select

import exceptions
import models
from repositories.database.base import BaseRepository
from services.db_api.schemas import User

__all__ = ('UserRepository',)


class UserRepository(BaseRepository):

    def get_by_telegram_id(self, telegram: int) -> models.User:
        statement = select(User).where(User.telegram_id == telegram)
        with self._session_factory() as session:
            result = session.scalar(statement)
        if result is None:
            raise exceptions.UserNotInDatabase
        return models.User(
            id=result.id,
            telegram_id=result.telegram_id,
            username=result.username,
            balance=result.balance,
            is_banned=result.is_banned,
        )
