from sqlalchemy import select, update

from cart import models as cart_models
from common.repositories import BaseRepository
from database.schemas import CartProduct, User, Product
from products.exceptions import ProductDoesNotExistError

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

    def create(
            self,
            *,
            user_id: int,
            product_id: int,
            quantity: int = 0,
    ) -> None:
        cart_product = CartProduct(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity
        )
        product_quantity_update_statement = (
            update(Product)
            .where(Product.id == product_id)
            .values(quantity=Product.quantity - quantity)
        )
        with self._session_factory() as session:
            with session.begin():
                session.add(cart_product)
                session.execute(product_quantity_update_statement)

    def get_quantity(self, cart_product_id: int) -> int:
        statement = (
            select(CartProduct.quantity)
            .where(CartProduct.id == cart_product_id)
        )
        with self._session_factory() as session:
            row = session.execute(statement).first()
        if row is None:
            raise ProductDoesNotExistError
        return row[0]

    def update_quantity(
            self,
            *,
            product_id: int,
            quantity: int,
            cart_product_id: int | None = None,
    ) -> None:
        product_quantity_statement = (
            select(Product.quantity)
            .where(Product.id == product_id)
        )

        if cart_product_id is None:
            cart_product_quantity = 0
        else:
            cart_product_quantity = self.get_quantity(cart_product_id)

        with self._session_factory() as session:
            product_quantity_row = (
                session.execute(product_quantity_statement).first()
            )
            if product_quantity_row is None:
                raise ProductDoesNotExistError

            product_quantity: int = product_quantity_row[0]

            quantity_to_add_to_user_cart = quantity - cart_product_quantity
            product_quantity_after_update = (
                    product_quantity - quantity_to_add_to_user_cart
            )

            update_product_quantity_statement = (
                update(Product)
                .where(Product.id == product_id)
                .values(quantity=product_quantity_after_update)
            )
            update_cart_product_quantity_statement = (
                update(CartProduct)
                .where(CartProduct.id == cart_product_id)
                .values(quantity=quantity)
            )

            with session.begin():
                session.execute(update_product_quantity_statement)
                session.execute(update_cart_product_quantity_statement)
