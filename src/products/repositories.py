from collections.abc import Iterable

from sqlalchemy import select

from common.repositories import BaseRepository
from database import schemas as database_models
from products.models import Product

__all__ = ('ProductRepository',)


class ProductRepository(BaseRepository):

    def create(
            self,
            *,
            name: str,
            description: str,
            price: float,
            quantity: int,
            pictures: Iterable[str],
            category_id: int,
            subcategory_id: int = None,
    ) -> Product:
        # Concatenate pictures list to string
        # so we can store multiple media files in string column in DB
        picture = '|'.join(pictures) or None

        product = database_models.Product(
            category_id=category_id,
            subcategory_id=subcategory_id,
            name=name,
            description=description,
            picture=picture,
            price=price,
            quantity=quantity,
        )
        with self._session_factory() as session:
            with session.begin():
                session.add(product)
                session.flush()
                session.refresh(product)

        return Product(
            id=product.id,
            category_id=product.category_id,
            subcategory_id=product.subcategory_id,
            name=product.name,
            description=product.description,
            picture=product.picture,
            price=product.price,
            quantity=product.quantity,
            min_order_quantity=product.min_order_quantity,
            max_order_quantity=product.max_order_quantity,
            max_replacement_time_in_minutes=product.max_replacement_time_in_minutes,
            max_displayed_stock_count=product.max_displayed_stock_count,
            is_duplicated_stock_entries_allowed=product.is_duplicated_stock_entries_allowed,
            is_hidden=product.is_hidden,
            can_be_purchased=product.can_be_purchased,
        )

    def get_all(self) -> list[Product]:
        with self._session_factory() as session:
            products = session.scalars(database_models.Product).all()
        return [
            Product(
                id=product.id,
                category_id=product.category_id,
                subcategory_id=product.subcategory_id,
                name=product.name,
                description=product.description,
                picture=product.picture,
                price=product.price,
                quantity=product.quantity,
                min_order_quantity=product.min_order_quantity,
                max_order_quantity=product.max_order_quantity,
                max_replacement_time_in_minutes=product.max_replacement_time_in_minutes,
                max_displayed_stock_count=product.max_displayed_stock_count,
                is_duplicated_stock_entries_allowed=product.is_duplicated_stock_entries_allowed,
                is_hidden=product.is_hidden,
                can_be_purchased=product.can_be_purchased,
            ) for product in products
        ]

    def get_by_id(self, product_id: int) -> Product:
        with self._session_factory() as session:
            product = session.get(database_models.Product, product_id)
        return Product(
            id=product.id,
            category_id=product.category_id,
            subcategory_id=product.subcategory_id,
            name=product.name,
            description=product.description,
            picture=product.picture,
            price=product.price,
            quantity=product.quantity,
            min_order_quantity=product.min_order_quantity,
            max_order_quantity=product.max_order_quantity,
            max_replacement_time_in_minutes=product.max_replacement_time_in_minutes,
            max_displayed_stock_count=product.max_displayed_stock_count,
            is_duplicated_stock_entries_allowed=product.is_duplicated_stock_entries_allowed,
            is_hidden=product.is_hidden,
            can_be_purchased=product.can_be_purchased,
        )

    def get_by_category_id(self, category_id: int) -> list[Product]:
        statement = (
            select(database_models.Product)
            .where(database_models.Product.category_id == category_id)
        )
        with self._session_factory() as session:
            products = session.scalars(statement)
        return [
            Product(
                id=product.id,
                category_id=product.category_id,
                subcategory_id=product.subcategory_id,
                name=product.name,
                description=product.description,
                picture=product.picture,
                price=product.price,
                quantity=product.quantity,
                min_order_quantity=product.min_order_quantity,
                max_order_quantity=product.max_order_quantity,
                max_replacement_time_in_minutes=product.max_replacement_time_in_minutes,
                max_displayed_stock_count=product.max_displayed_stock_count,
                is_duplicated_stock_entries_allowed=product.is_duplicated_stock_entries_allowed,
                is_hidden=product.is_hidden,
                can_be_purchased=product.can_be_purchased,
            ) for product in products
        ]
