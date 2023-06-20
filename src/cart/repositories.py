from sqlalchemy import select

from cart import models as cart_models
from common.repositories import BaseRepository
from database.schemas import CartProduct, User, Product

__all__ = ('CartRepository',)


class CartRepository(BaseRepository):

    def get_cart_products(
            self,
            *,
            user_telegram_id: int,
    ) -> list[cart_models.CartProduct]:
        statement = (
            select(
                CartProduct.id,
                Product.id,
                Product.name,
                Product.price,
                CartProduct.quantity,
            )
            .join(User, onclause=CartProduct.user_id == User.id)
            .join(Product, onclause=CartProduct.product_id == Product.id)
            .where(User.telegram_id == user_telegram_id)
        )
        with self._session_factory() as session:
            rows = session.execute(statement).all()
        return [
            cart_models.CartProduct(
                id=cart_product_id,
                product=cart_models.Product(
                    id=product_id,
                    name=product_name,
                    price=price,
                ),
                quantity=quantity,
            )
            for cart_product_id, product_id, product_name, price, quantity
            in rows
        ]
