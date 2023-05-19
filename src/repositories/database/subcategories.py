import structlog
from sqlalchemy import select
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
                max_displayed_stocks_count=(
                    subcategory.max_displayed_stocks_count
                ),
                is_hidden=subcategory.is_hidden,
                can_be_seen=subcategory.can_be_seen,
                category_id=category_id,
            ) for subcategory in result
        ]
