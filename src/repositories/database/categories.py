import structlog
from sqlalchemy import update, select
from structlog.contextvars import bound_contextvars

import models
from repositories.database.base import BaseRepository
from services.db_api.schemas import Category

__all__ = ('CategoryRepository',)

logger = structlog.get_logger('app')


class CategoryRepository(BaseRepository):

    def get_by_id(self, category_id: int) -> models.Category:
        """
        Retrieve a category object by its ID.

        Args:
            category_id (int): The ID of the category to retrieve.

        Returns:
            models.Category: The category object matching the given ID.
        """
        with bound_contextvars(category_id=category_id):
            logger.debug('Category repository: retrieving category by ID')

            with self._session_factory() as session:
                result = session.get(Category, category_id)

            logger.debug('Category repository: retrieved category by ID')

        return models.Category(
            id=result.id,
            name=result.name,
            icon=result.icon,
            priority=result.priority,
            max_displayed_stocks_count=result.max_displayed_stocks_count,
            is_hidden=result.is_hidden,
            can_be_seen=result.can_be_seen,
        )

    def update_name(self, *, category_id, category_name: str) -> bool:
        """
        Update the name of a category with the given ID.

        Args:
            category_id: The ID of the category to update.
            category_name: The new name for the category.

        Returns:
            True if the category name was successfully updated, False otherwise.
        """
        statement = (
            update(Category)
            .where(Category.id == category_id)
            .values(name=category_name)
        )
        with self._session_factory() as session:
            with session.begin():
                result = session.execute(statement)
        is_updated = bool(result.rowcount)

        with bound_contextvars(
                category_id=category_id,
                category_name=category_name,
        ):
            if is_updated:
                logger.debug('Category repository: name successfully updated')
            else:
                logger.debug('Category repository: could not update name')
        return is_updated
