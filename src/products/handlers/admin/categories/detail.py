from aiogram import Dispatcher
from aiogram.types import CallbackQuery


async def on_show_category_detail(
        callback_query: CallbackQuery,
        callback_data: dict,
) -> None:
    pass


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_show_category_detail,
        state='*',
    )
