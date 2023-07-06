import structlog
from structlog.stdlib import BoundLogger

from cart.repositories import CartRepository

__all__ = ('release_expired_cart_products',)

logger: BoundLogger = structlog.get_logger('app')


def release_expired_cart_products(
        cart_repository: CartRepository,
        max_stored_time_in_seconds: int,
) -> None:
    cart_products = cart_repository.get_expired_cart_products(
        max_stored_time_in_seconds
    )
    for cart_product in cart_products:
        cart_repository.release_expired_cart_product(cart_product)
        logger.debug(
            'Cart product has been deleted for inactivity',
            product_id=cart_product.product.id,
            quantity=cart_product.quantity,
        )
