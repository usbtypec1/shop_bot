from decimal import Decimal

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

    def calculate_total_cost_by_user_id(self, user_id: int) -> Decimal:
        statement = (
            select(func.sum(Sale.amount * Sale.quantity))
            .where(Sale.user_id == user_id)
        )
        with self._session_factory() as session:
            row = session.execute(statement).first()
        return row[0] if row is not None else Decimal('0')

    def calculate_total_cost(self) -> Decimal:
        statement = select(func.sum(Sale.amount * Sale.quantity))
        with self._session_factory() as session:
            row = session.execute(statement).first()
        return row[0] if row is not None else Decimal('0')

    def count_all(self) -> int:
        statement = select(func.count())
        with self._session_factory() as session:
            row = session.execute(statement).first()
        return row[0] if row is not None else 0
