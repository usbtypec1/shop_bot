from collections.abc import Iterable
from decimal import Decimal
from typing import Protocol

from users.exceptions import (
    PermanentDiscountValidationError,
    InsufficientUserBalanceError
)
from users.models import UsersIdentifiers

__all__ = (
    'parse_users_identifiers_for_search',
    'calculate_total_balance',
    'parse_permanent_discount',
    'calculate_discounted_price',
    'validate_user_balance',
    'validate_discount_percentage_range',
)


class HasBalance(Protocol):
    balance: Decimal


def parse_users_identifiers_for_search(
        user_identifiers_text: str,
) -> UsersIdentifiers:
    """
    Parses the user identifiers from the given text for searching.

    The user identifiers can be provided as a string, where each line represents
    either a user ID or a username. The function splits the input text into
    lines and extracts the user IDs and usernames separately.

    Args:
        user_identifiers_text: The text containing user identifiers, where each
            line represents a user ID or a username.

    Returns:
        Instance of UsersIdentifiers with the extracted user IDs and usernames.

    Example:
        >>> parse_users_identifiers_for_search("123\\njohn_doe\\n456\\njane")
        UsersIdentifiers(user_ids=[123, 456], usernames=['john_doe', 'jane'])
    """
    user_identifiers = user_identifiers_text.splitlines()
    user_ids: list[int] = []
    usernames: list[str] = []
    for user_identifier in user_identifiers:
        if user_identifier.isdigit():
            user_ids.append(int(user_identifier))
        else:
            usernames.append(user_identifier)
    return UsersIdentifiers(
        user_ids=user_ids,
        usernames=usernames,
    )


def calculate_total_balance(items: Iterable[HasBalance]) -> Decimal:
    return sum(item.balance for item in items)


def validate_discount_percentage_range(
        discount_percentage: int,
) -> None:
    if not (0 <= discount_percentage <= 99):
        raise PermanentDiscountValidationError(
            '❌ Permanent discount must be within the range of 0 to 99'
        )


def validate_user_balance(
        *,
        user: HasBalance,
        amount_to_subtract: Decimal,
) -> None:
    """
    Validate if the user has sufficient balance to subtract specified amount.

    Args:
        user: The user object with a balance.
        amount_to_subtract: The amount to be subtracted from the user's balance.

    Raises:
        InsufficientUserBalanceError: If the user's balance is less than the
                                      amount to be subtracted.
    """
    if user.balance < amount_to_subtract:
        raise InsufficientUserBalanceError(
            '❌ You have insufficient funds in your balance'
        )


# TODO rename to 'discount_value'
def parse_permanent_discount(permanent_discount: str) -> int:
    """
    Parses the permanent discount value from a string and validates it.

    The permanent discount value is expected to be a string representation of an
    integer between 1 and 99 (inclusive). The function attempts to convert the
    input string to an integer and then performs validation checks.

    Args:
        permanent_discount: The string representation of the permanent discount.

    Returns:
        The parsed permanent discount value as an integer.

    Raises:
        PermanentDiscountValidationError: If the permanent discount value is not
            a valid integer or falls outside the allowed range of 1 to 99.

    Example:
        >>> parse_permanent_discount("25")
        25
    """
    try:
        permanent_discount = int(permanent_discount)
    except ValueError:
        raise PermanentDiscountValidationError(
            '❌ Permanent discount must be an integer'
        )
    validate_discount_percentage_range(permanent_discount)
    return permanent_discount


def calculate_discounted_price(
        original_price: Decimal,
        discount_percentage: int,
) -> Decimal:
    validate_discount_percentage_range(discount_percentage)
    discount_amount = original_price * discount_percentage / 100
    return original_price - discount_amount
