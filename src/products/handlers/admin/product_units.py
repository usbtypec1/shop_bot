import os
import uuid

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, Message, ContentType
from loader import dp
from services import product_services

import config
import database
import responses.product_management
from common.filters import AdminFilter
from common.views import answer_view
from database import queries
from products.callback_data import (
    ProductCallbackFactory,
    ProductUnitCallbackFactory,
)
from products.services import answer_view_with_media
from products.states import AddProductUnitStates, EditProductUnitStates
from products.views import (
    AdminProductDetailView, ProductUnitCreateView,
    ProductUnitLoadingCompleteView
)


@dp.callback_query_handler(
    ProductCallbackFactory().filter(action='add_units'),
    AdminFilter(),
    state='*',
)
async def add_product_unit(
        query: CallbackQuery,
        callback_data: dict[str, str],
        state: FSMContext,
) -> None:
    await state.update_data(callback_data | {'units': []})
    view = ProductUnitCreateView()
    await AddProductUnitStates.waiting_content.set()
    await answer_view(message=query.message, view=view)


@dp.message_handler(
    Text('✅ Complete'),
    AdminFilter(),
    state=AddProductUnitStates.waiting_content,
)
async def complete_units_loading(
        message: Message,
        state: FSMContext,
) -> None:
    data = await state.get_data()
    product_id = data['product_id']
    units = data['units']
    await state.finish()
    with database.create_session() as session:
        for unit in units:
            unit.create_product_unit(session)
        queries.edit_product_quantity(session, product_id, len(units))
        product = queries.get_product(session, product_id)
        view = ProductUnitLoadingCompleteView(product.name)
        await answer_view(message=message, view=view)
        view = AdminProductDetailView(product)
        await answer_view_with_media(
            message=message,
            base_path=config.PRODUCT_PICTURE_PATH,
            product=product,
            view=view,
        )


