import pathlib
from decimal import Decimal
from uuid import uuid4

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import (
    CallbackQuery, Message, ContentType,
    InlineKeyboardMarkup, InlineKeyboardButton
)

import config
from common.filters import AdminFilter
from common.views import answer_view, edit_message_by_view
from products.callback_data import (
    AdminProductCreateCallbackData,
    AdminProductPermittedGatewayChoiceCallbackData
)
from products.models import PaymentMethod
from products.repositories import ProductRepository
from products.services import parse_media_types
from products.states import ProductCreateStates
from products.views import (
    AdminAskForProductMediaView,
    AdminProductPermittedGatewaysView
)


async def on_start_product_creation_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    category_id = callback_data['category_id']
    await ProductCreateStates.name.set()
    await state.update_data(category_id=category_id)
    await callback_query.message.edit_text('📙 Enter the name of the product')


async def on_product_name_input(
        message: Message,
        state: FSMContext,
) -> None:
    await state.update_data(name=message.text)
    await ProductCreateStates.description.set()
    await message.answer('📋 Enter the product description')


async def on_product_description_input(
        message: Message,
        state: FSMContext,
) -> None:
    await state.update_data(description=message.text)
    await ProductCreateStates.media.set()
    view = AdminAskForProductMediaView()
    await answer_view(message=message, view=view)


async def on_complete_product_picture_uploading(
        callback_query: CallbackQuery,
        state: FSMContext,
) -> None:
    await ProductCreateStates.price.set()
    await callback_query.message.answer(
        '💵 Enter the price of goods in dollars'
    )


async def on_product_picture_upload(
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
        await ProductCreateStates.price.set()
        await message.answer('💵 Enter the price of goods in dollars')
        return

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


async def on_product_price_input(
        message: Message,
        state: FSMContext,
) -> None:
    try:
        price = Decimal(message.text)
    except ValueError:
        await message.answer('❌ Invalid price!')
        return
    await state.update_data(price=price)
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Yes',
                    callback_data='product-settings-specify',
                ),
                InlineKeyboardButton(
                    text='No',
                    callback_data='product-create-finish',
                ),
            ],
        ],
    )
    await message.answer(
        text='Do you want to specific advanced settings?',
        reply_markup=markup,
    )


async def on_ask_for_advanced_settings(
        callback_query: CallbackQuery,
        state: FSMContext,
) -> None:
    await ProductCreateStates.min_order_quantity.set()
    await callback_query.message.answer('Enter Minimum Order quantity')


async def on_product_minimum_order_quantity_input(
        message: Message,
        state: FSMContext,
) -> None:
    try:
        min_order_quantity = int(message.text)
    except ValueError:
        await message.answer(
            '❌ Invalid minimum order quantity (must be a number)!'
        )
        return
    await ProductCreateStates.max_order_quantity.set()
    await state.update_data(min_order_quantity=min_order_quantity)
    await message.answer(
        'Enter the Maximum Order quantity'
        ' (Enter 1 for infinite number, no limitations)'
    )


async def on_product_maximum_order_quantity_input(
        message: Message,
        state: FSMContext,
) -> None:
    try:
        max_order_quantity = int(message.text)
    except ValueError:
        await message.answer(
            '❌ Invalid maximum order quantity (must be a number)!'
        )
        return
    await ProductCreateStates.max_replacement_time_in_minutes.set()
    await state.update_data(max_order_quantity=max_order_quantity)
    await message.answer(
        'Enter the Maximum Replacement Time allowed in minutes:'
        ' (default minutes is 15, enter any text A-Z to set to default time)'
    )


async def on_maximum_replacement_time_input(
        message: Message,
        state: FSMContext,
) -> None:
    try:
        max_replacement_time_in_minutes = int(message.text)
    except ValueError:
        await message.answer(
            '❌ Invalid maximum replacement time (must be a number)!'
        )
        return
    await ProductCreateStates.max_displayed_stock.set()
    await state.update_data(
        max_replacement_time_in_minutes=max_replacement_time_in_minutes,
    )
    await message.answer(
        'Max Displayed Stock: (Choose 1 to show "In Stock"'
        ' instead of the exact quantity of this product)'
    )


