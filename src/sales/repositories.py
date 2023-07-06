from collections.abc import Iterable
from decimal import Decimal

from sqlalchemy import select, func, delete, update

from cart import models as cart_models
from common.repositories import BaseRepository
from database.schemas import Sale, SoldProduct, CartProduct, User
from payments import models as payments_models
from sales import models as sales_models

__all__ = ('SaleRepository',)


def map_to_sale_dto(
        sale: Sale,
        sold_products: Iterable[SoldProduct],
) -> sales_models.Sale:
    return sales_models.Sale(
        id=sale.id,
        payment_method=sale.payment_method,
        created_at=sale.created_at,
        products=[
            sales_models.SoldProduct(
                product_id=sold_product.product_id,
                price_at_the_moment=sold_product.price_at_the_moment,
                quantity=sold_product.quantity,
            ) for sold_product in sold_products
        ]
    )


class SaleRepository(BaseRepository):

    def create_and_subtract_from_balance(
            self,
            *,
            user_id: int,
            cart_products: Iterable[cart_models.CartProduct],
            payment_method: payments_models.PaymentMethod,
    ) -> sales_models.Sale:
        sale = Sale(
            user_id=user_id,
            payment_method=payment_method,
        )
        products_to_be_sold = [
            SoldProduct(
                sale=sale,
                product_id=cart_product.product.id,
                price_at_the_moment=cart_product.product.price,
                quantity=cart_product.quantity,
            ) for cart_product in cart_products
        ]
        cart_product_ids = [cart_product.id for cart_product in cart_products]
        cart_products_delete_statement = (
            delete(CartProduct)
            .where(CartProduct.id.in_(cart_product_ids))
        )
        total_cost = sum(
            cart_product.total_cost
            for cart_product in cart_products
        )
        subtract_from_balance_statement = (
            update(User)
            .where(User.id == user_id)
            .values(balance=User.balance - total_cost)
        )
        with self._session_factory() as session:
            with session.begin():
                session.add(sale)
                session.add_all(products_to_be_sold)
                session.execute(cart_products_delete_statement)
                session.execute(subtract_from_balance_statement)

                session.flush()
                session.refresh(sale)

        return map_to_sale_dto(sale=sale, sold_products=products_to_be_sold)

    def create(
            self,
            user_id: int,
            cart_products: Iterable[cart_models.CartProduct],
            payment_method: payments_models.PaymentMethod,
    ) -> sales_models.Sale:
        sale = Sale(
            user_id=user_id,
            payment_method=payment_method,
        )
        products_to_be_sold = [
            SoldProduct(
                sale=sale,
                product_id=cart_product.product.id,
                price_at_the_moment=cart_product.product.price,
                quantity=cart_product.quantity,
            ) for cart_product in cart_products
        ]
        cart_product_ids = [cart_product.id for cart_product in cart_products]
        cart_products_delete_statement = (
            delete(CartProduct)
            .where(CartProduct.id.in_(cart_product_ids))
        )
        with self._session_factory() as session:
            with session.begin():
                session.add(sale)
                session.add_all(products_to_be_sold)
                session.execute(cart_products_delete_statement)

                session.flush()
                session.refresh(sale)

        return map_to_sale_dto(sale=sale, sold_products=products_to_be_sold)

    def count_by_user_id(self, user_id: int) -> int:
        statement = select(func.count()).where(Sale.user_id == user_id)
        with self._session_factory() as session:
            row = session.execute(statement).first()

        return row[0] if row is not None else 0

    def calculate_total_cost_by_user_id(self, user_id: int) -> Decimal:
        statement = (
            select(
                func.sum(
                    SoldProduct.price_at_the_moment * SoldProduct.quantity
                )
            )
            .join(SoldProduct, onclause=Sale.id == SoldProduct.sale_id)
            .where(Sale.user_id == user_id)
        )
        with self._session_factory() as session:
            row = session.execute(statement).first()
        return row[0] if row is not None else Decimal('0')

    def calculate_total_cost(self) -> Decimal:
        statement = (
            select(
                func.sum(
                    SoldProduct.price_at_the_moment * SoldProduct.quantity
                )
            )
            .join(SoldProduct, onclause=Sale.id == SoldProduct.sale_id)
        )
        with self._session_factory() as session:
            row = session.execute(statement).first()
        return row[0] if row is not None else Decimal('0')

    def count_all(self) -> int:
        statement = select(func.count())
        with self._session_factory() as session:
            row = session.execute(statement).first()
        return row[0] if row is not None else 0
