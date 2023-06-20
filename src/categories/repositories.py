import structlog
from sqlalchemy import update, select, exists, delete
from sqlalchemy.orm import Session
from structlog.contextvars import bound_contextvars

from categories import models as category_models
from common.repositories import BaseRepository
from database.schemas import Category

__all__ = ('CategoryRepository',)

logger = structlog.get_logger('app')


class CategoryRepository(BaseRepository):

    def get_categories(self) -> list[category_models.Category]:
        statement = (
            select(Category)
            .where(Category.parent_id.is_(None))
        )

        with self._session_factory() as session:
            logger.debug(
                'Category repository: retrieving categories by parent ID'
            )
            categories = session.scalars(statement).all()
            logger.debug(
                'Category repository: retrieved categories by parent ID',
                categories=categories,
            )

        return [
            category_models.Category(
                id=category.id,
                name=category.name,
                icon=category.icon,
                priority=category.priority,
                max_displayed_stock_count=category.max_displayed_stock_count,
                is_hidden=category.is_hidden,
                can_be_seen=category.can_be_seen,
                parent_id=category.parent_id,
            ) for category in categories
        ]

    def get_subcategories(
            self,
            parent_id: int,
    ) -> list[category_models.Category]:
        with bound_contextvars(parent_id=parent_id):
            statement = (
                select(Category)
                .where(Category.parent_id == parent_id)
            )

            with self._session_factory() as session:
                logger.debug(
                    'Category repository: retrieving subcategories by parent ID'
                )
                subcategories = session.scalars(statement).all()
                logger.debug(
                    'Category repository:'
                    ' retrieved subcategories by parent ID',
                    subcategories=subcategories,
                )

            return [
                category_models.Category(
                    id=category.id,
                    name=category.name,
                    icon=category.icon,
                    priority=category.priority,
                    max_displayed_stock_count=category.max_displayed_stock_count,
                    is_hidden=category.is_hidden,
                    can_be_seen=category.can_be_seen,
                    parent_id=category.parent_id,
                ) for category in subcategories
            ]

    def get_by_id(self, category_id: int) -> category_models.Category:
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

        return category_models.Category(
            id=result.id,
            name=result.name,
            icon=result.icon,
            priority=result.priority,
            max_displayed_stock_count=result.max_displayed_stock_count,
            is_hidden=result.is_hidden,
            can_be_seen=result.can_be_seen,
            parent_id=result.parent_id,
        )

    def delete_by_id(self, category_id: int) -> bool:
        statement_to_delete_category = (
            delete(Category)
            .where(Category.id == category_id)
        )
        statement_to_delete_subcategories = (
            delete(Category)
            .where(Category.id == category_id)
        )

        with (
            bound_contextvars(category_id=category_id),
            self._session_factory() as session,
            session.begin(),
        ):
            logger.debug('Category repository: deleting category')

            result = session.execute(statement_to_delete_category)
            session.execute(statement_to_delete_subcategories)

            is_deleted = bool(result.rowcount)

            if is_deleted:
                logger.debug('Category repository: deleted category')
            else:
                logger.debug('Ccategory repository: could not delete category')
        return is_deleted

    def __shift_category_priorities(
            self,
            *,
            session: Session,
            priority: int,
    ) -> None:
        statement = (
            update(Category)
            .where(Category.priority >= priority)
            .values(priority=Category.priority + 1)
        )
        session.execute(statement)

    def create(
            self,
            *,
            name: str,
            priority: int,
            max_displayed_stock_count: int,
            is_hidden: bool,
            can_be_seen: bool,
            icon: str | None = None,
            parent_id: int | None = None,
    ) -> category_models.Category:
        category = Category(
            name=name,
            icon=icon,
            priority=priority,
            is_hidden=is_hidden,
            can_be_seen=can_be_seen,
            max_displayed_stock_count=max_displayed_stock_count,
            parent_id=parent_id,
        )
        statement = (
            select(
                exists()
                .where(Category.priority == priority)
            )
        )
        with self._session_factory() as session:
            with session.begin():
                is_same_priority_category_exists = session.scalar(statement)
                if is_same_priority_category_exists:
                    self.__shift_category_priorities(
                        session=session,
                        priority=priority,
                    )
                session.add(category)
                session.flush()
                session.refresh(category)
        return category_models.Category(
            id=category.id,
            name=category.name,
            icon=category.icon,
            priority=category.priority,
            is_hidden=category.is_hidden,
            can_be_seen=category.can_be_seen,
            max_displayed_stock_count=category.max_displayed_stock_count,
            parent_id=category.parent_id
        )

    def update_name(self, *, category_id: int, category_name: str) -> bool:
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
            category_id: int,
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
            category_id: int,
            max_displayed_stock_count: int,
    ) -> bool:
        """
        Update the max displayed stock count of a category with the given ID.

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

    def update_priority(
            self,
            *,
            category_id: int,
            category_priority: int,
    ) -> bool:
        """
        Update the priority of a category with the given ID.

        Args:
            category_id: The ID of the category to update.
            category_priority: Priority of the category.

        Returns:
            True if the category priority was successfully updated,
            False otherwise.
        """
        statement = (
            update(Category)
            .where(Category.id == category_id)
            .values(priority=category_priority)
        )
        with self._session_factory() as session:
            with session.begin():
                result = session.execute(statement)
        is_updated = bool(result.rowcount)

        with bound_contextvars(
                category_id=category_id,
                priority=category_priority,
        ):
            if is_updated:
                logger.debug(
                    'Category repository: priority successfully updated'
                )
            else:
                logger.debug(
                    'Category repository: could not update category priority'
                )
        return is_updated

    def update_hidden_status(
            self,
            *,
            category_id: int,
            is_hidden: bool,
    ) -> bool:
        """
        Update the hidden status of a category with the given ID.

        Args:
            category_id: The ID of the category to update.
            is_hidden: Is category hidden.

        Returns:
            True if the category hidden status was successfully updated,
            False otherwise.
        """
        statement = (
            update(Category)
            .where(Category.id == category_id)
            .values(is_hidden=is_hidden)
        )
        with self._session_factory() as session:
            with session.begin():
                result = session.execute(statement)
        is_updated = bool(result.rowcount)

        with bound_contextvars(
                category_id=category_id,
                is_hidden=is_hidden,
        ):
            if is_updated:
                logger.debug(
                    'Category repository: hidden status successfully updated'
                )
            else:
                logger.debug(
                    'Category repository: could not update hidden status'
                )
        return is_updated

    def update_can_be_seen_status(
            self,
            *,
            category_id: int,
            can_be_seen: bool,
    ) -> bool:
        """
        Update the can be seen status of a category with the given ID.

        Args:
            category_id: The ID of the category to update.
            can_be_seen: Can category be seen.

        Returns:
            True if the category can be seen status was successfully updated,
            False otherwise.
        """
        statement = (
            update(Category)
            .where(Category.id == category_id)
            .values(can_be_seen=can_be_seen)
        )
        with self._session_factory() as session:
            with session.begin():
                result = session.execute(statement)
        is_updated = bool(result.rowcount)

        with bound_contextvars(
                category_id=category_id,
                can_be_seen=can_be_seen,
        ):
            if is_updated:
                logger.debug(
                    'Category repository:'
                    ' can be seen status successfully updated'
                )
            else:
                logger.debug(
                    'Category repository: could not update can be seen status'
                )
        return is_updated

    def get_subcategory_ids(self, parent_id: int) -> list[int]:
        statement = select(Category.id).where(Category.parent_id == parent_id)
        with self._session_factory() as session:
            result = session.execute(statement).all()
        return [row[0] for row in result]
