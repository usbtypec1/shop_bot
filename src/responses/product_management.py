from typing import Optional

import structlog
import aiogram
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
import keyboards.reply.product_management_keyboards
from keyboards.inline import product_management_keyboards
from keyboards.reply import shop_management_keyboards
from responses import base
from database import schemas
from services.files import answer_medias, answer_media_with_text

logger = structlog.get_logger('responses')


class ProductCategoriesResponse(base.BaseResponse):

    def __init__(self,
                 update: aiogram.types.Message | aiogram.types.CallbackQuery,
                 categories: list[schemas.Category]):
        self.__update = update
        self.__keyboard = product_management_keyboards.CategoriesKeyboard(
            categories)

    async def _send_response(self) -> aiogram.types.Message:
        message_text = '📝 Products Management'
        if isinstance(self.__update, aiogram.types.CallbackQuery):
            await self.__update.answer()
            if len(self.__update.message.photo) > 0:
                await self.__update.message.delete()
                return await self.__update.message.answer(message_text,
                                                          reply_markup=self.__keyboard)
            return await self.__update.message.edit_text(message_text,
                                                         reply_markup=self.__keyboard)
        elif isinstance(self.__update, aiogram.types.Message):
            return await self.__update.answer(message_text,
                                              reply_markup=self.__keyboard)


class CategoryItemsResponse(base.BaseResponse):
    def __init__(self, query: aiogram.types.CallbackQuery,
                 items: list[tuple[int, str, str]],
                 category_id: int):
        self.__query = query
        self.__keyboard = product_management_keyboards.CategoryItemsKeyboard(
            items, category_id)

    async def _send_response(self) -> aiogram.types.Message:
        message_text = (
            '📦 Available products and subcategories\n\n'
            '📝 To edit goods Click on it'
        )
        message = self.__query.message
        await self.__query.answer()
        if any((message.photo, message.video, message.animation)):
            await self.__query.message.delete()
            return await self.__query.message.answer(
                message_text, reply_markup=self.__keyboard
            )
        return await self.__query.message.edit_text(
            message_text,
            reply_markup=self.__keyboard
        )


class SubcategoryProductsResponse(base.BaseResponse):
    def __init__(self, query: aiogram.types.CallbackQuery, category_id: int,
                 subcategory_id: int, products: list[schemas.Product]):
        self.__query = query
        self.__keyboard = product_management_keyboards.SubcategoryProductsKeyboard(
            products, subcategory_id, category_id
        )

    async def _send_response(self) -> aiogram.types.Message:
        await self.__query.answer()
        message_text = (
            '📦 Available items\n\n'
            '📝 To edit goods Click on it'
        )
        if len(self.__query.message.photo) > 0:
            await self.__query.message.delete()
            return await self.__query.message.answer(
                message_text, reply_markup=self.__keyboard
            )
        return await self.__query.message.edit_text(
            message_text,
            reply_markup=self.__keyboard
        )


class AddProductNameResponse(base.BaseResponse):
    def __init__(self, query: aiogram.types.CallbackQuery):
        self.__query = query

    async def _send_response(self):
        await self.__query.answer()
        await self.__query.message.edit_text('📙 Enter the name of the product')


class AddProductDescriptionResponse(base.BaseResponse):
    def __init__(self, message: aiogram.types.Message):
        self.__message = message

    async def _send_response(self):
        await self.__message.answer('📋 Enter the product description')


class AddProductImageResponse(base.BaseResponse):
    def __init__(self, message: aiogram.types.Message):
        self.__message = message

    async def _send_response(self):
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Complete',
                        callback_data='complete-product-picture-uploading',
                    )
                ]
            ]
        )
        await self.__message.answer(
            '📷/📹/🎥 You can include multiple images and videos'
            ' for each product, but only one GIF file.'
            '\n\nPlease note that if you upload more than one photo or video,'
            ' the product buttons will not be inlined'
            ' (they won\'t be attached to the group of images or videos).'
            ' Also ensure that your videos are in MP4 format.'
            '\n\nIf you want to add multiple images and/or videos,'
            ' kindly press the "Complete" button once you have'
            ' finished sending all of them.'
            '\n\nYou must send media files one by one ❗️',
            reply_markup=markup,
        )


class AddProductPriceResponse(base.BaseResponse):
    def __init__(self, message: aiogram.types.Message):
        self.__message = message

    async def _send_response(self):
        await self.__message.answer('💵 Enter the price of goods in dollars')


