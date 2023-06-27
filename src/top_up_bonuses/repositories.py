from common.repositories import BaseRepository
from database.schemas import TopUpBonus
from top_up_bonuses import models as bonuses_models

__all__ = ('TopUpBonusRepository',)


def map_to_dto(top_up_bonus: TopUpBonus) -> bonuses_models.TopUpBonus:
    return bonuses_models.TopUpBonus(
        id=top_up_bonus.id,
        min_amount_threshold=top_up_bonus.min_amount_threshold,
        bonus_percentage=top_up_bonus.bonus_percentage,
        starts_at=top_up_bonus.starts_at,
        expires_at=top_up_bonus.expires_at,
    )


class TopUpBonusRepository(BaseRepository):

    def create(self):
        pass

    def get_by_id(self):
        pass

    def get_all(self):
        pass

    def update(self):
        pass
