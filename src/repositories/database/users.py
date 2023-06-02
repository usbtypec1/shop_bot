from sqlalchemy import select

import exceptions
import models
from database.schemas import User
from repositories.database.base import BaseRepository

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

    def create(
            self,
            *,
            telegram_id: int,
            username: str | None = None,
    ) -> models.User:
        user = User(telegram_id=telegram_id, username=username)
        with self._session_factory() as session:
            with session.begin():
                session.merge(user)
        return models.User(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            balance=user.balance,
            is_banned=user.is_banned,
        )