class IncorrectPriceResponse(base.BaseResponse):
    def __init__(self, message: aiogram.types.Message):
        self.__message = message

    async def _send_response(self):
        await self.__message.answer('❗️ Enter the correct price ❗️')


class SuccessProductAddingResponse(base.BaseResponse):
    def __init__(self, message: aiogram.types.Message, product_name: str):
        self.__message = message
        self.__product_name = product_name

    async def _send_response(self):
        await self.__message.answer(f'✅ Product {self.__product_name} Created')


class AddProductUnitResponse(base.BaseResponse):
    def __init__(self,
                 update: aiogram.types.Message | aiogram.types.CallbackQuery):
        self.__update = update
        self.__keyboard = keyboards.reply.product_management_keyboards.CompleteProductAddingKeyboard()

    async def _send_response(self):
        message_text = (
            '📦 Enter the product data\n\n'
            'Examples of download:\n\n'
            'Product 1\n'
            'Product 2\n'
            'Product n\n\n'
            'Grouped Documents\n\n'
            'The products will be loaded until you click ✅ Complete'
        )
        if isinstance(self.__update, aiogram.types.CallbackQuery):
            await self.__update.answer()
            await self.__update.message.delete()
            await self.__update.message.answer(message_text,
                                               reply_markup=self.__keyboard)
        elif isinstance(self.__update, aiogram.types.Message):
            await self.__update.answer(message_text,
                                       reply_markup=self.__keyboard)


class SuccessUnitAddingResponse(base.BaseResponse):
    def __init__(self, message: aiogram.types.Message):
        self.__message = message

    async def _send_response(self):
        await self.__message.answer('✅ Goods loaded')


class CompleteUnitLoadingResponse(base.BaseResponse):
    def __init__(self, message: aiogram.types.Message, product_name: str):
        self.__message = message
        self.__product_name = product_name
        self.__keyboard = keyboards.reply.shop_management_keyboards.ShopManagementKeyboard()

    async def _send_response(self):
        await self.__message.answer(
            f'✅ loading {self.__product_name} Completed',
            reply_markup=self.__keyboard
        )


class ProductResponse(base.BaseResponse):

    def __init__(
            self,
            update: aiogram.types.CallbackQuery | aiogram.types.Message,
            product: schemas.Product,
            category_id: int,
            subcategory_id: int | None = None,
    ):
        self.__update = update
        self.__product = product
        self.__keyboard = product_management_keyboards.ProductKeyboard(
            category_id, product.id, subcategory_id=subcategory_id
        )

    async def _send_response(self):
        message_text = (
            f'📓 Name: {self.__product.name}\n\n'
            f'📋 Description:\n\n{self.__product.description}\n\n'
            f'💳 Price: ${self.__product.price:.2f}\n\n'
            f'📦 Available to purchase: {self.__product.quantity}'
            f' pc{"s" if self.__product.quantity > 1 else ""}\n\n'
        )
        logger.debug('Product edit', product=self.__product)
        if isinstance(self.__update, aiogram.types.CallbackQuery):
            message = self.__update.message
        else:
            message = self.__update
        if not self.__product.picture:
            await message.answer(
                text=message_text,
                reply_markup=self.__keyboard,
            )
        elif len(self.__product.media_file_names) == 1:
            await answer_media_with_text(
                message=message,
                base_path=config.PRODUCT_PICTURE_PATH,
                product=self.__product,
                caption=message_text,
                reply_markup=self.__keyboard
            )
        else:
            await answer_medias(
                message=message,
                base_path=config.PRODUCT_PICTURE_PATH,
                product=self.__product,
            )
            await message.answer(
                text=message_text,
                reply_markup=self.__keyboard
            )


# class EditProductResponse(base.BaseResponse):
#     def __init__(self, query: aiogram.types.CallbackQuery):
#         self.__query = query

#     async def _send_response(self) -> aiogram.types.Message:
#         message_text = '✏️ Enter a new value'
#         await self.__query.answer()
#         if len(self.__query.message.photo) > 0:
#             await self.__query.message.delete()
#             return await self.__query.message.answer('✏️ Enter a new value')
#         return await self.__query.message.edit_text(message_text)

