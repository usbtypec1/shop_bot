from collections.abc import Iterable
from uuid import UUID

from products.models import ProductMedia, MediaType

__all__ = (
    'file_extension_to_media_type',
    'parse_media_types',
)

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
