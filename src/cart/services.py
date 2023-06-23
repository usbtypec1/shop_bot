from typing import Protocol

from cart.exceptions import (
    NotEnoughProductQuantityError,
    ProductQuantityOutOfRangeError,
)

__all__ = (
    'validate_product_quantity_change',
)


class Product(Protocol):
    id: int
    quantity: int
    max_order_quantity: int | None
    min_order_quantity: int | None


def validate_product_quantity_change(
        *,
        product: Product,
        cart_product_quantity: int,
        will_be_changed_to: int,
) -> None:
    """
    Validates the quantity of a product
    that is being changed in a shopping cart.

    Args:
        product: The product being modified.
        cart_product_quantity: The current quantity of the product in the cart.
        will_be_changed_to: The desired quantity to change to.

    Raises:
        NotEnoughProductQuantityError:
            If the product quantity is not sufficient.
        ProductQuantityOutOfRangeError:
            If the desired quantity is outside the allowed range.
    """

    quantity_difference = will_be_changed_to - cart_product_quantity

    if product.quantity < quantity_difference:
        raise NotEnoughProductQuantityError(product_id=product.id)

    product_quantity_after_update = product.quantity - quantity_difference

    need_to_check_max_order_quantity = product.max_order_quantity is not None
    need_to_check_min_order_quantity = product.min_order_quantity is not None

    more_than_allowed = (
            need_to_check_max_order_quantity
            and will_be_changed_to > product.max_order_quantity
    )
    less_than_required = (
            need_to_check_min_order_quantity
            and will_be_changed_to < product.min_order_quantity
    )

    if more_than_allowed or less_than_required:
        raise ProductQuantityOutOfRangeError(product_id=product.id)