class EditProductResponse(base.BaseResponse):
    def __init__(self, query: aiogram.types.CallbackQuery,
                 custom_message: Optional[str] = None,
                 custom_markup: InlineKeyboardMarkup | None = None):
        self.__query = query
        self.custom_message = custom_message
        self.custom_markup = custom_markup

    async def _send_response(self) -> aiogram.types.Message:
        message = self.__query.message
        message_text = self.custom_message or '✏️ Enter a new value'
        await self.__query.answer()
        if any((message.photo, message.video, message.animation)):
            await self.__query.message.delete()
            return await message.answer(message_text,
                                        reply_markup=self.custom_markup)
        return await message.edit_text(message_text,
                                       reply_markup=self.custom_markup)


class SuccessRemovalProductResponse(base.BaseResponse):
    def __init__(self, query: aiogram.types.CallbackQuery):
        self.__query = query

    async def _send_response(self) -> aiogram.types.Message:
        await self.__query.answer()
        return await self.__query.message.edit_text('✅ Product(s) Removed')


class SuccessProductChangeResponse(base.BaseResponse):
    def __init__(self, message: aiogram.types.Message):
        self.__message = message

    async def _send_response(self):
        await self.__message.answer('✅ Changes Saved')


class ProductUnitsResponse(base.BaseResponse):
    def __init__(self,
                 update: aiogram.types.CallbackQuery | aiogram.types.Message,
                 category_id: int, product_id: int,
                 product_units: list[schemas.ProductUnit],
                 subcategory_id: int = None):
        self.__update = update
        self.__keyboard = product_management_keyboards.ProductUnitsKeyboard(
            category_id, product_id, product_units, subcategory_id
        )

    async def _send_response(self) -> aiogram.types.Message:
        message_text = '📦 All available data'
        if isinstance(self.__update, aiogram.types.CallbackQuery):
            await self.__update.answer()
            await self.__update.message.delete()
            return await self.__update.message.answer(message_text,
                                                      reply_markup=self.__keyboard)
        elif isinstance(self.__update, aiogram.types.Message):
            return await self.__update.answer(message_text,
                                              reply_markup=self.__keyboard)


class ProductUnitResponse(base.BaseResponse):
    def __init__(self,
                 update: aiogram.types.CallbackQuery | aiogram.types.Message,
                 product_id: int, product_unit: schemas.ProductUnit,
                 category_id: int, subcategory_id: int = None):
        self.__update = update
        self.__unit = product_unit
        self.__keyboard = product_management_keyboards.ProductUnitKeyboard(
            category_id, product_id, self.__unit.id, subcategory_id
        )

    async def _send_response(self):
        text = self.get_text()
        if isinstance(self.__update, aiogram.types.CallbackQuery):
            await self.__update.answer()
            if self.__unit.type == 'text':
                await self.__update.message.edit_text(
                    text, reply_markup=self.__keyboard
                )
            if self.__unit.type == 'document':
                await self.__update.message.delete()
                await self.__update.message.answer_document(
                    aiogram.types.InputFile(
                        config.PRODUCT_UNITS_PATH / self.__unit.content),
                    caption=text,
                    reply_markup=self.__keyboard
                )
        elif isinstance(self.__update, aiogram.types.Message):
            if self.__unit.type == 'text':
                await self.__update.answer(text, reply_markup=self.__keyboard)
            if self.__unit.type == 'document':
                await self.__update.answer_document(
                    aiogram.types.InputFile(
                        config.PRODUCT_UNITS_PATH / self.__unit.content),
                    caption=text, reply_markup=self.__keyboard
                )

    def get_text(self) -> str:
        if self.__unit.type == 'text':
            return (
                f'📋 Product Type: Text\n'
                f'📦 Data:\n\n{self.__unit.content}'
            )
        elif self.__unit.type == 'document':
            return f'📋 Product Type: Document\n'
        return ''


class EditProductUnitsResponse(base.BaseResponse):
    def __init__(self, query: aiogram.types.CallbackQuery):
        self.__query = query

    async def _send_response(self):
        await self.__query.answer()
        await self.__query.message.edit_text(
            '📝 Enter the new product data, or Load file.')


class SuccessRemovalUnitResponse(base.BaseResponse):
    def __init__(self, query: aiogram.types.CallbackQuery):
        self.__query = query

    async def _send_response(self) -> aiogram.types.Message:
        await self.__query.answer()
        return await self.__query.message.answer('✅ Position removed')
