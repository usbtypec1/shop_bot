from sqlalchemy import select, func

from common.repositories import BaseRepository
from database.schemas import Sale

__all__ = ('SaleRepository',)


class SaleRepository(BaseRepository):

    def count_by_user_id(self, user_id: int) -> int:
        statement = select(func.count()).where(Sale.user_id == user_id)
        with self._session_factory() as session:
            row = session.execute(statement).first()

        return row[0] if row is not None else 0
