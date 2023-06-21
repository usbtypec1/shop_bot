from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from database.schemas.products import PaymentMethod, MediaType

__all__ = (
    'Product',
    'MediaFileName',
    'PaymentMethod',
    'MediaType',
    'ProductMedia',
)

MediaFileName = NewType('MediaFileName', str)


@dataclass(frozen=True, slots=True)
class ProductMedia:
    uuid: UUID
    type: MediaType

    @property
    def file_name(self) -> str:
        media_type_to_file_extension = {
            MediaType.PHOTO: 'jpg',
            MediaType.VIDEO: 'mp4',
            MediaType.ANIMATION: 'gif.mp4'
        }
        file_extension = media_type_to_file_extension[self.type]
        return f'{str(self.uuid)}.{file_extension}'


@dataclass(frozen=True, slots=True)
class Product:
    id: int
    category_id: int
    name: str
    description: str
    price: float
    quantity: int
    min_order_quantity: int | None
    max_order_quantity: int | None
    max_replacement_time_in_minutes: int
    max_displayed_stock_count: int | None
    is_duplicated_stock_entries_allowed: bool
    is_hidden: bool
    can_be_purchased: bool
    media: list[ProductMedia]
    permitted_gateways: list[PaymentMethod]

    @property
    def photos_and_videos(self) -> list[ProductMedia]:
        return [
            media for media in self.media
            if media.type in (MediaType.PHOTO, MediaType.VIDEO)
        ]

    @property
    def animations(self) -> list[ProductMedia]:
        return [
            media for media in self.media
            if media.type == MediaType.ANIMATION
        ]
