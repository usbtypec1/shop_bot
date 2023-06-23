from sqlalchemy import select, func

from common.repositories import BaseRepository
from database.schemas import User, Sale

__all__ = ('SaleRepository',)


class SaleRepository(BaseRepository):

    def count_by_user_telegram_id(self, user_telegram_id: int) -> int:
        statement = (
            select(func.count())
            .join(User, Sale.user_id == User.id)
            .where(User.telegram_id == user_telegram_id)
        )
        with self._session_factory() as session:
            row = session.execute(statement).first()

        return row[0] if row is not None else 0
