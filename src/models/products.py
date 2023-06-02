from dataclasses import dataclass
from typing import NewType

__all__ = (
    'Product',
    'MediaFileName',
)

MediaFileName = NewType('MediaFileName', str)


@dataclass(frozen=True, slots=True)
class Product:
    category_id: int
    subcategory_id: int
    name: str
    description: str
    picture: str
    price: float
    quantity: int
    min_order_quantity: int
    max_order_quantity: int
    max_replacement_time_in_minutes: int
    max_displayed_stock_count: int
    is_duplicated_stock_entries_allowed: bool
    is_hidden: bool
    can_be_purchased: bool
    media_file_names: list[MediaFileName]
    photo_and_video_file_names: list[MediaFileName]
    photo_file_names: list[MediaFileName]
    video_file_names: list[MediaFileName]
    animation_file_names: list[MediaFileName]
