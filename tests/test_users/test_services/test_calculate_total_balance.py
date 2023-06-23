from dataclasses import dataclass
from decimal import Decimal

from users.services import calculate_total_balance


@dataclass(frozen=True, slots=True)
class MockItem:
    balance: Decimal


def test_calculate_total_balance():
    items = [
        MockItem(Decimal('100.50')),
        MockItem(Decimal('200.75')),
        MockItem(Decimal('50.25')),
    ]
    expected_result = Decimal('351.50')
    assert calculate_total_balance(items) == expected_result


def test_calculate_total_balance_empty_items():
    items = []
    expected_result = Decimal('0')
    assert calculate_total_balance(items) == expected_result


def test_calculate_total_balance_single_item():
    items = [MockItem(Decimal('500.25'))]
    expected_result = Decimal('500.25')
    assert calculate_total_balance(items) == expected_result


def test_calculate_total_balance_negative_balance():
    items = [
        MockItem(Decimal('100.50')),
        MockItem(Decimal('-200.75')),
        MockItem(Decimal('50.25')),
    ]
    expected_result = Decimal('-50')
    assert calculate_total_balance(items) == expected_result
