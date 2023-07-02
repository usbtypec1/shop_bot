import contextlib
import pathlib
import shutil
from collections.abc import Iterable
from uuid import UUID

import structlog
from aiogram.types import (
    MediaGroup,
    Message,
    InputMediaPhoto,
    InputMediaVideo,
    InputMedia,
)
from aiogram.utils.exceptions import TelegramAPIError

from common.views import View, answer_view
from products.exceptions import ProductQuantityValidationError
from products.models import Product, ProductMedia, MediaType

__all__ = (
    'batch_move_files',
    'answer_view_with_media',
    'file_extension_to_media_type',
    'parse_media_types',
    'parse_product_quantity',
)

logger: structlog.stdlib.BoundLogger = structlog.get_logger('app')


def build_file_paths(
        *,
        base_path: pathlib.Path,
        file_names: Iterable[str],
) -> list[pathlib.Path]:
    return [base_path / file_name for file_name in file_names]


async def answer_view_with_media(
        *,
        message: Message,
        base_path: pathlib.Path,
        product: Product,
        view: View,
) -> Message:
    if len(product.media) > 10:
        raise ValueError('Too many media files (10 maximum)')

    for animation in product.animations:
        file_path = base_path / animation.file_name
        try:
            with file_path.open('rb') as file_io:
                await message.answer_animation(file_io)
        except OSError:
            logger.error('File does not exist', file_path=file_path)
        except TelegramAPIError:
            logger.exception(
                'Could not send mediafile',
                media_type=animation.type.name,
            )

    media_type_to_input_media = {
        MediaType.PHOTO: InputMediaPhoto,
        MediaType.VIDEO: InputMediaVideo,
    }

    with contextlib.ExitStack() as exit_stack:
        input_medias: list[InputMedia] = []
        for photo_or_video in product.photos_and_videos:

            file_path = base_path / photo_or_video.file_name
            try:
                file_io = exit_stack.enter_context(file_path.open('rb'))
            except FileNotFoundError:
                logger.error('File does not exist', file_path=file_path)
                continue

            input_media = media_type_to_input_media[photo_or_video.type]
            input_medias.append(input_media(file_io))

        if input_medias:
            media_group = MediaGroup(input_medias)

            try:
                await message.answer_media_group(media_group)
            except TelegramAPIError:
                logger.error('Could not send media group')

    return await answer_view(message=message, view=view)


def batch_move_files(
        *,
        base_path: pathlib.Path,
        file_names: Iterable[str],
        destination_path: pathlib.Path,
):
    """Moves batch of files from a source directory to a destination directory.

    Args:
        base_path (pathlib.Path): The directory containing files to be moved.
        file_names (Iterable[str]): An iterable of file names to be moved.
        destination_path (pathlib.Path): The directory to move the files to.
    """
    file_paths = build_file_paths(
        base_path=base_path,
        file_names=file_names,
    )
    for file_path in file_paths:
        shutil.move(file_path, destination_path)
        logger.info(
            'File has been moved',
            file_path=file_path,
            destination=destination_path,
        )


def batch_delete_files(
        *,
        base_path: pathlib.Path,
        file_names: Iterable[str],
) -> None:
    """Deletes a list of media files from the specified directory.

    Args:
        base_path (pathlib.Path): The directory containing the media files.
        file_names (Iterable[str]): An iterable of file names to be deleted.
    """
    file_paths = build_file_paths(
        base_path=base_path,
        file_names=file_names,
    )

    for file_path in file_paths:
        file_path.unlink(missing_ok=True)
        logger.info('File has been deleted', file_path=file_path)


file_extension_to_media_type: dict[str, MediaType] = {
    'jpg': MediaType.PHOTO,
    'gif.mp4': MediaType.ANIMATION,
    'mp4': MediaType.VIDEO,
}


def parse_media_types(media: Iterable[str]) -> list[ProductMedia]:
    product_media: list[ProductMedia] = []
    for media_file_name in media:

        file_name, *file_extension = media_file_name.split('.')
        file_extension = '.'.join(file_extension)
        product_media.append(
            ProductMedia(
                uuid=UUID(file_name),
                type=file_extension_to_media_type[file_extension],
            )
        )

    return product_media


def parse_product_quantity(quantity: str) -> int:
    if not quantity.isdigit():
        raise ProductQuantityValidationError(
            '❌ Number of pieces must be a <b><u>number</u></b>'
        )
    if (quantity := int(quantity)) <= 0:
        raise ProductQuantityValidationError(
            '❌ Number of pieces must be greater than 0'
        )
    return quantity
