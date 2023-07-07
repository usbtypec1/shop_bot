from decimal import Decimal

import pytest

from common.services import render_money


@pytest.mark.parametrize(
    'item, expected',
    [
        (10.5000, '10.5'),
        (100.00, '100'),
        (50, '50'),
        (Decimal('10.99900000'), '10.999'),
        (Decimal('-5'), '-5'),
        (-5, '-5'),
        (-5.00220, '-5.0022'),
        (0, '0'),
        (0.0, '0'),
        (Decimal('0.00'), '0'),
        (3.14159, '3.14159'),
        (Decimal('999999999.999999999'), '999999999.999999999'),
        (Decimal('-12345.67890'), '-12345.6789'),
        ('12.345', '12.345'),
        ('123', '123'),
        ('45.000', '45'),
        ('-7', '-7'),
        ('0.00', '0'),
    ],
)
def test_render_money(item, expected):
    assert render_money(item) == expected