async def on_maximum_displayed_stock_input(
        message: Message,
        state: FSMContext,
) -> None:
    try:
        max_displayed_stock = int(message.text)
    except ValueError:
        await message.answer(
            '❌ Invalid maximum displayed stock (must be a number)!'
        )
        return
    if max_displayed_stock == 1:
        max_displayed_stock = None
    await ProductCreateStates.is_duplicated_stock_entries_allowed.set()
    await state.update_data(max_displayed_stock=max_displayed_stock)
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Yes',
                    callback_data='product-duplicated-stock-entries-prevented',
                ),
                InlineKeyboardButton(
                    text='No',
                    callback_data='product-duplicated-stock-entries-allowed',
                )
            ]
        ]
    )
    await message.answer(
        'Do you want to Prevent Duplicate Stock Entries?',
        reply_markup=markup
    )


async def on_prevent_duplicate_stock_entries_status_choice(
        callback_query: CallbackQuery,
        state: FSMContext,
) -> None:
    is_duplicated_stock_entries_allowed = (
            'product-duplicated-stock-entries-allowed' == callback_query.data
    )
    await ProductCreateStates.is_hidden.set()
    await state.update_data(
        is_duplicated_stock_entries_allowed=is_duplicated_stock_entries_allowed,
    )
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Yes',
                    callback_data='product-hidden',
                ),
                InlineKeyboardButton(
                    text='No',
                    callback_data='product-not-hidden',
                )
            ]
        ]
    )
    await callback_query.message.answer(
        text='Hide product from Shop?',
        reply_markup=markup,
    )


async def on_permitted_gateways_choice(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    state_data = await state.get_data()
    permitted_gateways: set[PaymentMethod] = state_data.get(
        'permitted_gateways',
        set(),
    )
    payment_method = callback_data['payment_method']
    if payment_method in permitted_gateways:
        permitted_gateways.remove(payment_method)
    else:
        permitted_gateways.add(payment_method)
    await state.update_data(permitted_gateways=permitted_gateways)
    view = AdminProductPermittedGatewaysView(
        payment_method=PaymentMethod,
        chosen_payment_methods=permitted_gateways,
    )
    await edit_message_by_view(message=callback_query.message, view=view)


async def on_hidden_status_choice(
        callback_query: CallbackQuery,
        state: FSMContext,
) -> None:
    is_hidden = 'product-hidden' == callback_query.data
    await ProductCreateStates.can_be_purchased.set()
    await state.update_data(is_hidden=is_hidden)
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Yes',
                    callback_data='product-can-not-be-purchased',
                ),
                InlineKeyboardButton(
                    text='No',
                    callback_data='product-can-be-purchased',
                )
            ]
        ]
    )
    await callback_query.message.answer(
        'Prevent Users from purchasing this product?',
        reply_markup=markup,
    )


async def on_can_be_purchased_status_choice(
        callback_query: CallbackQuery,
        state: FSMContext,
) -> None:
    can_be_purchased = callback_query.data == 'product-can-be-purchased'
    await ProductCreateStates.permitted_gateways.set()
    await state.update_data(can_be_purchased=can_be_purchased)
    view = AdminProductPermittedGatewaysView(
        payment_method=PaymentMethod,
    )
    await answer_view(message=callback_query.message, view=view)


async def on_product_create_finish(
        callback_query: CallbackQuery,
        state: FSMContext,
        product_repository: ProductRepository,
) -> None:
    state_data = await state.get_data()
    await state.finish()

    name: str = state_data['name']
    description: str = state_data['description']
    media: set[str] = state_data.get('media', set())
    price: Decimal = state_data['price']
    category_id: int = state_data['category_id']

    product = product_repository.create(
        name=name,
        description=description,
        media=parse_media_types(media),
        price=price,
        category_id=category_id,
    )
    print(product)


