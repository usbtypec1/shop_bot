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
            max_displayed_stock_count=result.max_displayed_stock_count,
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

    def update_icon(
            self,
            *,
            category_id,
            category_icon: str | None = None,
    ) -> bool:
        """
        Update the icon of a category with the given ID.

        Args:
            category_id: The ID of the category to update.
            category_icon: The new icon for the category.

        Returns:
            True if the category icon was successfully updated, False otherwise.
        """
        statement = (
            update(Category)
            .where(Category.id == category_id)
            .values(icon=category_icon)
        )
        with self._session_factory() as session:
            with session.begin():
                result = session.execute(statement)
        is_updated = bool(result.rowcount)

        with bound_contextvars(
                category_id=category_id,
                category_icon=category_icon,
        ):
            if is_updated:
                logger.debug('Category repository: icon successfully updated')
            else:
                logger.debug('Category repository: could not update icon')
        return is_updated

    def update_max_displayed_stock_count(
            self,
            *,
            category_id,
            max_displayed_stock_count: int,
    ) -> bool:
        """
        Update the icon of a category with the given ID.

        Args:
            category_id: The ID of the category to update.
            max_displayed_stock_count: Max displayed stock count for
                                                the category.

        Returns:
            True if the category icon was successfully updated, False otherwise.
        """
        statement = (
            update(Category)
            .where(Category.id == category_id)
            .values(max_displayed_stock_count=max_displayed_stock_count)
        )
        with self._session_factory() as session:
            with session.begin():
                result = session.execute(statement)
        is_updated = bool(result.rowcount)

        with bound_contextvars(
                category_id=category_id,
                max_displayed_stock_count=max_displayed_stock_count,
        ):
            if is_updated:
                logger.debug(
                    'Category repository:'
                    ' max displayed stock count successfully updated'
                )
            else:
                logger.debug(
                    'Category repository:'
                    ' could not update max_displayed_stock_count'
                )
        return is_updated
