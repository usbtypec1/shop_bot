from datetime import datetime

from sqlalchemy import select, delete

from common.repositories import BaseRepository
from database.schemas import TimeSensitiveDiscount
from time_sensitive_discounts import models as discounts_models
from time_sensitive_discounts.exceptions import (
    TimeSensitiveDiscountDoesNotExistError,
)

__all__ = ('TimeSensitiveDiscountRepository',)


def map_to_dto(
        time_sensitive_discount: TimeSensitiveDiscount,
) -> discounts_models.TimeSensitiveDiscount:
    """
    Maps a database model TimeSensitiveDiscount object
    to a TimeSensitiveDiscount DTO object.

    Args:
        time_sensitive_discount: TimeSensitiveDiscount database model.

    Returns:
        The mapped TimeSensitiveDiscount DTO.
    """
    return discounts_models.TimeSensitiveDiscount(
        id=time_sensitive_discount.id,
        starts_at=time_sensitive_discount.starts_at,
        expires_at=time_sensitive_discount.expires_at,
        code=time_sensitive_discount.code,
        value=time_sensitive_discount.value,
    )


class TimeSensitiveDiscountRepository(BaseRepository):
    """
    Repository for managing TimeSensitiveDiscount objects.

    Methods:
        create: Create a new TimeSensitiveDiscount object.
        get_all: Retrieve all TimeSensitiveDiscount objects.
        get_by_id: Retrieve a TimeSensitiveDiscount object by ID.
        delete_by_id: Delete a TimeSensitiveDiscount object by ID.
        update: Update a TimeSensitiveDiscount object by ID.
    """

    def create(
            self,
            *,
            starts_at: datetime | None,
            expires_at: datetime | None,
            code: str,
            value: int,
    ) -> discounts_models.TimeSensitiveDiscount:
        """
        Create a new TimeSensitiveDiscount object.

        Keyword Args:
            starts_at: The start date and time of the discount.
            expires_at: The expiration date and time of the discount.
            code: The discount code.
            value: The value of the discount.

        Returns:
            The created TimeSensitiveDiscount object.
        """
        time_sensitive_discount = TimeSensitiveDiscount(
            starts_at=starts_at,
            expires_at=expires_at,
            code=code,
            value=value,
        )
        with self._session_factory() as session:
            with session.begin():
                session.add(time_sensitive_discount)
                session.flush()
                session.refresh(time_sensitive_discount)
        return map_to_dto(time_sensitive_discount)

    def get_all(self) -> list[discounts_models.TimeSensitiveDiscount]:
        """
        Retrieve all TimeSensitiveDiscount objects.

        Returns:
            A list of TimeSensitiveDiscount objects.
        """
        statement = select(TimeSensitiveDiscount)
        with self._session_factory() as session:
            time_sensitive_discounts = session.scalars(statement).all()
        return [
            map_to_dto(time_sensitive_discount)
            for time_sensitive_discount in time_sensitive_discounts
        ]

    def get_by_id(
            self,
            time_sensitive_discount_id: int,
    ) -> discounts_models.TimeSensitiveDiscount:
        """
        Retrieve a TimeSensitiveDiscount object by ID.

        Args:
            time_sensitive_discount_id: The ID of the TimeSensitiveDiscount.

        Returns:
            The retrieved TimeSensitiveDiscount object.

        Raises:
            TimeSensitiveDiscountDoesNotExistError: If the TimeSensitiveDiscount
                                                    does not exist.
        """
        statement = (
            select(TimeSensitiveDiscount)
            .where(TimeSensitiveDiscount.id == time_sensitive_discount_id)
        )
        with self._session_factory() as session:
            time_sensitive_discount = session.scalar(statement)
        if time_sensitive_discount is None:
            raise TimeSensitiveDiscountDoesNotExistError
        return map_to_dto(time_sensitive_discount)

    def delete_by_id(self, time_sensitive_discount_id: int) -> None:
        """
        Delete a TimeSensitiveDiscount by ID.

        Args:
            time_sensitive_discount_id: The ID of the TimeSensitiveDiscount.
        """
        statement = (
            delete(TimeSensitiveDiscount)
            .where(TimeSensitiveDiscount.id == time_sensitive_discount_id)
        )
        with self._session_factory() as session:
            with session.begin():
                session.execute(statement)

    def update(
            self,
            *,
            id_: int,
            starts_at: datetime | None,
            expires_at: datetime | None,
            code: str,
            value: int,
    ) -> discounts_models.TimeSensitiveDiscount:
        """
        Update TimeSensitiveDiscount object.

        Keyword Args:
            id_: Id of the TimeSensitiveDiscount object.
            starts_at: The start date and time of the discount.
            expires_at: The expiration date and time of the discount.
            code: The discount code.
            value: The value of the discount.

        Returns:
            The updated TimeSensitiveDiscount object.
        """
        time_sensitive_discount = TimeSensitiveDiscount(
            id=id_,
            starts_at=starts_at,
            expires_at=expires_at,
            code=code,
            value=value,
        )
        with self._session_factory() as session:
            with session.begin():
                session.merge(time_sensitive_discount)
        return map_to_dto(time_sensitive_discount)