async def on_product_advanced_settings_create_finish(
        callback_query: CallbackQuery,
        state: FSMContext,
        product_repository: ProductRepository,
) -> None:
    state_data = await state.get_data()
    await state.finish()

    category_id: int = state_data['category_id']
    name: str = state_data['name']
    description: str = state_data['description']
    media: set[str] = state_data.get('media', set())
    price: Decimal = state_data['price']
    min_order_quantity: int = state_data['min_order_quantity']
    max_order_quantity: int = state_data['max_order_quantity']
    max_replacement_time_in_minutes: int = state_data[
        'max_replacement_time_in_minutes']
    max_displayed_stock_count: int | None = state_data['max_displayed_stock']
    is_duplicated_stock_entries_allowed: bool = state_data[
        'is_duplicated_stock_entries_allowed']
    is_hidden: bool = state_data['is_hidden']
    can_be_purchased: bool = state_data['can_be_purchased']
    permitted_gateways: set[PaymentMethod] = state_data.get(
        'permitted_gateways',
        set()
    )

    product = product_repository.create(
        name=name,
        description=description,
        media=parse_media_types(media),
        price=price,
        category_id=category_id,
        min_order_quantity=min_order_quantity,
        max_order_quantity=max_order_quantity,
        max_replacement_time_in_minutes=max_replacement_time_in_minutes,
        max_displayed_stock_count=max_displayed_stock_count,
        is_duplicated_stock_entries_allowed=is_duplicated_stock_entries_allowed,
        is_hidden=is_hidden,
        can_be_purchased=can_be_purchased,
        permitted_gateways=permitted_gateways,
    )
    print(product)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_start_product_creation_flow,
        AdminProductCreateCallbackData().filter(),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_message_handler(
        on_product_name_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        state=ProductCreateStates.name,
    )
    dispatcher.register_message_handler(
        on_product_description_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        state=ProductCreateStates.description,
    )
    dispatcher.register_callback_query_handler(
        on_complete_product_picture_uploading,
        Text('complete-product-picture-uploading'),
        AdminFilter(),
        state=ProductCreateStates.media,
    )
    dispatcher.register_message_handler(
        on_product_picture_upload,
        AdminFilter(),
        content_types=(
            ContentType.TEXT,
            ContentType.PHOTO,
            ContentType.VIDEO,
            ContentType.ANIMATION,
        ),
        state=ProductCreateStates.media,
    )
    dispatcher.register_message_handler(
        on_product_price_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        state=ProductCreateStates.price,
    )
    dispatcher.register_callback_query_handler(
        on_ask_for_advanced_settings,
        Text('product-settings-specify'),
        AdminFilter(),
        state=ProductCreateStates.price,
    )
    dispatcher.register_message_handler(
        on_product_minimum_order_quantity_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        state=ProductCreateStates.min_order_quantity,
    )
    dispatcher.register_message_handler(
        on_product_maximum_order_quantity_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        state=ProductCreateStates.max_order_quantity,
    )
    dispatcher.register_message_handler(
        on_maximum_replacement_time_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        state=ProductCreateStates.max_replacement_time_in_minutes,
    )
    dispatcher.register_message_handler(
        on_maximum_displayed_stock_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        state=ProductCreateStates.max_displayed_stock,
    )
    dispatcher.register_callback_query_handler(
        on_prevent_duplicate_stock_entries_status_choice,
        AdminFilter(),
        state=ProductCreateStates.is_duplicated_stock_entries_allowed,
    )
    dispatcher.register_callback_query_handler(
        on_hidden_status_choice,
        AdminFilter(),
        state=ProductCreateStates.is_hidden,
    )
    dispatcher.register_callback_query_handler(
        on_can_be_purchased_status_choice,
        AdminFilter(),
        state=ProductCreateStates.can_be_purchased,
    )
    dispatcher.register_callback_query_handler(
        on_permitted_gateways_choice,
        AdminFilter(),
        AdminProductPermittedGatewayChoiceCallbackData().filter(),
        state=ProductCreateStates.permitted_gateways,
    )
    dispatcher.register_callback_query_handler(
        on_product_create_finish,
        Text('permitted-gateways-choose-finish'),
        AdminFilter(),
        state=ProductCreateStates.price,
    )
    dispatcher.register_callback_query_handler(
        on_product_advanced_settings_create_finish,
        Text('permitted-gateways-choose-finish'),
        AdminFilter(),
        state=ProductCreateStates.permitted_gateways,
    )
