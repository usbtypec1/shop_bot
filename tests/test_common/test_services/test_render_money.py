from decimal import Decimal

import pytest

from common.services import render_money


@pytest.mark.parametrize(
    'item, expected',
    [
        (Decimal('10.5000'), '10.5'),
        (Decimal('100.00'), '100'),
        (Decimal('50'), '50'),
        (Decimal('10.99900000'), '10.999'),
        (Decimal('-5'), '-5'),
        (Decimal('-5.00220'), '-5.0022'),
        (Decimal('0.0'), '0'),
        (Decimal('1234567890'), '1234567890'),
        (Decimal('3.14159'), '3.14159'),
    ]
)
def test_render_money(item, expected):
    assert render_money(item) == expected
