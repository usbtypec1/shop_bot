from decimal import Decimal

from top_up_bonuses.exceptions import BonusPercentageValidationError

__all__ = (
    'parse_top_up_bonus_percentage',
    'calculate_amount_to_top_up_with_bonus',
)


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


def calculate_amount_to_top_up_with_bonus(
        amount_to_top_up: Decimal,
        bonus_percentage: int,
) -> Decimal:
    return amount_to_top_up + amount_to_top_up * bonus_percentage
