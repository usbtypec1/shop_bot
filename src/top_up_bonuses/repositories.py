from datetime import datetime
from decimal import Decimal

from sqlalchemy import select, delete

from common.repositories import BaseRepository
from database.schemas import TopUpBonus
from top_up_bonuses import models as bonuses_models
from top_up_bonuses.exceptions import TopUpBonusDoesNotExistError

__all__ = ('TopUpBonusRepository',)


def map_to_dto(top_up_bonus: TopUpBonus) -> bonuses_models.TopUpBonus:
    """
    Maps a database model TopUpBonus to a TopUpBonus DTO.

    Args:
        top_up_bonus: The database model TopUpBonus to be mapped.

    Returns:
        The TopUpBonus DTO.
    """
    return bonuses_models.TopUpBonus(
        id=top_up_bonus.id,
        min_amount_threshold=top_up_bonus.min_amount_threshold,
        bonus_percentage=top_up_bonus.bonus_percentage,
        starts_at=top_up_bonus.starts_at,
        expires_at=top_up_bonus.expires_at,
    )


class TopUpBonusRepository(BaseRepository):
    """
    Repository for managing TopUpBonus objects.

    Methods:
        create: Create a new TopUpBonus object.
        get_by_id: Retrieve a TopUpBonus object by ID.
        get_all: Retrieve all TopUpBonus objects.
        update: Update an existing TopUpBonus object.
        delete_by_id: Delete a TopUpBonus object by ID.
        get_by_top_up_amount: Retrieve a TopUpBonus that can be applied
                              to the amount to be topped up.
    """

    def create(
            self,
            *,
            min_amount_threshold: Decimal,
            bonus_percentage: int,
            starts_at: datetime,
            expires_at: datetime | None,
    ) -> bonuses_models.TopUpBonus:
        """
        Create a new TopUpBonus object.

        Keyword Args:
            min_amount_threshold: The minimum amount threshold for the bonus.
            bonus_percentage: The bonus percentage.
            starts_at: The start date and time of the bonus.
            expires_at: The expiration date and time of the bonus.

        Returns:
            The created TopUpBonus as DTO.
        """
        top_up_bonus = TopUpBonus(
            min_amount_threshold=min_amount_threshold,
            bonus_percentage=bonus_percentage,
            starts_at=starts_at,
            expires_at=expires_at,
        )
        with self._session_factory() as session:
            with session.begin():
                session.add(top_up_bonus)
                session.flush()
                session.refresh(top_up_bonus)
        return map_to_dto(top_up_bonus)

    def get_by_id(self, top_up_bonus_id: int) -> bonuses_models.TopUpBonus:
        """
        Retrieve a TopUpBonus DTO by ID.

        Args:
            top_up_bonus_id: The ID of the TopUpBonus.

        Returns:
            The retrieved TopUpBonus DTO.

        Raises:
            TopUpBonusDoesNotExistError: If the TopUpBonus does not exist.
        """
        statement = (
            select(TopUpBonus)
            .where(TopUpBonus.id == top_up_bonus_id)
        )
        with self._session_factory() as session:
            top_up_bonus: TopUpBonus | None = session.scalar(statement)
        if top_up_bonus is None:
            raise TopUpBonusDoesNotExistError
        return map_to_dto(top_up_bonus)

    def get_all(self):
        """
        Retrieve all TopUpBonus objects.

        Returns:
            A list of TopUpBonus DTOs.
        """
        statement = select(TopUpBonus)
        with self._session_factory() as session:
            top_up_bonuses = session.scalars(statement).all()
        return [map_to_dto(top_up_bonus) for top_up_bonus in top_up_bonuses]

    def update(
            self,
            *,
            id_: int,
            min_amount_threshold: Decimal,
            bonus_percentage: int,
            starts_at: datetime,
            expires_at: datetime | None,
    ) -> bonuses_models.TopUpBonus:
        """
        Update an existing TopUpBonus object.

        Args:
            id_: The ID of the TopUpBonus to be updated.
            min_amount_threshold: The minimum amount threshold for the bonus.
            bonus_percentage: The bonus percentage.
            starts_at: The start date and time of the bonus.
            expires_at: The expiration date and time of the bonus.

        Returns:
            The updated TopUpBonus object as DTO.
        """
        top_up_bonus = TopUpBonus(
            id=id_,
            min_amount_threshold=min_amount_threshold,
            bonus_percentage=bonus_percentage,
            starts_at=starts_at,
            expires_at=expires_at,
        )
        with self._session_factory() as session:
            with session.begin():
                session.merge(top_up_bonus)
        return map_to_dto(top_up_bonus)

    def delete_by_id(self, top_up_bonus_id: int) -> None:
        """
        Delete a TopUpBonus by ID.

        Args:
            top_up_bonus_id: The ID of the TopUpBonus.
        """
        statement = delete(TopUpBonus).where(TopUpBonus.id == top_up_bonus_id)
        with self._session_factory() as session:
            with session.begin():
                session.execute(statement)

    def get_by_top_up_amount(
            self,
            amount: Decimal,
    ) -> bonuses_models.TopUpBonus:
        """
        Retrieve a TopUpBonus that can be applied to the amount to be topped up.

        Args:
            amount (Decimal): The top-up amount.

        Returns:
            The retrieved TopUpBonus object.

        Raises:
            TopUpBonusDoesNotExistError: If no matching TopUpBonus is found.

        Examples:
            >>> repository = TopUpBonusRepository()
            >>> bonus = repository.get_by_top_up_amount(amount=Decimal(200.0))
            >>> bonus.min_amount_threshold
            Decimal('100.0')
            >>> bonus.bonus_percentage
            10
        """
        statement = (
            select(TopUpBonus)
            .where(TopUpBonus.min_amount_threshold < amount)
            .order_by(TopUpBonus.min_amount_threshold.asc())
            .limit(1)
        )
        with self._session_factory() as session:
            top_up_bonus = session.scalar(statement)
        if top_up_bonus is None:
            raise TopUpBonusDoesNotExistError
        return map_to_dto(top_up_bonus)
