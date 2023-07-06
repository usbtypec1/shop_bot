from aiogram import Dispatcher

__all__ = ('register_handlers',)

from aiogram.dispatcher import FSMContext

from aiogram.types import CallbackQuery


async def on_(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    pass



def register_handlers(dispatcher: Dispatcher) -> None:
    # dispatcher.register_callback_query_handler()
    pass
