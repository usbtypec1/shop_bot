import uuid

import aiogram
import structlog
from aiogram import dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import (
    ContentType,
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

import config
from filters import is_admin
from keyboards.inline import callback_factories
from loader import dp
from responses.product_management import (
    EditProductResponse,
    SuccessProductChangeResponse,
    ProductResponse,
    IncorrectPriceResponse,
)
import database
from database import queries
from services.files import answer_medias, batch_move_files, batch_delete_files
from states import product_states

logger = structlog.get_logger('app')


@dp.callback_query_handler(
    callback_factories.ProductCallbackFactory().filter(action='edit_title'),
    is_admin.IsUserAdmin()
)
async def edit_product_title(
        query: aiogram.types.CallbackQuery,
        callback_data: dict[str, str],
):
    await EditProductResponse(query)
    await product_states.EditProductTitle.waiting_title.set()
    await dp.current_state().update_data(callback_data)


@dp.message_handler(
    is_admin.IsUserAdmin(),
    state=product_states.EditProductTitle.waiting_title,
)
async def edit_product_title(
        message: aiogram.types.Message,
        state: dispatcher.FSMContext,
):
    state_data = await state.get_data()
    await state.finish()
    product_id, subcategory_id = (
        int(state_data['product_id']),
        state_data['subcategory_id'],
    )
    subcategory_id = int(subcategory_id) if subcategory_id != '' else None
    with database.create_session() as session:
        queries.edit_product_name(session, product_id, message.text)
        product = queries.get_product(session, product_id)
        await SuccessProductChangeResponse(message)
        await ProductResponse(
            message, category_id=int(state_data['category_id']),
            product=product, subcategory_id=subcategory_id
        )


@dp.callback_query_handler(
    callback_factories.ProductCallbackFactory()
    .filter(action='edit_description'),
    is_admin.IsUserAdmin(),
)
async def edit_product_description(
        query: aiogram.types.CallbackQuery,
        callback_data: dict[str, str],
):
    await EditProductResponse(query)
    await product_states.EditProductDescription.waiting_description.set()
    await dp.current_state().update_data(callback_data)


@dp.message_handler(
    is_admin.IsUserAdmin(),
    state=product_states.EditProductDescription.waiting_description,
)
async def edit_product_description(
        message: aiogram.types.Message,
        state: dispatcher.FSMContext,
):
    state_data = await state.get_data()
    await state.finish()
    product_id, subcategory_id = int(state_data['product_id']), state_data[
        'subcategory_id']
    subcategory_id = int(subcategory_id) if subcategory_id != '' else None
    with database.create_session() as session:
        queries.edit_product_description(session, product_id, message.text)
        product = queries.get_product(session, product_id)
        await SuccessProductChangeResponse(message)
        await ProductResponse(
            message, category_id=int(state_data['category_id']),
            product=product, subcategory_id=subcategory_id
        )


@dp.callback_query_handler(
    callback_factories.ProductCallbackFactory().filter(action='edit_picture'),
    is_admin.IsUserAdmin(),
)
async def edit_product_picture(
        query: aiogram.types.CallbackQuery,
        callback_data: dict[str, str],
):
    with database.create_session() as session:
        product = queries.get_product(session, int(callback_data['product_id']))
        if product.media_file_names:
            await answer_medias(
                message=query.message,
                base_path=config.PRODUCT_PICTURE_PATH,
                product=product,
            )

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Complete',
                    callback_data='complete-product-picture-edit',
                ),
            ]
        ]
    )
    await EditProductResponse(
        query,
        custom_message=(
            '✏️ Please attach or send the new product image.'
            ' If you wish to delete the current image,'
            ' please enter any text.'
            '\nYou must send media files one by one ❗️'
        ),
        custom_markup=markup,
    )

    await product_states.EditProductPicture.waiting_picture.set()
    await dp.current_state().update_data(callback_data)


