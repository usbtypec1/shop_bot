from aiogram.types import CallbackQuery

import database
import products.callback_data
import responses.product_management
from common.filters import AdminFilter
from database import queries
from loader import dp
from services import product_services


@dp.callback_query_handler(
    products.callback_data.ProductCallbackFactory().filter(action='delete'),
    AdminFilter(),
)
async def delete_product(
        query: CallbackQuery,
        callback_data: dict[str, str],
) -> None:
    category_id = int(callback_data['category_id'])
    subcategory_id = callback_data['subcategory_id']
    product_id = int(callback_data['product_id'])
    with database.create_session() as session:
        product_services.ProductLifeCycle(product_id=product_id).load_from_db(session).delete(session)
        await responses.product_management.SuccessRemovalUnitResponse(query)
        if subcategory_id != '':
            subcategory_id = int(subcategory_id)
            products = queries.get_category_products(session, subcategory_id=subcategory_id)
            await responses.product_management.SubcategoryProductsResponse(
                query, category_id, subcategory_id, products
            )
        else:
            items = queries.get_category_items(session, category_id)
            await responses.product_management.CategoryItemsResponse(query, items, category_id)


@dp.callback_query_handler(
    products.callback_data.ProductCallbackFactory().filter(action='delete_units'),
    AdminFilter(),
)
async def delete_product_units(
        callback_query: CallbackQuery,
        callback_data: dict[str, str],
) -> None:
    category_id: int = int(callback_data['category_id'])
    subcategory_id: int = int(callback_data['subcategory_id'])
    category_id = int(category_id) if category_id else None
    subcategory_id = int(subcategory_id) if subcategory_id else None

    product_id = int(callback_data['product_id'])
    with database.create_session() as session:
        product_life_cycle = product_services.ProductLifeCycle(
            product_id=product_id).load_from_db(session).delete_product_units(session)
        product = queries.get_product(session, product_id)
        await responses.product_management.ProductResponse(
            callback_query, product, category_id, subcategory_id
        )
