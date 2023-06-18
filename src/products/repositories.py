from collections.abc import Iterable
from decimal import Decimal

from sqlalchemy import select, delete, update
from sqlalchemy.orm import joinedload

from common.repositories import BaseRepository
from database import schemas as database_models
from products.models import Product, PaymentMethod, ProductMedia

__all__ = ('ProductRepository',)


class ProductRepository(BaseRepository):

    def create(
            self,
            *,
            name: str,
            description: str,
            media: Iterable[ProductMedia],
            price: Decimal,
            category_id: int,
            min_order_quantity: int | None = None,
            max_order_quantity: int | None = None,
            max_replacement_time_in_minutes: int = 15,
            max_displayed_stock_count: int | None = None,
            is_duplicated_stock_entries_allowed: bool = False,
            is_hidden: bool = True,
            can_be_purchased: bool = False,
            permitted_gateways: Iterable[PaymentMethod] | None = None,
    ) -> Product:
        if permitted_gateways is None:
            permitted_gateways = []

        product = database_models.Product(
            name=name,
            description=description,
            category_id=category_id,
            price=price,
            min_order_quantity=min_order_quantity,
            max_order_quantity=max_order_quantity,
            max_replacement_time_in_minutes=max_replacement_time_in_minutes,
            max_displayed_stock_count=max_displayed_stock_count,
            is_duplicated_stock_entries_allowed=is_duplicated_stock_entries_allowed,
            is_hidden=is_hidden,
            can_be_purchased=can_be_purchased,
        )
        product_media_to_insert = [
            database_models.ProductMedia(
                uuid=product_media.uuid,
                type=product_media.type,
                product=product,
            ) for product_media in media
        ]
        permitted_gateways_to_insert = [
            database_models.ProductPermittedGateway(
                product=product,
                payment_method=payment_method,
            ) for payment_method in permitted_gateways
        ]
        with self._session_factory() as session:
            with session.begin():
                session.add(product)
                session.add_all(product_media_to_insert)
                session.add_all(permitted_gateways_to_insert)
                session.flush()
                session.refresh(product)

        return Product(
            id=product.id,
            category_id=product.category_id,
            name=product.name,
            description=product.description,
            price=product.price,
            quantity=product.quantity,
            min_order_quantity=product.min_order_quantity,
            max_order_quantity=product.max_order_quantity,
            max_replacement_time_in_minutes=product.max_replacement_time_in_minutes,
            max_displayed_stock_count=product.max_displayed_stock_count,
            is_duplicated_stock_entries_allowed=product.is_duplicated_stock_entries_allowed,
            is_hidden=product.is_hidden,
            can_be_purchased=product.can_be_purchased,
            media=list(media),
            permitted_gateways=list(permitted_gateways),
        )

    def get_by_id(self, product_id: int) -> Product:
        statement = (
            select(database_models.Product)
            .where(database_models.Product.id == product_id)
            .options(
                joinedload(database_models.Product.media),
                joinedload(database_models.Product.permitted_gateways),
            )
        )
        with self._session_factory() as session:
            product = session.scalar(statement)
        permitted_gateways = [
            permitted_gateway.payment_method
            for permitted_gateway in product.permitted_gateways
        ]
        media = [
            ProductMedia(
                uuid=product_media.uuid,
                type=product_media.type,
            ) for product_media in product.media
        ]
        return Product(
            id=product.id,
            category_id=product.category_id,
            name=product.name,
            description=product.description,
            price=product.price,
            quantity=product.quantity,
            min_order_quantity=product.min_order_quantity,
            max_order_quantity=product.max_order_quantity,
            max_replacement_time_in_minutes=product.max_replacement_time_in_minutes,
            max_displayed_stock_count=product.max_displayed_stock_count,
            is_duplicated_stock_entries_allowed=product.is_duplicated_stock_entries_allowed,
            is_hidden=product.is_hidden,
            can_be_purchased=product.can_be_purchased,
            media=media,
            permitted_gateways=permitted_gateways,
        )

    def get_by_category_id(self, category_id: int) -> list[Product]:
        statement = (
            select(database_models.Product)
            .where(database_models.Product.category_id == category_id)
            .options(
                joinedload(database_models.Product.media),
                joinedload(database_models.Product.permitted_gateways),
            )
        )
        with self._session_factory() as session:
            products = session.scalars(statement).unique().all()
        return [
            Product(
                id=product.id,
                category_id=product.category_id,
                name=product.name,
                description=product.description,
                price=product.price,
                quantity=product.quantity,
                min_order_quantity=product.min_order_quantity,
                max_order_quantity=product.max_order_quantity,
                max_replacement_time_in_minutes=product.max_replacement_time_in_minutes,
                max_displayed_stock_count=product.max_displayed_stock_count,
                is_duplicated_stock_entries_allowed=product.is_duplicated_stock_entries_allowed,
                is_hidden=product.is_hidden,
                can_be_purchased=product.can_be_purchased,
                media=product.media,
                permitted_gateways=product.permitted_gateways,
            ) for product in products
        ]

    def update_media(
            self,
            *,
            product_id: int,
            media: Iterable[ProductMedia],
    ) -> None:
        delete_statement = (
            delete(database_models.Product)
            .where(database_models.Product.id == product_id)
        )
        media_to_insert = [
            database_models.ProductMedia(
                product_id=product_id,
                uuid=product_media.uuid,
                type=product_media.type,
            ) for product_media in media
        ]

        with self._session_factory() as session:
            with session.begin():
                session.execute(delete_statement)
                session.add_all(media_to_insert)

    def update_permitted_gateways(
            self,
            *,
            product_id: int,
            payment_methods: Iterable[PaymentMethod],
    ) -> None:
        delete_statement = (
            delete(database_models.ProductPermittedGateway)
            .where(
                database_models.ProductPermittedGateway.product_id == product_id
            )
        )
        payment_methods_to_insert = [
            database_models.ProductPermittedGateway(
                product_id=product_id,
                payment_method=payment_method,
            ) for payment_method in payment_methods
        ]
        with self._session_factory() as session:
            with session.begin():
                session.execute(delete_statement)
                session.add_all(payment_methods_to_insert)

    def __update_by_id(self, *, product_id, values_to_update: dict) -> None:
        statement = (
            update(database_models.Product)
            .where(database_models.Product.id == product_id)
            .values(values_to_update)
        )
        with self._session_factory() as session:
            with session.begin():
                session.execute(statement)

    def update_name(self, *, product_id: int, name: str) -> None:
        self.__update_by_id(
            product_id=product_id,
            values_to_update={'name': name},
        )

    def update_description(self, *, product_id: int, description: str) -> None:
        self.__update_by_id(
            product_id=product_id,
            values_to_update={'description': description},
        )

    def update_price(self, *, product_id: int, price: Decimal) -> None:
        self.__update_by_id(
            product_id=product_id,
            values_to_update={'price': price},
        )

    def update_quantity(self, *, product_id: int, quantity: int) -> None:
        self.__update_by_id(
            product_id=product_id,
            values_to_update={'quantity': quantity},
        )

    def update_min_order_quantity(self, *, product_id: int,
                                  min_order_quantity: int | None) -> None:
        self.__update_by_id(
            product_id=product_id,
            values_to_update={'min_order_quantity': min_order_quantity},
        )

    def update_max_order_quantity(self, *, product_id: int,
                                  max_order_quantity: int | None) -> None:
        self.__update_by_id(
            product_id=product_id,
            values_to_update={'max_order_quantity': max_order_quantity},
        )

    def update_max_replacement_time(self, *, product_id: int,
                                    max_replacement_time: int) -> None:
        self.__update_by_id(
            product_id=product_id,
            values_to_update={
                'max_replacement_time_in_minutes': max_replacement_time,
            },
        )

    def update_max_displayed_stock_count(
            self,
            *,
            product_id: int,
            max_displayed_stock_count: int | None
    ) -> None:
        self.__update_by_id(
            product_id=product_id,
            values_to_update={
                'max_displayed_stock_count': max_displayed_stock_count,
            },
        )

    def update_duplicated_stock_entries_status(
            self,
            *,
            product_id: int,
            is_duplicated_stock_entries_allowed: bool,
    ) -> None:
        self.__update_by_id(
            product_id=product_id,
            values_to_update={
                'is_duplicated_stock_entries_allowed': (
                    is_duplicated_stock_entries_allowed
                ),
            },
        )

    def update_hidden_status(self, *, product_id: int, is_hidden: bool) -> None:
        self.__update_by_id(
            product_id=product_id,
            values_to_update={'is_hidden': is_hidden},
        )

    def update_can_be_purchased_status(
            self,
            *,
            product_id: int,
            can_be_purchased: bool,
    ) -> None:
        self.__update_by_id(
            product_id=product_id,
            values_to_update={'can_be_purchased': can_be_purchased},
        )
