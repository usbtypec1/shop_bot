import decimal
import uuid

import structlog
from aiogram import dispatcher
from aiogram import filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, ContentType, Message

import config
from common.filters import AdminFilter
from common.views import answer_view
from products.callback_data import ProductCallbackFactory
from responses.product_management import (
    SuccessUnitAddingResponse,
    AddProductDescriptionResponse,
    AddProductPriceResponse,
    AddProductImageResponse,
    AddProductNameResponse,
    SuccessProductAddingResponse,
    AddProductUnitResponse,
    IncorrectPriceResponse,
)
from services.product_services import ProductLifeCycle
from users.views import AdminMenuView

logger = structlog.get_logger('app')


@dp.callback_query_handler(
    ProductCallbackFactory().filter(action='add', product_id=''),
    AdminFilter(),
)
async def add_product(
        query: CallbackQuery,
        callback_data: dict[str, str],
        state: FSMContext,
) -> None:
    category_id, subcategory_id = (
        callback_data['category_id'],
        callback_data['subcategory_id'],
    )
    category_id = int(category_id) if category_id != '' else None
    subcategory_id = int(subcategory_id) if subcategory_id != '' else None
    await AddProductStates.waiting_name.set()
    await state.update_data(
        product_life_cycle=ProductLifeCycle(category_id, subcategory_id)
    )
    await AddProductNameResponse(query)


@dp.message_handler(
    AdminFilter(),
    state=AddProductStates.waiting_name,
)
async def on_product_name_input(
        message: Message,
        state: dispatcher.FSMContext,
) -> None:
    state_data = await state.get_data()
    product_life_cycle = state_data['product_life_cycle']
    product_life_cycle.add_product_name(message.text)
    await state.update_data({'product_life_cycle': product_life_cycle})
    await AddProductStates.next()
    await AddProductDescriptionResponse(message)


@dp.message_handler(
    AdminFilter(),
    state=AddProductStates.waiting_description,
)
async def on_product_description_input(
        message: Message,
        state: dispatcher.FSMContext,
):
    product_life_cycle = (await state.get_data())['product_life_cycle']
    product_life_cycle.add_product_description(message.text)
    await state.update_data({'product_life_cycle': product_life_cycle})
    await AddProductStates.next()
    await AddProductImageResponse(message)


@dp.callback_query_handler(
    Text('complete-product-picture-uploading'),
    AdminFilter(),
    state=AddProductStates.waiting_picture,
)
async def complete_product_picture_uploading(
        callback_query: CallbackQuery,
) -> None:
    await AddProductStates.next()
    await AddProductPriceResponse(callback_query.message)


@dp.message_handler(
    AdminFilter(),
    state=AddProductStates.waiting_picture,
    content_types=(
            ContentType.TEXT,
            ContentType.PHOTO,
            ContentType.VIDEO,
            ContentType.ANIMATION,
    ),
)
async def product_picture(
        message: Message,
        state: dispatcher.FSMContext,
) -> None:
    logger.debug('Add product media: photos', photo=message.photo)
    logger.debug('Add product media: video', photo=message.video)
    logger.debug('Add product media: animation', photo=message.animation)

    if not any((message.photo, message.video, message.animation)):
        await AddProductStates.next()
        await AddProductPriceResponse(message)
        return

    state_data = await state.get_data()

    logger.debug('Add product media: state data', state_data=state_data)

    product_life_cycle: ProductLifeCycle = state_data['product_life_cycle']

    pending_dir = config.PENDING_DIR_PATH / str(message.from_user.id)
    product_life_cycle.add_pending_dir_path(pending_dir)

    if message.photo:
        filename = f'{uuid.uuid4()}.jpg'
        await message.photo[-1].download(
            destination_file=pending_dir / filename)
    elif message.video:
        filename = f'{uuid.uuid4()}.mp4'
        await message.video.download(destination_file=pending_dir / filename)
    elif message.animation:
        filename = f'{uuid.uuid4()}.gif.mp4'
        await message.animation.download(
            destination_file=pending_dir / filename)
    else:
        await message.answer('Invalid file')
        return

    logger.debug('Add product media: generated filename', filename=filename)
    product_life_cycle.add_product_picture_filename(filename)

    await state.update_data({'product_life_cycle': product_life_cycle})
    await message.reply('File has been uploaded')


@dp.message_handler(
    AdminFilter(),
    state=AddProductStates.waiting_price,
)
async def product_price(
        message: Message,
        state: dispatcher.FSMContext,
) -> None:
    price = message.text
    if not price.replace('.', '').isdigit():
        await IncorrectPriceResponse(message)
        raise dispatcher.handler.CancelHandler
    state_data = await state.get_data()
    product_life_cycle: ProductLifeCycle = state_data['product_life_cycle']
    product_life_cycle.add_product_price(float(decimal.Decimal(message.text)))
    await state.update_data({'product_life_cycle': product_life_cycle})
    await AddProductStates.next()
    await SuccessProductAddingResponse(
        message=message,
        product_name=product_life_cycle.get_product_name()
    )
    await AddProductUnitResponse(message)


@dp.message_handler(
    filters.Text('✅ Complete'),
    AdminFilter(),
    state=AddProductStates.waiting_content,
)
async def complete_product_adding(
        message: Message,
        state: dispatcher.FSMContext,
) -> None:
    state_data = await state.get_data()
    await state.finish()
    product_life_cycle: ProductLifeCycle = state_data['product_life_cycle']
    logger.debug('Create product', product_life_cycle=product_life_cycle)
    product_life_cycle.create_product()
    await answer_view(message=message, view=AdminMenuView())


@dp.message_handler(
    content_types=(
            ContentType.TEXT,
            ContentType.PHOTO,
            ContentType.DOCUMENT,
    ),
    state=AddProductStates.waiting_content,
)
async def add_product_unit(
        message: Message,
        state: dispatcher.FSMContext,
) -> None:
    state_data = await state.get_data()
    product = state_data['product_life_cycle']
    pending_dir = config.PENDING_DIR_PATH / str(message.from_user.id)
    if message.document is not None:
        product_data_file = pending_dir / f'{uuid.uuid4()}.{message.document.mime_subtype}'
        await message.document.download(destination_file=product_data_file)
        product.add_product_unit(product_data_file.name, 'document',
                                 pending_dir)
    elif len(message.photo) > 0:
        product_data_file = pending_dir / f'{uuid.uuid4()}.jpg'
        await message.photo[-1].download(destination_file=product_data_file)
        product.add_product_unit(product_data_file.name, 'document',
                                 pending_dir)
    elif message.text is not None:
        for product_unit in message.text.split('\n'):
            product.add_product_unit(product_unit, 'text')
    await state.update_data({'product_life_cycle': product})
    await SuccessUnitAddingResponse(message)
