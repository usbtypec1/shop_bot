from dataclasses import dataclass

import pytest

from cart.views import ProductQuantityOutOfRangeWarningView


@dataclass(frozen=True, slots=True)
class MockProduct:
    min_order_quantity: int | None = None
    max_order_quantity: int | None = None


def test_get_text_with_min_and_max_order_quantity():
    product = MockProduct(min_order_quantity=1, max_order_quantity=10)
    view = ProductQuantityOutOfRangeWarningView(product)
    expected_text = "You can't order less than 1 or more than 10"
    assert view.get_text() == expected_text


def test_get_text_with_min_order_quantity_only():
    product = MockProduct(min_order_quantity=5)
    view = ProductQuantityOutOfRangeWarningView(product)
    expected_text = "You can't order less than 5"
    assert view.get_text() == expected_text


def test_get_text_with_max_order_quantity_only():
    product = MockProduct(max_order_quantity=20)
    view = ProductQuantityOutOfRangeWarningView(product)
    expected_text = "You can't order more than 20"
    assert view.get_text() == expected_text


def test_get_text_with_no_min_or_max_order_quantity():
    product = MockProduct()
    view = ProductQuantityOutOfRangeWarningView(product)
    expected_error = (
        'Neither `min_order_quantity` nor `max_order_quantity` '
        'has been specified for this product'
    )
    with pytest.raises(ValueError) as error:
        view.get_text()

    assert str(error.value) == expected_error
