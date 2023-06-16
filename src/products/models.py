from dataclasses import dataclass
from typing import NewType

__all__ = (
    'Product',
    'MediaFileName',
)

MediaFileName = NewType('MediaFileName', str)


@dataclass(frozen=True, slots=True)
class Product:
    id: int
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

    @property
    def media_file_names(self) -> list[str]:
        return [] if self.picture is None else self.picture.split('|')

    @property
    def photo_and_video_file_names(self) -> list[str]:
        """Media file names (except GIFs) with relative order."""
        return [
            file_name for file_name in self.media_file_names
            if file_name.endswith('.jpg')
               or (
                       file_name.endswith('.mp4')
                       and not file_name.endswith('.gif.mp4')
               )
        ]

    @property
    def photo_file_names(self) -> list[str]:
        return [file_name for file_name in self.media_file_names
                if file_name.endswith('.jpg')]

    @property
    def video_file_names(self) -> list[str]:
        return [file_name for file_name in self.media_file_names
                if file_name.endswith('.mp4')
                and not file_name.endswith('.gif.mp4')]

    @property
    def animation_file_names(self) -> list[str] | None:
        return [file_name for file_name in self.media_file_names
                if file_name.endswith('.gif.mp4')]