@dp.message_handler(
    AdminFilter(),
    content_types=(
            ContentType.TEXT,
            ContentType.PHOTO,
            ContentType.DOCUMENT,
    ),
    state=AddProductUnitStates.waiting_content,
)
async def add_product_unit(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    units, product_id = data['units'], data['product_id']
    pending_dir = config.PENDING_DIR_PATH / str(message.from_user.id)
    if message.document is not None:
        filename = f'{uuid.uuid4()}.{message.document.mime_subtype}'
        await message.document.download(destination_file=pending_dir / filename)
        units.append(
            product_services.ProductUnitLifeCycle(
                product_id, product_unit_content=filename,
                product_unit_type='document',
                pending_dir_path=pending_dir)
        )
    elif len(message.photo) > 0:
        filename = f'{uuid.uuid4()}.jpg'
        await message.photo[-1].download(
            destination_file=pending_dir / filename)
        units.append(
            product_services.ProductUnitLifeCycle(
                product_id, product_unit_content=filename,
                product_unit_type='document',
                pending_dir_path=pending_dir)
        )
    elif message.text is not None:
        for unit in message.text.split('\n'):
            units.append(product_services.ProductUnitLifeCycle(
                product_id, product_unit_content=unit,
                product_unit_type='text'
            ))
    await state.update_data({'units': units})
    await message.answer('✅ Goods loaded')


@dp.callback_query_handler(
    ProductCallbackFactory().filter(action='units'),
    AdminFilter(),
    state='*',
)
async def product_units(
        query: CallbackQuery,
        callback_data: dict[str, str],
) -> None:
    product_id = int(callback_data['product_id'])
    subcategory_id = callback_data['subcategory_id']
    subcategory_id = int(subcategory_id) if subcategory_id != '' else None
    with database.create_session() as session:
        units = queries.get_not_sold_product_units(session, product_id)
        await responses.product_management.ProductUnitsResponse(
            query, int(callback_data['category_id']), product_id,
            units, subcategory_id
        )


@dp.callback_query_handler(
    ProductUnitCallbackFactory().filter(action='manage'),
    AdminFilter(),
    state='*',
)
async def product_unit_menu(
        query: CallbackQuery,
        callback_data: dict[str, str],
) -> None:
    unit_id = int(callback_data['id'])
    subcategory_id = callback_data['subcategory_id']
    subcategory_id = int(subcategory_id) if subcategory_id != '' else None
    with database.create_session() as session:
        unit = queries.get_product_unit(session, unit_id)
        await responses.product_management.ProductUnitResponse(
            query, int(callback_data['product_id']), unit,
            int(callback_data['category_id']), subcategory_id
        )


@dp.callback_query_handler(
    ProductUnitCallbackFactory().filter(action='edit'),
    AdminFilter(),
    state='*',
)
async def edit_product_unit(
        query: CallbackQuery,
        callback_data: dict[str, str],
) -> None:
    await query.message.edit_text('📝 Enter the new product data, or Load file')
    await EditProductUnitStates.waiting_content.set()
    await dp.current_state().update_data(callback_data)


@dp.message_handler(
    AdminFilter(),
    state=EditProductUnitStates.waiting_content,
    content_types=(
            ContentType.PHOTO,
            ContentType.DOCUMENT,
    ),
)
async def edit_product_unit(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    subcategory_id = data['subcategory_id']
    subcategory_id = int(subcategory_id) if subcategory_id != '' else None
    unit_id = int(data['id'])
    await state.finish()
    with database.create_session() as session:
        product_unit = queries.get_product_unit(session, unit_id)
        filename = product_unit.content if product_unit.type == 'document' else str(
            uuid.uuid4())
        if len(message.photo) > 0:
            filename = f'{filename}.jpg'
            await message.photo[-1].download(
                destination_file=config.PRODUCT_UNITS_PATH / filename)
        elif message.document is not None:
            filename = f'{filename}.{message.document.mime_type}'
            await message.document.download(
                destination_file=config.PRODUCT_UNITS_PATH / filename)
        if product_unit.type != 'document':
            queries.edit_product_unit(session, unit_id, 'document', filename)
        await responses.product_management.ProductUnitResponse(
            message, int(data['product_id']), product_unit,
            int(data['category_id']), subcategory_id
        )


@dp.message_handler(
    AdminFilter(),
    state=EditProductUnitStates.waiting_content,
)
async def edit_product_unit(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.finish()
    product_unit_id = int(data['id'])
    subcategory_id = data['subcategory_id']
    subcategory_id = int(subcategory_id) if subcategory_id != '' else None
    with database.create_session() as session:
        product_unit = queries.get_product_unit(session, product_unit_id)
        if product_unit.type == 'document':
            if (config.PRODUCT_UNITS_PATH / product_unit.content).exists():
                os.remove(config.PRODUCT_UNITS_PATH / product_unit.content)
        queries.edit_product_unit(session, product_unit_id, 'text',
                                  message.text)
        await responses.product_management.ProductUnitResponse(
            message, int(data['product_id']), product_unit,
            int(data['category_id']), subcategory_id
        )


@dp.callback_query_handler(
    ProductUnitCallbackFactory().filter(action='delete'),
    AdminFilter(),
    state='*',
)
async def delete_product_unit(
        query: CallbackQuery,
        callback_data: dict[str, str],
) -> None:
    product_id = int(callback_data['product_id'])
    subcategory_id = callback_data['subcategory_id']
    subcategory_id = int(subcategory_id) if subcategory_id != '' else None
    product_unit_life_cycle = product_services.ProductUnitLifeCycle(
        product_unit_id=int(callback_data['id']))
    with database.create_session() as session:
        product_unit_life_cycle.delete_product_unit(session)
        queries.edit_product_quantity(session, product_id, -1)
        units = queries.get_not_sold_product_units(session, product_id)
        await query.message.answer('✅ Position removed')
        await responses.product_management.ProductUnitsResponse(
            query, int(callback_data['category_id']), product_id, units,
            subcategory_id
        )
