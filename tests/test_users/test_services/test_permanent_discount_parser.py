import pytest

from users.exceptions import PermanentDiscountValidationError
from users.services import parse_permanent_discount


@pytest.mark.parametrize(
    'permanent_discount, expected',
    [
        ('50', 50),
        ('20', 20),
        ('1', 1),
        ('99', 99),
    ]
)
def test_parse_permanent_discount_valid_integer(permanent_discount, expected):
    assert parse_permanent_discount(permanent_discount) == expected


def test_parse_permanent_discount_invalid_integer():
    permanent_discount = "abc"
    with pytest.raises(PermanentDiscountValidationError) as error:
        parse_permanent_discount(permanent_discount)
    assert str(error.value) == '❌ Permanent discount must be an integer'


@pytest.mark.parametrize(
    'permanent_discount',
    (
            '100',
            '0',
    )
)
def test_parse_permanent_discount_out_of_range(permanent_discount):
    with pytest.raises(PermanentDiscountValidationError) as error:
        parse_permanent_discount(permanent_discount)
    assert str(error.value) == (
        '❌ Permanent discount must be within the range of 1 to 99'
    )
