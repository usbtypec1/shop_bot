from dataclasses import dataclass

import pytest

from cart.exceptions import (
    NotEnoughProductQuantityError,
    ProductQuantityOutOfRangeError,
)
from cart.services import validate_product_quantity_change


@dataclass(frozen=True, slots=True)
class MockProduct:
    quantity: int = 0
    max_order_quantity: int | None = None
    min_order_quantity: int | None = None


def test_validate_product_quantity_change_not_enough_quantity():
    product = MockProduct(quantity=5)
    cart_product_quantity = 3
    will_be_changed_to = 9

    with pytest.raises(NotEnoughProductQuantityError):
        validate_product_quantity_change(
            product=product,
            cart_product_quantity=cart_product_quantity,
            will_be_changed_to=will_be_changed_to,
        )


def test_validate_product_quantity_change_out_of_range():
    product = MockProduct(
        quantity=10,
        max_order_quantity=5,
        min_order_quantity=1,
    )
    cart_product_quantity = 5
    will_be_changed_to = 7
    with pytest.raises(ProductQuantityOutOfRangeError):
        validate_product_quantity_change(
            product=product,
            cart_product_quantity=cart_product_quantity,
            will_be_changed_to=will_be_changed_to,
        )


def test_validate_product_quantity_change_within_range():
    product = MockProduct(
        quantity=10,
        max_order_quantity=20,
        min_order_quantity=1,
    )
    cart_product_quantity = 5
    will_be_changed_to = 8
    validate_product_quantity_change(
        product=product,
        cart_product_quantity=cart_product_quantity,
        will_be_changed_to=will_be_changed_to,
    )


def test_validate_product_quantity_change_no_range_limits():
    product = MockProduct(quantity=10)
    cart_product_quantity = 5
    will_be_changed_to = 8

    validate_product_quantity_change(
        product=product,
        cart_product_quantity=cart_product_quantity,
        will_be_changed_to=will_be_changed_to
    )
