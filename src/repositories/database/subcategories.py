import structlog
from sqlalchemy import select, update, exists, delete
from sqlalchemy.orm import Session
from structlog.contextvars import bound_contextvars

import models
from repositories.database.base import BaseRepository
from services.db_api.schemas import Subcategory

__all__ = ('SubcategoryRepository',)

logger = structlog.get_logger('app')


class SubcategoryRepository(BaseRepository):

    def get_by_id(self, subcategory_id: int) -> models.Subcategory:
        with bound_contextvars(subcategory_id=subcategory_id):
            logger.debug('Subcategory repository: retrieving subcategory by ID')

            with self._session_factory() as session:
                result = session.get(Subcategory, subcategory_id)

            logger.debug('Subcategory repository: retrieved subcategory by ID')

        return models.Subcategory(
            id=result.id,
            name=result.name,
            icon=result.icon,
            priority=result.priority,
            max_displayed_stock_count=result.max_displayed_stock_count,
            is_hidden=result.is_hidden,
            can_be_seen=result.can_be_seen,
            category_id=result.category_id,
        )

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
            category_id: int
    ) -> None:
        statement = (
            update(Subcategory)
            .where(
                Subcategory.priority >= priority,
                Subcategory.category_id == category_id,
            )
            .values(priority=Subcategory.priority + 1)
        )
        session.execute(statement)

    def create(
            self,
            *,
            name: str,
            priority: int,
            category_id: int,
            max_displayed_stock_count: int,
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
            max_displayed_stock_count=max_displayed_stock_count,
        )
        statement = select(exists().where(Subcategory.priority == priority))
        with self._session_factory() as session:
            with session.begin():
                is_same_priority_subcategory_exists = session.scalar(statement)
                if is_same_priority_subcategory_exists:
                    self.__shift_subcategory_priorities(
                        session=session,
                        priority=priority,
                        category_id=category_id,
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
            max_displayed_stock_count=subcategory.max_displayed_stock_count,
        )

    def delete_by_id(self, subcategory_id: int) -> bool:
        statement = delete(Subcategory).where(Subcategory.id == subcategory_id)

        with (
            bound_contextvars(subcategory_id=subcategory_id),
            self._session_factory() as session,
            session.begin(),
        ):
            logger.debug('Subcategory repository: deleting subcategory')

            result = session.execute(statement)

            is_deleted = bool(result.rowcount)

            if is_deleted:
                logger.debug('Subcategory repository: deleted subcategory')
            else:
                logger.debug(
                    'Subcategory repository: could not delete subcategory'
                )
        return is_deleted

    def update_name(self, *, subcategory_id: int, subcategory_name: str) -> bool:
        """
        Update the name of a subcategory with the given ID.

        Args:
            subcategory_id: The ID of the subcategory to update.
            subcategory_name: The new name for the subcategory.

        Returns:
            True if the subcategory name was successfully updated,
            False otherwise.
        """
        statement = (
            update(Subcategory)
            .where(Subcategory.id == subcategory_id)
            .values(name=subcategory_name)
        )
        with self._session_factory() as session:
            with session.begin():
                result = session.execute(statement)
        is_updated = bool(result.rowcount)

        with bound_contextvars(
                subcategory_id=subcategory_id,
                subcategory_name=subcategory_name,
        ):
            if is_updated:
                logger.debug(
                    'Subcategory repository: name successfully updated'
                )
            else:
                logger.debug('Subcategory repository: could not update name')
        return is_updated

    def update_icon(
            self,
            *,
            subcategory_id: int,
            subcategory_icon: str | None = None,
    ) -> bool:
        """
        Update the icon of a subcategory with the given ID.

        Args:
            subcategory_id: The ID of the subcategory to update.
            subcategory_icon: The new icon for the subcategory.

        Returns:
            True if the subcategory icon was successfully updated,
            False otherwise.
        """
        statement = (
            update(Subcategory)
            .where(Subcategory.id == subcategory_id)
            .values(icon=subcategory_icon)
        )
        with self._session_factory() as session:
            with session.begin():
                result = session.execute(statement)
        is_updated = bool(result.rowcount)

        with bound_contextvars(
                subcategory_id=subcategory_id,
                subcategory_icon=subcategory_icon,
        ):
            if is_updated:
                logger.debug(
                    'Subcategory repository: icon successfully updated'
                )
            else:
                logger.debug('Subcategory repository: could not update icon')
        return is_updated

    def update_max_displayed_stock_count(
            self,
            *,
            subcategory_id: int,
            max_displayed_stock_count: int,
    ) -> bool:
        """
        Update the max displayed stock count of a subcategory with the given ID.

        Args:
            subcategory_id: The ID of the subcategory to update.
            max_displayed_stock_count: Max displayed stock count for
                                                the subcategory.

        Returns:
            True if the subcategory icon was successfully updated,
            False otherwise.
        """
        statement = (
            update(Subcategory)
            .where(Subcategory.id == subcategory_id)
            .values(max_displayed_stock_count=max_displayed_stock_count)
        )
        with self._session_factory() as session:
            with session.begin():
                result = session.execute(statement)
        is_updated = bool(result.rowcount)

        with bound_contextvars(
                subcategory_id=subcategory_id,
                max_displayed_stock_count=max_displayed_stock_count,
        ):
            if is_updated:
                logger.debug(
                    'Subcategory repository:'
                    ' max displayed stock count successfully updated'
                )
            else:
                logger.debug(
                    'Subcategory repository:'
                    ' could not update max_displayed_stock_count'
                )
        return is_updated

    def update_priority(
            self,
            *,
            subcategory_id: int,
            subcategory_priority: int,
    ) -> bool:
        """
        Update the priority of a subcategory with the given ID.

        Args:
            subcategory_id: The ID of the subcategory to update.
            subcategory_priority: Priority of the subcategory.

        Returns:
            True if the subcategory priority was successfully updated,
            False otherwise.
        """
        statement = (
            update(Subcategory)
            .where(Subcategory.id == subcategory_id)
            .values(priority=subcategory_priority)
        )
        with self._session_factory() as session:
            with session.begin():
                result = session.execute(statement)
        is_updated = bool(result.rowcount)

        with bound_contextvars(
                subcategory_id=subcategory_id,
                priority=subcategory_priority,
        ):
            if is_updated:
                logger.debug(
                    'Subcategory repository: priority successfully updated'
                )
            else:
                logger.debug(
                    'Subategory repository:'
                    ' could not update subcategory priority'
                )
        return is_updated

    def update_hidden_status(
            self,
            *,
            subcategory_id: int,
            is_hidden: bool,
    ) -> bool:
        """
        Update the hidden status of a subcategory with the given ID.

        Args:
            subcategory_id: The ID of the subcategory to update.
            is_hidden: Is subcategory hidden.

        Returns:
            True if the subcategory hidden status was successfully updated,
            False otherwise.
        """
        statement = (
            update(Subcategory)
            .where(Subcategory.id == subcategory_id)
            .values(is_hidden=is_hidden)
        )
        with self._session_factory() as session:
            with session.begin():
                result = session.execute(statement)
        is_updated = bool(result.rowcount)

        with bound_contextvars(
                subcategory_id=subcategory_id,
                is_hidden=is_hidden,
        ):
            if is_updated:
                logger.debug(
                    'Subcategory repository: hidden status successfully updated'
                )
            else:
                logger.debug(
                    'Subcategory repository: could not update hidden status'
                )
        return is_updated

    def update_can_be_seen_status(
            self,
            *,
            subcategory_id: int,
            can_be_seen: bool,
    ) -> bool:
        """
        Update the can be seen status of a subcategory with the given ID.

        Args:
            subcategory_id: The ID of the subcategory to update.
            can_be_seen: Can subcategory be seen.

        Returns:
            True if the subcategory can be seen status was successfully updated,
            False otherwise.
        """
        statement = (
            update(Subcategory)
            .where(Subcategory.id == subcategory_id)
            .values(can_be_seen=can_be_seen)
        )
        with self._session_factory() as session:
            with session.begin():
                result = session.execute(statement)
        is_updated = bool(result.rowcount)

        with bound_contextvars(
                subcategory_id=subcategory_id,
                can_be_seen=can_be_seen,
        ):
            if is_updated:
                logger.debug(
                    'Subcategory repository:'
                    ' can be seen status successfully updated'
                )
            else:
                logger.debug(
                    'Subcategory repository:'
                    ' could not update can be seen status'
                )
        return is_updated
