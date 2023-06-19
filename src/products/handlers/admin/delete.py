# @dp.callback_query_handler(
#     products.callback_data.ProductCallbackFactory().filter(action='delete_units'),
#     AdminFilter(),
# )
# async def delete_product_units(
#         callback_query: CallbackQuery,
#         callback_data: dict[str, str],
# ) -> None:
#     category_id: int = int(callback_data['category_id'])
#     subcategory_id: int = int(callback_data['subcategory_id'])
#     category_id = int(category_id) if category_id else None
#     subcategory_id = int(subcategory_id) if subcategory_id else None
#
#     product_id = int(callback_data['product_id'])
#     with database.create_session() as session:
#         product_life_cycle = product_services.ProductLifeCycle(
#             product_id=product_id).load_from_db(session).delete_product_units(session)
#         product = queries.get_product(session, product_id)
#         await responses.product_management.ProductResponse(
#             callback_query, product, category_id, subcategory_id
#         )
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import (
    CallbackQuery, InlineKeyboardMarkup,
    InlineKeyboardButton
)

from common.filters import AdminFilter
from products.callback_data import AdminProductDeleteCallbackData
from products.repositories import ProductRepository
from products.states import ProductDeleteStates


async def on_ask_product_delete_confirmation(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    product_id: int = callback_data['product_id']
    await ProductDeleteStates.confirm.set()
    await state.update_data(product_id=product_id)
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='❌ Delete',
                    callback_data='delete-confirm'
                ),
                InlineKeyboardButton(
                    text='⬅️ Back',
                    callback_data='delete-reject',
                ),
            ],
        ],
    )
    await callback_query.message.edit_text(
        text='❗️ Are you sure you want to delete this product?',
        reply_markup=markup,
    )


async def on_product_delete_confirm(
        callback_query: CallbackQuery,
        state: FSMContext,
        product_repository: ProductRepository,
) -> None:
    state_data = await state.get_data()
    await state.finish()
    product_id: int = state_data['product_id']
    product_repository.delete_by_id(product_id)
    await callback_query.answer('❗️ Product has been deleted', show_alert=True)
    await callback_query.message.delete()


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_ask_product_delete_confirmation,
        AdminFilter(),
        AdminProductDeleteCallbackData().filter(),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        on_product_delete_confirm,
        AdminFilter(),
        Text('delete-confirm'),
        state=ProductDeleteStates.confirm,
    )
