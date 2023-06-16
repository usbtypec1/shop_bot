from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, Message

import database
import responses.product_management
from common.filters import AdminFilter
from database import queries
from loader import dp
from products.callback_data import ProductCallbackFactory


@dp.message_handler(
    Text('📝 Products Management'),
    AdminFilter(),
    state='*',
)
async def product_categories(message: Message) -> None:
    with database.create_session() as session:
        categories = queries.get_all_categories(session)
        await responses.product_management.ProductCategoriesResponse(message,
                                                                     categories)


@dp.callback_query_handler(
    ProductCallbackFactory().filter(
        category_id='', subcategory_id='', product_id='', action='manage'),
    AdminFilter(),
    state='*',
)
async def product_categories(query: CallbackQuery) -> None:
    with database.create_session() as session:
        categories = queries.get_all_categories(session)
        await responses.product_management.ProductCategoriesResponse(query,
                                                                     categories)


@dp.callback_query_handler(
    ProductCallbackFactory().filter(
        subcategory_id='',
        product_id='',
        action='manage',
    ),
    AdminFilter(),
    state='*',
)
async def category_items(
        query: CallbackQuery,
        callback_data: dict[str, str],
) -> None:
    category_id = int(callback_data['category_id'])
    with database.create_session() as session:
        items = queries.get_category_items(session, category_id=category_id)
    await responses.product_management.CategoryItemsResponse(query, items,
                                                             category_id)


@dp.callback_query_handler(
    ProductCallbackFactory().filter(product_id='', action='manage'),
    AdminFilter(),
    state='*',
)
async def subcategory_products(
        query: CallbackQuery,
        callback_data: dict[str, str],
) -> None:
    subcategory_id = int(callback_data['subcategory_id'])
    with database.create_session() as session:
        products = queries.get_category_products(session,
                                                 subcategory_id=subcategory_id)
        await responses.product_management.SubcategoryProductsResponse(
            query, int(callback_data['category_id']), subcategory_id, products
        )


@dp.callback_query_handler(
    ProductCallbackFactory().filter(action='manage'),
    AdminFilter(),
    state='*',
)
async def product_menu(
        query: CallbackQuery,
        callback_data: dict[str, str],
) -> None:
    category_id, subcategory_id = callback_data['category_id'], callback_data[
        'subcategory_id']
    category_id = int(category_id) if category_id != '' else None
    subcategory_id = int(subcategory_id) if subcategory_id != '' else None
    with database.create_session() as session:
        product = queries.get_product(session, int(callback_data['product_id']))
        await responses.product_management.ProductResponse(
            query, product, category_id, subcategory_id
        )
