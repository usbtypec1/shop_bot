from top_up_bonuses.exceptions import BonusPercentageValidationError

__all__ = ('parse_top_up_bonus_percentage',)


def parse_top_up_bonus_percentage(bonus_percentage: str) -> int:
    try:
        bonus_percentage = int(bonus_percentage)
    except ValueError:
        raise BonusPercentageValidationError(
            '❌ Bonus percentage must be an integer'
        )
    if bonus_percentage < 1:
        raise BonusPercentageValidationError(
            '❌ Bonus percentage must be greater or equal than 1'
        )
    return bonus_percentage
