import contextlib
import pathlib
import shutil
from collections.abc import Iterable, Callable

import structlog
from aiogram.types import (
    MediaGroup,
    Message,
    InputMediaPhoto,
    InputMediaVideo,
    InputMedia,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)

from services.db_api.schemas import Product

logger = structlog.get_logger('app')


def build_file_paths(
        *,
        base_path: pathlib.Path,
        file_names: Iterable[str],
) -> list[pathlib.Path]:
    return [base_path / file_name for file_name in file_names]


async def answer_media_with_text(
        message: Message,
        base_path: pathlib.Path,
        product: Product,
        caption: str | None = None,
        reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None,
):
    file_path = base_path / product.picture
    if file_path.name.endswith('.gif.mp4'):
        answer = message.answer_animation
    else:
        file_extension_strategies = {
            '.jpg': message.answer_photo,
            '.mp4': message.answer_video,
        }
        answer = file_extension_strategies[file_path.suffix]
    with file_path.open(mode='rb') as file_io:
        await answer(file_io, caption=caption, reply_markup=reply_markup)


async def answer_medias(
        message: Message,
        base_path: pathlib.Path,
        product: Product,
):
    animation_file_paths = build_file_paths(
        base_path=base_path,
        file_names=product.animation_file_names,
    )
    for animation_file_path in animation_file_paths:
        with animation_file_path.open(mode='rb') as file_io:
            await message.answer_animation(file_io)

    photo_and_video_file_paths = build_file_paths(
        base_path=base_path,
        file_names=product.photo_and_video_file_names,
    )

    if photo_and_video_file_paths:

        with contextlib.ExitStack() as exit_stack:
            media_group = MediaGroup()
            for file_path in photo_and_video_file_paths:
                attach_to_media_group_and_exit_stack(
                    file_path=file_path,
                    media_group=media_group,
                    exit_stack=exit_stack,
                )
            await message.answer_media_group(media_group)


def attach_to_media_group_and_exit_stack(
        *,
        file_path: pathlib.Path,
        media_group: MediaGroup,
        exit_stack: contextlib.ExitStack,
) -> None:
    file_extension_strategies: (
        dict[str, tuple[type[InputMedia], Callable[[InputMedia], None]]]
    ) = {
        '.jpg': (InputMediaPhoto, media_group.attach_photo),
        '.mp4': (InputMediaVideo, media_group.attach_video),
    }
    try:
        input_media_type, attach_media = (
            file_extension_strategies[file_path.suffix]
        )
    except KeyError:
        raise ValueError(f'Invalid file extension: {file_path.suffix}')

    # ensure file IO will be closed
    file_io = exit_stack.enter_context(file_path.open(mode='rb'))

    attach_media(input_media_type(file_io))


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
