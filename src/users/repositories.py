from sqlalchemy import select, func, delete, update

from common.repositories import BaseRepository
from database.schemas import User
from users import models as users_models

__all__ = ('UserRepository',)

from users.exceptions import UserNotInDatabase


class UserRepository(BaseRepository):

    def get_by_id(self, user_id: int) -> users_models.User:
        with self._session_factory() as session:
            result = session.get(User, user_id)
        if result is None:
            raise UserNotInDatabase
        return users_models.User(
            id=result.id,
            telegram_id=result.telegram_id,
            username=result.username,
            balance=result.balance,
            is_banned=result.is_banned,
            created_at=result.created_at,
        )

    def get_by_telegram_id(self, telegram_id: int) -> users_models.User:
        statement = select(User).where(User.telegram_id == telegram_id)
        with self._session_factory() as session:
            result = session.scalar(statement)
        if result is None:
            raise UserNotInDatabase
        return users_models.User(
            id=result.id,
            telegram_id=result.telegram_id,
            username=result.username,
            balance=result.balance,
            is_banned=result.is_banned,
            created_at=result.created_at,
        )

    def create(
            self,
            *,
            telegram_id: int,
            username: str | None = None,
    ) -> users_models.User:
        user = User(telegram_id=telegram_id, username=username)
        with self._session_factory() as session:
            with session.begin():
                session.merge(user)
        return users_models.User(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            balance=user.balance,
            is_banned=user.is_banned,
            created_at=user.created_at,
        )

    def delete_by_id(self, user_id: int) -> bool:
        statement = delete(User).where(User.id == user_id)
        with self._session_factory() as session:
            with session.begin():
                result = session.execute(statement)
        return bool(result.rowcount)

    def get_total_balance(self) -> float:
        statement = select(func.sum(User.balance))
        with self._session_factory() as session:
            result = session.execute(statement).first()
        return result[0]

    def get_total_count(self) -> int:
        statement = select(func.count(User.id))
        with self._session_factory() as session:
            result = session.execute(statement).first()
        return result[0]

    def ban_by_id(self, user_id: int) -> bool:
        statement = (
            update(User)
            .where(User.id == user_id)
            .values(is_banned=True)
        )
        with self._session_factory() as session:
            with session.begin():
                result = session.execute(statement)
        return bool(result.rowcount)

    def unban_by_id(self, user_id: int) -> bool:
        statement = (
            update(User)
            .where(User.id == user_id)
            .values(is_banned=False)
        )
        with self._session_factory() as session:
            with session.begin():
                result = session.execute(statement)
        return bool(result.rowcount)