@dp.message_handler(
    content_types=ContentType.TEXT,
    state=product_states.EditProductPicture.waiting_picture,
)
async def process_edit_picture_text(
        message: aiogram.types.Message,
        state: FSMContext,
):
    async with state.proxy() as data:
        product_id = int(data['product_id'])
        subcategory_id = (
            int(data['subcategory_id'])
            if data['subcategory_id'] != '' else None
        )

        with database.create_session() as session:
            product = queries.get_product(session, product_id)
            if not product.picture:
                await message.answer("❌ No picture found to delete.")
                return
            batch_delete_files(
                base_path=config.PRODUCT_PICTURE_PATH,
                file_names=product.media_file_names,
            )
            queries.edit_product_picture(
                session=session,
                product_id=product.id,
                picture=None,
            )
            await message.answer("✅ The product picture has been deleted.")

    await state.finish()

    # Add the desired responses after deleting the
    # product picture or when there is no picture to delete
    with database.create_session() as session:
        product = queries.get_product(session, product_id)
        await SuccessProductChangeResponse(message)
        await ProductResponse(
            message, category_id=int(data['category_id']),
            product=product, subcategory_id=subcategory_id
        )


@dp.callback_query_handler(
    Text('complete-product-picture-edit'),
    is_admin.IsUserAdmin(),
    state=product_states.EditProductPicture.waiting_picture,
)
async def complete_product_media_edit(
        callback_query: CallbackQuery,
        state: FSMContext,
) -> None:
    state_data = await state.get_data()
    product_id = state_data['product_id']
    file_names = state_data.get('file_names', [])
    subcategory_id = state_data['subcategory_id']
    await state.finish()

    pending_dir = config.PENDING_DIR_PATH / str(callback_query.from_user.id)
    batch_move_files(
        base_path=pending_dir,
        file_names=file_names,
        destination_path=config.PRODUCT_PICTURE_PATH,
    )
    file_names = '|'.join(file_names)

    with database.create_session() as session:
        product = queries.get_product(session, product_id)
        batch_delete_files(
            base_path=config.PRODUCT_PICTURE_PATH,
            file_names=product.media_file_names,
        )
        queries.edit_product_picture(session, product.id, file_names)
        await SuccessProductChangeResponse(
            message=callback_query.message
        )
        await ProductResponse(
            callback_query.message, category_id=int(state_data['category_id']),
            product=product, subcategory_id=subcategory_id
        )


@dp.message_handler(
    is_admin.IsUserAdmin(),
    state=product_states.EditProductPicture.waiting_picture,
    content_types=(
            ContentType.PHOTO,
            ContentType.VIDEO,
            ContentType.ANIMATION,
    ),
)
async def on_product_media_input(
        message: Message,
        state: FSMContext,
):
    state_data = await state.get_data()
    product_id, subcategory_id = (
        int(state_data['product_id']),
        state_data['subcategory_id'],
    )
    subcategory_id = int(subcategory_id) if subcategory_id else None
    await state.update_data(
        subcategory_id=subcategory_id,
        product_id=product_id,
    )
    file_names = state_data.get('file_names', [])
    pending_dir = config.PENDING_DIR_PATH / str(message.from_user.id)
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
            destination_file=pending_dir / filename,
        )
    else:
        await message.answer('Invalid file')
        return

    file_names.append(filename)
    await state.update_data(file_names=file_names)
    await message.reply('File has been uploaded')


@dp.callback_query_handler(
    callback_factories.ProductCallbackFactory().filter(action='edit_price'),
    is_admin.IsUserAdmin()
)
async def edit_product_title(
        query: CallbackQuery,
        callback_data: dict[str, str],
):
    await EditProductResponse(query)
    await product_states.EditProductPrice.waiting_price.set()
    await dp.current_state().update_data(callback_data)


@dp.message_handler(
    is_admin.IsUserAdmin(),
    state=product_states.EditProductPrice,
)
async def edit_product_price(
        message: Message,
        state: dispatcher.FSMContext,
):
    if not message.text.replace('.', '').isdigit():
        await IncorrectPriceResponse(message)
        raise dispatcher.handler.CancelHandler
    state_data = await state.get_data()
    await state.finish()
    product_id, subcategory_id = (
        int(state_data['product_id']),
        state_data['subcategory_id'],
    )
    subcategory_id = int(subcategory_id) if subcategory_id != '' else None

    with database.create_session() as session:
        queries.edit_product_price(session, product_id, float(message.text))
        product = queries.get_product(session, product_id)
        await SuccessProductChangeResponse(message)
        await ProductResponse(
            message, category_id=int(state_data['category_id']),
            product=product, subcategory_id=subcategory_id
        )
