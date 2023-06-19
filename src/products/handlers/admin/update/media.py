import pathlib
from uuid import uuid4

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, Message, ContentType

import config
from common.filters import AdminFilter
from common.views import edit_message_by_view, answer_view
from products.callback_data import AdminProductUpdateCallbackData
from products.repositories import ProductRepository
from products.services import parse_media_types, batch_move_files
from products.states import ProductUpdateStates
from products.views import AdminAskForProductMediaView, AdminProductDetailView

__all__ = ('register_handlers',)


async def on_start_product_media_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    product_id: int = callback_data['product_id']
    await ProductUpdateStates.media.set()
    await state.update_data(product_id=product_id)
    view = AdminAskForProductMediaView()
    await edit_message_by_view(message=callback_query.message, view=view)


async def on_media_file_upload(
        message: Message,
        state: FSMContext,
) -> None:
    if message.photo:
        file = message.photo[-1]
        filename = f'{uuid4()}.jpg'
    elif message.video:
        file = message.video
        filename = f'{uuid4()}.mp4'
    elif message.animation:
        file = message.animation
        filename = f'{uuid4()}.gif.mp4'
    else:
        raise ValueError('Invalid media type')

    file_path = pathlib.Path.joinpath(
        config.PENDING_DIR_PATH,
        str(message.from_user.id),
        filename,
    )
    await file.download(destination_file=file_path)
    state_data = await state.get_data()
    media: set[str] = state_data.get('media', set())
    media.add(filename)
    await state.update_data(media=media)
    await message.reply('File has been uploaded')


async def on_media_upload_finish(
        callback_query: CallbackQuery,
        state: FSMContext,
        product_repository: ProductRepository,
) -> None:
    state_data = await state.get_data()
    await state.finish()
    product_id: int = state_data['product_id']
    media: set[str] = state_data.get('media', set())
    product_repository.update_media(
        product_id=product_id,
        media=parse_media_types(media),
    )
    batch_move_files(
        base_path=config.PENDING_DIR_PATH / str(callback_query.from_user.id),
        file_names=media,
        destination_path=config.PRODUCT_PICTURE_PATH,
    )
    product = product_repository.get_by_id(product_id)
    view = AdminProductDetailView(product)
    await answer_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_start_product_media_update_flow,
        AdminFilter(),
        AdminProductUpdateCallbackData().filter(field='media'),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        on_media_upload_finish,
        AdminFilter(),
        Text('complete-product-picture-uploading'),
        state=ProductUpdateStates.media,
    )
    dispatcher.register_message_handler(
        on_media_file_upload,
        AdminFilter(),
        content_types=(
            ContentType.PHOTO,
            ContentType.VIDEO,
            ContentType.ANIMATION,
        ),
        state=ProductUpdateStates.media,
    )
