import structlog
from sqlalchemy import select, update, exists
from sqlalchemy.orm import Session
from structlog.contextvars import bound_contextvars

import models
from repositories.database.base import BaseRepository
from services.db_api.schemas import Subcategory

__all__ = ('SubcategoryRepository',)

logger = structlog.get_logger('app')


class SubcategoryRepository(BaseRepository):

    def get_by_category_id(self, category_id: int) -> list[models.Subcategory]:
        """
        Retrieve a category object by its ID.

        Args:
            category_id (int): The ID of the category to retrieve.

        Returns:
            models.Category: The category object matching the given ID.
        """
        with bound_contextvars(category_id=category_id):
            logger.debug(
                'Subcategory repository: retrieved subcategory by category ID'
            )

            statement = (
                select(Subcategory)
                .where(Subcategory.category_id == category_id)
                .order_by(Subcategory.priority.asc())
            )
            with self._session_factory() as session:
                result = session.scalars(statement).fetchall()

            logger.debug(
                'Subcategory repository: retrieved subcategory by category ID'
            )

        return [
            models.Subcategory(
                id=subcategory.id,
                name=subcategory.name,
                icon=subcategory.icon,
                priority=subcategory.priority,
                max_displayed_stock_count=subcategory.max_displayed_stock_count,
                is_hidden=subcategory.is_hidden,
                can_be_seen=subcategory.can_be_seen,
                category_id=category_id,
            ) for subcategory in result
        ]

    def __shift_subcategory_priorities(
            self,
            *,
            session: Session,
            priority: int,
    ) -> None:
        statement = (
            update(Subcategory)
            .where(Subcategory.priority >= priority)
            .values(priority=Subcategory.priority + 1)
        )
        session.execute(statement)

    def create(
            self,
            *,
            name: str,
            priority: int,
            category_id: int,
            max_displayed_stocks_count: int,
            is_hidden: bool,
            can_be_seen: bool,
            icon: str | None = None,
    ) -> models.Subcategory:
        subcategory = Subcategory(
            name=name,
            icon=icon,
            priority=priority,
            is_hidden=is_hidden,
            can_be_seen=can_be_seen,
            category_id=category_id,
            max_displayed_stock_count=max_displayed_stocks_count,
        )
        statement = select(exists().where(Subcategory.priority == priority))
        with self._session_factory() as session:
            with session.begin():
                is_same_priority_subcategory_exists = session.scalar(statement)
                if is_same_priority_subcategory_exists:
                    self.__shift_subcategory_priorities(
                        session=session,
                        priority=priority,
                    )
                session.add(subcategory)
                session.flush()
                session.refresh(subcategory)
        return models.Subcategory(
            id=subcategory.id,
            name=subcategory.name,
            icon=subcategory.icon,
            priority=subcategory.priority,
            is_hidden=subcategory.is_hidden,
            can_be_seen=subcategory.can_be_seen,
            category_id=subcategory.category_id,
            max_displayed_stock_count=subcategory.max_displayed_stocks_count,
        )
