from collections.abc import Iterable
from decimal import Decimal

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

    def get_total_balance(self) -> Decimal:
        statement = select(func.sum(User.balance))
        with self._session_factory() as session:
            row = session.execute(statement).first()
        return Decimal('0') if row is None else row[0]

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

    def is_banned(self, telegram_id: int) -> bool:
        statement = (
            select(User.is_banned)
            .where(User.telegram_id == telegram_id)
        )
        with self._session_factory() as session:
            row = session.execute(statement).first()

        return row is not None and row[0]

    def get_by_usernames_and_ids(
            self,
            *,
            usernames: Iterable[str] | None = None,
            user_ids: Iterable[int] | None = None,
            limit: int = 100,
            offset: int = 0,
    ) -> list[users_models.User]:
        """Retrieves a list of users based on their usernames and/or user IDs.

        Args:
            usernames: A collection of usernames to filter the users.
            user_ids: A collection of user IDs to filter the users.
            limit: The maximum number of users to retrieve.
            offset: The number of users to skip before retrieving.

        Returns:
            A list of User objects matching the provided criteria.
        """
        statement = select(User).slice(offset, offset + limit)
        if usernames is not None:
            statement = statement.where(User.username.in_(usernames))
        if user_ids is not None:
            statement = statement.where(User.id.in_(user_ids))
        with self._session_factory() as session:
            users = session.scalars(statement).all()
        return [
            users_models.User(
                id=user.id,
                telegram_id=user.telegram_id,
                username=user.username,
                balance=user.balance,
                is_banned=user.is_banned,
                created_at=user.created_at,
            ) for user in users
        ]
